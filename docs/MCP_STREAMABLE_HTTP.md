# MCP Streamable HTTP Transport Support

dq-cli now supports the **MCP Streamable HTTP** transport (per MCP specification 2025-03-26), providing enhanced connectivity to modern MCP servers.

## What is Streamable HTTP?

Streamable HTTP is the modern transport protocol for Model Context Protocol (MCP), replacing the deprecated HTTP+SSE transport. It offers:

- ✅ **True bidirectional communication** - Servers can initiate requests to clients
- ✅ **Session management** - Persistent sessions with `Mcp-Session-Id` headers
- ✅ **Resumable connections** - Automatic reconnection with `Last-Event-ID`
- ✅ **Better security** - Origin validation, standard CORS, improved authentication
- ✅ **Flexible response modes** - Single JSON or SSE streaming

## Supported Transports

dq-cli supports three MCP transport types:

1. **stdio** - Launch MCP servers as subprocesses (traditional)
2. **legacy-sse** - Deprecated HTTP+SSE transport (for compatibility)
3. **streamable-http** - Modern Streamable HTTP transport ⭐ **Recommended**

## Quick Start

### Adding a Streamable HTTP Server

```bash
# Auto-detect transport (tries Streamable HTTP first, falls back to legacy SSE)
dq-cli mcp add my-server --url https://api.example.com/mcp --token your-auth-token

# Explicitly use Streamable HTTP
dq-cli mcp add my-server \
  --url https://api.example.com/mcp \
  --token your-auth-token \
  --transport streamable-http
```

### Configuration Options

When adding an MCP server, you can specify:

- `--url` - Server endpoint URL (required for HTTP transports)
- `--token` - Authentication token (optional)
- `--transport` - Transport type: `auto`, `streamable-http`, `legacy-sse`, or `stdio`
- `--timeout` - Connection timeout in seconds (default: 30)
- `--header` - Custom HTTP headers (can be specified multiple times)

### Examples

#### Basic Streamable HTTP Server

```bash
dq-cli mcp add anthropic-server \
  --url https://api.anthropic.com/mcp \
  --token sk-ant-xxxxx \
  --transport streamable-http
```

#### With Custom Headers and Timeout

```bash
dq-cli mcp add custom-server \
  --url https://internal.company.com/mcp \
  --token internal-token-123 \
  --transport streamable-http \
  --timeout 60 \
  --header "X-API-Key: key123" \
  --header "X-Client-Version: 1.0.0"
```

#### Auto-Detection (Recommended for Most Cases)

```bash
# Let dq-cli detect the best transport automatically
dq-cli mcp add smart-server \
  --url https://mcp-server.example.com/endpoint
```

The auto-detection will:
1. Try Streamable HTTP first
2. Fall back to legacy SSE if Streamable HTTP fails
3. Cache the detected transport type for faster future connections

## Configuration File Format

MCP server configurations are stored in `mcp_config.jsonl`. Example entry:

```json
{
  "name": "my-streamable-server",
  "url": "https://api.example.com/mcp",
  "token": "your-auth-token",
  "transport_type": "streamable-http",
  "custom_headers": {
    "X-API-Key": "key123",
    "X-Client-Version": "1.0.0"
  },
  "timeout": 60.0,
  "auto_confirm": ["safe_tool_1", "safe_tool_2"]
}
```

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Server identifier (required) |
| `url` | string | HTTP endpoint URL (for HTTP transports) |
| `token` | string | Authentication token (optional) |
| `transport_type` | string | `auto`, `streamable-http`, `legacy-sse`, or `stdio` |
| `custom_headers` | object | Custom HTTP headers for requests |
| `timeout` | number | Connection timeout in seconds |
| `command` | string | Command to launch (for stdio transport) |
| `args` | array | Command arguments (for stdio transport) |
| `env` | object | Environment variables (for stdio transport) |
| `auto_confirm` | array | Tools to auto-confirm without prompting |

## Transport Detection and Caching

### Auto-Detection Flow

When `transport_type` is `auto` or not specified:

1. **Try Streamable HTTP**
   - Send POST with InitializeRequest
   - If successful → use Streamable HTTP
   - Cache `transport_type: "streamable-http"` in config

2. **Fallback to Legacy SSE** (if Streamable HTTP fails)
   - Send GET expecting SSE stream
   - If successful → use legacy SSE
   - Cache `transport_type: "legacy-sse"` in config
   - Show deprecation warning

3. **Connection Failed** (if both fail)
   - Log error with diagnostic information
   - Server may not be MCP-compatible

### Manual Override

You can force a specific transport:

```bash
# Force Streamable HTTP (fail if not supported)
dq-cli mcp add server --url https://example.com/mcp --transport streamable-http

# Force legacy SSE (for older servers)
dq-cli mcp add server --url https://example.com/mcp --transport legacy-sse
```

## Session Management

### Session IDs

Streamable HTTP servers may assign session IDs via the `Mcp-Session-Id` header. dq-cli:

- ✅ Automatically extracts and stores session IDs
- ✅ Includes session ID in all subsequent requests
- ✅ Handles session expiration (HTTP 404) with automatic reinitialization
- ✅ Sends DELETE requests on graceful shutdown to terminate sessions

### Session Persistence

Sessions are maintained throughout the daemon lifecycle:

```bash
# Start daemon (establishes sessions)
dq-cli daemon start

# Sessions remain active for all chat interactions
dq-cli chat

# Stop daemon (cleanly terminates sessions)
dq-cli daemon stop
```

### Reconnection

If a connection is lost, dq-cli will:

1. Detect the disconnection
2. Attempt to reconnect using the configured transport
3. Establish a new session (for Streamable HTTP)
4. Resume operations

## Troubleshooting

### Connection Issues

**Problem**: Server connection fails with "no compatible transport"

**Solutions**:
- Verify the server URL is correct
- Check if the server is running and accessible
- Try manual transport selection: `--transport streamable-http` or `--transport legacy-sse`
- Check server logs for errors

### Authentication Errors

**Problem**: HTTP 401 Unauthorized

**Solutions**:
- Verify your `--token` is correct and not expired
- Check if the server requires custom headers (e.g., API keys)
- Add required headers with `--header` option

### Timeout Issues

**Problem**: Connection times out

**Solutions**:
- Increase timeout: `--timeout 120`
- Check network connectivity to the server
- Verify the server is responding (try `curl` to the endpoint)

### Legacy Server Deprecation Warning

**Problem**: Warning about "legacy HTTP+SSE (deprecated)"

**Solution**:
- This is normal for older MCP servers
- Connection will work fine
- Consider asking the server maintainer to upgrade to Streamable HTTP
- You can suppress warnings by explicitly setting `--transport legacy-sse`

## Checking Server Status

View MCP server connection status:

```bash
# List all configured servers
dq-cli mcp list

# View daemon logs
dq-cli daemon log

# Check daemon status
dq-cli daemon status
```

Look for log entries like:
- `Connected to 'server-name' using Streamable HTTP` ✅
- `Connected to 'server-name' using legacy HTTP+SSE (deprecated)` ⚠️
- `Cached transport type 'streamable-http' for 'server-name'` 📦

## Security Considerations

### Localhost Servers

For localhost MCP servers, dq-cli implements Origin validation to prevent DNS rebinding attacks:

- Validates that localhost URLs only accept local connections
- Binds to `127.0.0.1` instead of `0.0.0.0`
- Checks Origin headers on incoming requests

### Authentication

Streamable HTTP supports multiple authentication methods:

1. **Bearer Token** (via `--token`)
   - Sent as `Authorization: Bearer <token>` header
   - Recommended for API-based authentication

2. **Custom Headers** (via `--header`)
   - For API keys, client IDs, etc.
   - Example: `--header "X-API-Key: your-key"`

3. **HTTP Auth** (via URL)
   - `https://user:pass@example.com/mcp`
   - Less secure, use only if required

### HTTPS

Always use HTTPS for production servers:
- ✅ `https://api.example.com/mcp`
- ❌ `http://api.example.com/mcp` (insecure)

Localhost development can use HTTP:
- ✅ `http://localhost:8080/mcp`

## Migration from Legacy SSE

If you have existing servers using legacy HTTP+SSE:

1. **Update Server** - Upgrade server to support Streamable HTTP
2. **Clear Cache** - Remove `transport_type` from config to force re-detection
3. **Restart Daemon** - Restart to pick up new transport

```bash
# Stop daemon
dq-cli daemon stop

# Edit config to remove transport_type (will auto-detect)
# Edit: ~/.local/share/dq-cli/mcp_config.jsonl

# Start daemon (will re-detect as Streamable HTTP)
dq-cli daemon start
```

## Resources

- [MCP Specification - Transports](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Why MCP Switched to Streamable HTTP](https://brightdata.com/blog/ai/sse-vs-streamable-http)

## Changelog

### v0.4.0
- ✨ Added Streamable HTTP transport support
- ✨ Automatic transport detection with caching
- ✨ Session management with Mcp-Session-Id
- ✨ Resumable connections with Last-Event-ID
- ✨ Custom headers and timeout configuration
- 🔄 Upgraded MCP SDK to 1.26.0
- ⚠️ Legacy HTTP+SSE marked as deprecated (still supported)
