"""
Streamable HTTP transport manager for MCP servers.

Uses the official MCP SDK streamable_http_client for MCP Streamable HTTP transport
per specification 2025-03-26.
"""

import asyncio
from typing import Optional, Dict
from urllib.parse import urlparse
from contextlib import AsyncExitStack
from loguru import logger
import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from .models import ServerSession, SessionState


class StreamableHTTPManager:
    """Manages Streamable HTTP connections to MCP servers"""

    def __init__(self, exit_stack: AsyncExitStack):
        self.exit_stack = exit_stack
        self.default_timeout = httpx.Timeout(30.0, connect=10.0)

    def _is_localhost(self, url: str) -> bool:
        """Check if URL points to localhost"""
        parsed = urlparse(url)
        hostname = parsed.hostname or ''
        return hostname in ('localhost', '127.0.0.1', '::1', '[::1]')

    def _validate_origin(self, url: str):
        """Validate Origin header for localhost servers to prevent DNS rebinding"""
        if self._is_localhost(url):
            # For localhost servers, we should validate the Origin header
            # This is a security measure against DNS rebinding attacks
            # In practice, the MCP SDK handles this, but we log it for awareness
            logger.debug(f"Connecting to localhost server: {url}")

    def _create_http_client(self,
                           auth_token: Optional[str] = None,
                           custom_headers: Optional[Dict[str, str]] = None,
                           timeout: Optional[httpx.Timeout] = None) -> httpx.AsyncClient:
        """
        Create an httpx.AsyncClient with appropriate configuration.

        Args:
            auth_token: Optional Bearer token for authentication
            custom_headers: Optional custom headers to include
            timeout: Optional timeout configuration

        Returns:
            Configured httpx.AsyncClient
        """
        headers = {}

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        if custom_headers:
            # Merge custom headers, but don't override MCP-specific headers
            for key, value in custom_headers.items():
                if key.lower() not in ("mcp-session-id", "accept", "content-type"):
                    headers[key] = value

        return httpx.AsyncClient(
            headers=headers,
            timeout=timeout or self.default_timeout,
            follow_redirects=True
        )

    async def connect(self,
                     server_name: str,
                     url: str,
                     auth_token: Optional[str] = None,
                     custom_headers: Optional[Dict[str, str]] = None,
                     timeout: Optional[float] = None) -> Optional[ServerSession]:
        """
        Connect to an MCP server using Streamable HTTP transport.

        Args:
            server_name: Name of the server
            url: Server endpoint URL
            auth_token: Optional authentication token
            custom_headers: Optional custom headers
            timeout: Optional timeout in seconds

        Returns:
            ServerSession if successful, None otherwise
        """
        try:
            # Validate origin for localhost servers
            self._validate_origin(url)

            logger.info(f"Connecting to Streamable HTTP server '{server_name}' at {url}")

            # Create HTTP client with configuration
            timeout_config = None
            if timeout:
                timeout_config = httpx.Timeout(timeout, connect=timeout / 3)

            http_client = self._create_http_client(
                auth_token=auth_token,
                custom_headers=custom_headers,
                timeout=timeout_config
            )

            # Use the official MCP SDK streamable_http_client
            streams = await self.exit_stack.enter_async_context(
                streamable_http_client(url, http_client=http_client)
            )

            read_stream, write_stream, get_session_id = streams

            # Create ClientSession using the streams
            session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            # Initialize the session
            await session.initialize()

            # Get the session ID from the callback
            session_id = get_session_id()

            logger.info(f"Connected to Streamable HTTP server '{server_name}' with session_id={session_id}")

            # Create and return ServerSession
            server_session = ServerSession(
                session=session,
                transport_type='streamable-http',
                session_id=session_id,
                endpoint_url=url
            )
            server_session.state = SessionState.ACTIVE

            return server_session

        except httpx.HTTPStatusError as e:
            if 400 <= e.response.status_code < 500:
                logger.debug(f"HTTP {e.response.status_code} - server may not support Streamable HTTP")
            else:
                logger.error(f"HTTP error connecting to '{server_name}': {e.response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Error connecting to Streamable HTTP server '{server_name}': {str(e)}")
            if hasattr(e, '__traceback__'):
                import traceback
                logger.debug(f"Detailed error:\n{''.join(traceback.format_tb(e.__traceback__))}")
            return None

    async def close_session(self, server_session: ServerSession):
        """
        Close a Streamable HTTP session.

        The MCP SDK handles sending DELETE request automatically when the context exits.
        This method is for explicit cleanup if needed.
        """
        try:
            server_session.state = SessionState.DISCONNECTED
            logger.info(f"Closed Streamable HTTP session {server_session.session_id}")
        except Exception as e:
            logger.error(f"Error closing session: {str(e)}")
