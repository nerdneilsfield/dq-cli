## Why

The Model Context Protocol (MCP) updated its specification on 2025-03-26, replacing the HTTP+SSE transport with a new **Streamable HTTP** transport. This new transport provides true bidirectional communication, stronger authentication, session management, and resumable connections. Currently, dq-cli only supports the deprecated HTTP+SSE transport via `mcp.client.sse`, which limits interoperability with modern MCP servers and misses out on improved security and reliability features.

## What Changes

- Add support for the new MCP Streamable HTTP transport alongside existing SSE and stdio transports
- Implement HTTP POST/GET-based message exchange with optional SSE streaming
- Add session management with `Mcp-Session-Id` header support
- Implement resumable connections using SSE event IDs and `Last-Event-ID` header
- Add origin validation and security checks for HTTP transport
- Update MCP daemon server to detect and use Streamable HTTP when available
- Maintain backward compatibility with existing HTTP+SSE transport
- Add configuration options for Streamable HTTP servers in MCP config

## Capabilities

### New Capabilities
- `mcp-streamable-http-transport`: Complete implementation of MCP Streamable HTTP transport per 2025-03-26 specification, including HTTP POST/GET message exchange, optional SSE streaming, session management, resumability, and security validation
- `mcp-transport-detection`: Automatic detection and selection of appropriate transport (Streamable HTTP vs legacy HTTP+SSE) when connecting to MCP servers

### Modified Capabilities
- `model-switching`: Update to support Streamable HTTP transport alongside existing transports, allowing seamless model switching across different transport types

## Impact

**Affected Code:**
- `src/mcp_daemon/server.py` - Add Streamable HTTP manager initialization and connection logic
- `src/mcp_daemon/sse.py` - Refactor to support both legacy SSE and new Streamable HTTP SSE modes
- `src/mcp_daemon/models.py` - Add session models for Streamable HTTP (session IDs, event cursors)
- `src/mcp_daemon/handlers.py` - Update request handlers to support session-aware routing
- New file: `src/mcp_daemon/streamable_http.py` - Streamable HTTP transport manager

**Dependencies:**
- May require updated `mcp` SDK version if available (currently using `mcp>=1.2.1`)
- Add `httpx` for HTTP client operations (already in dependencies)

**Configuration:**
- Extend MCP server config schema to include Streamable HTTP options (endpoint URL, auth headers, session preferences)
- Add transport selection strategy (auto-detect, prefer-streamable, legacy-only)

**Breaking Changes:**
- None - maintains full backward compatibility with existing SSE and stdio transports
