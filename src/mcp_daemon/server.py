import os
import json
import signal
import asyncio
from typing import Dict, Optional, Any
from contextlib import AsyncExitStack
from loguru import logger

from mcp import ClientSession
from config import mcp_service

from .models import ServerSession, SessionState
from .handlers import RequestHandler
from .sse import SSEManager
from .stdio import StdioManager
from .streamable_http import StreamableHTTPManager

class MCPDaemonServer:
    """
    Daemon server that maintains persistent connections to MCP servers and
    provides an IPC interface for chat sessions to interact with them.
    """
    def __init__(self, socket_path: str, log_file: Optional[str] = None):
        self.socket_path = socket_path
        self.sessions: Dict[str, ServerSession] = {}
        self.server = None
        self.exit_stack = AsyncExitStack()
        self.running = False

        # Set up logging
        if log_file:
            logger.add(log_file, rotation="10 MB")

        # Initialize managers
        self.sse_manager = SSEManager(self.exit_stack)
        self.stdio_manager = StdioManager(self.exit_stack)
        self.streamable_http_manager = StreamableHTTPManager(self.exit_stack)
        self.request_handler = RequestHandler(self.sessions)

    def get_session_status(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a server session.

        Args:
            server_name: Name of the server

        Returns:
            Dict with session status info or None if session doesn't exist
        """
        session = self.sessions.get(server_name)
        if not session:
            return None

        return {
            "name": server_name,
            "transport_type": session.transport_type,
            "state": session.state.value,
            "session_id": session.session_id,
            "endpoint_url": session.endpoint_url,
            "is_active": session.state == SessionState.ACTIVE
        }

    async def reconnect_server(self, server_name: str) -> bool:
        """
        Attempt to reconnect to a server.

        Args:
            server_name: Name of the server to reconnect

        Returns:
            True if reconnection successful, False otherwise
        """
        # Get server config
        config = mcp_service.get_config(server_name)
        if not config:
            logger.error(f"No configuration found for server '{server_name}'")
            return False

        # Remove old session
        if server_name in self.sessions:
            old_session = self.sessions[server_name]
            logger.info(f"Removing disconnected session for '{server_name}' (transport: {old_session.transport_type})")
            del self.sessions[server_name]

        # Reconnect based on transport type
        if config.url:
            logger.info(f"Reconnecting to HTTP server '{server_name}'")
            transport_type = config.transport_type or 'auto'

            if transport_type == 'streamable-http':
                session = await self.streamable_http_manager.connect(
                    config.name,
                    config.url,
                    config.token,
                    config.custom_headers if config.custom_headers else None,
                    config.timeout
                )
            elif transport_type == 'legacy-sse':
                session = await self.sse_manager.connect(
                    config.name,
                    config.url,
                    config.token
                )
            else:  # auto-detect
                session = await self.streamable_http_manager.connect(
                    config.name,
                    config.url,
                    config.token,
                    config.custom_headers if config.custom_headers else None,
                    config.timeout
                )
                if not session:
                    session = await self.sse_manager.connect(
                        config.name,
                        config.url,
                        config.token
                    )

            if session:
                self.sessions[server_name] = session
                logger.info(f"Reconnected to '{server_name}' using {session.transport_type}")
                return True
        else:
            # stdio server
            logger.info(f"Reconnecting to stdio server '{server_name}'")
            session = await self.stdio_manager.connect(
                config.name,
                config.command,
                config.args,
                config.env
            )
            if session:
                self.sessions[server_name] = session
                logger.info(f"Reconnected to stdio server '{server_name}'")
                return True

        logger.error(f"Failed to reconnect to server '{server_name}'")
        return False
        
    async def connect_to_all_servers(self):
        """Connect to all configured MCP servers with automatic transport detection"""
        server_configs = mcp_service.get_all_configs()

        for config in server_configs:
            # Determine transport based on config
            transport_type = config.transport_type or 'auto'

            if config.url:  # HTTP-based server (Streamable HTTP or legacy SSE)
                logger.info(f"Connecting to HTTP server '{config.name}' at {config.url} (transport: {transport_type})")

                # Handle manual transport override
                if transport_type == 'stdio':
                    logger.warning(f"Config specifies stdio transport but URL is provided for '{config.name}'")
                    continue

                if transport_type == 'legacy-sse':
                    # Explicitly use legacy SSE
                    logger.debug(f"Using legacy SSE as configured for '{config.name}'")
                    session = await self.sse_manager.connect(
                        config.name,
                        config.url,
                        config.token
                    )
                    if session:
                        session.transport_type = 'legacy-sse'
                        self.sessions[config.name] = session
                    else:
                        logger.error(f"Failed to connect to '{config.name}' using legacy SSE")

                elif transport_type == 'streamable-http':
                    # Explicitly use Streamable HTTP
                    logger.debug(f"Using Streamable HTTP as configured for '{config.name}'")
                    session = await self.streamable_http_manager.connect(
                        config.name,
                        config.url,
                        config.token,
                        config.custom_headers if config.custom_headers else None,
                        config.timeout
                    )
                    if session:
                        self.sessions[config.name] = session
                    else:
                        logger.error(f"Failed to connect to '{config.name}' using Streamable HTTP")

                else:  # 'auto' or unspecified - auto-detect
                    # Try Streamable HTTP first (modern transport)
                    logger.debug(f"Auto-detecting transport for '{config.name}'")
                    session = await self.streamable_http_manager.connect(
                        config.name,
                        config.url,
                        config.token,
                        config.custom_headers if config.custom_headers else None,
                        config.timeout
                    )

                    if session:
                        logger.info(f"Connected to '{config.name}' using Streamable HTTP")
                        self.sessions[config.name] = session
                        # Cache detected transport type
                        if not config.transport_type:
                            config.transport_type = 'streamable-http'
                            mcp_service.update_config(config)
                            logger.debug(f"Cached transport type 'streamable-http' for '{config.name}'")
                    else:
                        # Fallback to legacy SSE if Streamable HTTP fails
                        logger.debug(f"Streamable HTTP failed for '{config.name}', trying legacy SSE")
                        session = await self.sse_manager.connect(
                            config.name,
                            config.url,
                            config.token
                        )
                        if session:
                            logger.warning(f"Connected to '{config.name}' using legacy HTTP+SSE (deprecated)")
                            session.transport_type = 'legacy-sse'
                            self.sessions[config.name] = session
                            # Cache detected transport type
                            if not config.transport_type:
                                config.transport_type = 'legacy-sse'
                                mcp_service.update_config(config)
                                logger.debug(f"Cached transport type 'legacy-sse' for '{config.name}'")
                        else:
                            logger.error(f"Failed to connect to server '{config.name}' - no compatible transport")

            else:  # stdio server
                logger.info(f"Connecting to stdio server '{config.name}'")
                session = await self.stdio_manager.connect(
                    config.name,
                    config.command,
                    config.args,
                    config.env
                )
                if session:
                    self.sessions[config.name] = session

            await asyncio.sleep(1)  # Delay to avoid overwhelming the system

    async def handle_client(self, reader, writer):
        """Handle client connections and process requests"""
        addr = writer.get_extra_info('peername')
        logger.info(f"Client connected: {addr}")
        
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                
                message = data.decode().strip()
                response = await self.request_handler.handle_request(message)
                
                writer.write(json.dumps(response).encode() + b'\n')
                await writer.drain()
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"Client disconnected: {addr}")
            
    async def start_server(self):
        """Start the IPC server"""
        try:
            # Remove socket file if it exists
            if os.path.exists(self.socket_path):
                os.unlink(self.socket_path)
                
            # Start server
            self.server = await asyncio.start_unix_server(
                self.handle_client, 
                self.socket_path
            )
            
            # Set socket permissions
            os.chmod(self.socket_path, 0o777)
            
            # Enter server context
            async with self.server:
                logger.info(f"MCP daemon server started at {self.socket_path}")
                self.running = True
                
                # Set up signal handlers
                for sig in (signal.SIGINT, signal.SIGTERM):
                    asyncio.get_event_loop().add_signal_handler(
                        sig, lambda: asyncio.create_task(self.stop_server())
                    )
                
                # Connect to all MCP servers
                await self.connect_to_all_servers()
                
                # Serve until stopped
                await self.server.serve_forever()
                
            return True
            
        except Exception as e:
            logger.error(f"Error starting server: {str(e)}")
            return False
            
    async def stop_server(self):
        """Stop the IPC server and disconnect from all MCP servers"""
        if not self.running:
            return

        logger.info("Stopping MCP daemon server...")

        # Stop server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

        # Close Streamable HTTP sessions explicitly (sends DELETE request)
        for name, session in self.sessions.items():
            if session.transport_type == 'streamable-http':
                logger.debug(f"Terminating Streamable HTTP session for '{name}'")
                await self.streamable_http_manager.close_session(session)

        # Close all MCP sessions (this will trigger MCP SDK cleanup)
        await self.exit_stack.aclose()
        self.sessions.clear()

        # Remove socket file
        try:
            if os.path.exists(self.socket_path):
                os.unlink(self.socket_path)
        except OSError as e:
            logger.error(f"Error removing socket file: {str(e)}")

        self.running = False
        logger.info("MCP daemon server stopped")
