# MCP Server Configuration Examples

This document provides real-world examples of MCP server configurations for dq-cli.

## Table of Contents

- [Basic Configurations](#basic-configurations)
- [Streamable HTTP Examples](#streamable-http-examples)
- [Legacy SSE Examples](#legacy-sse-examples)
- [stdio Examples](#stdio-examples)
- [Advanced Configurations](#advanced-configurations)

## Basic Configurations

### Minimal Streamable HTTP Server

```json
{
  "name": "simple-mcp",
  "url": "https://api.example.com/mcp"
}
```

Auto-detects transport, no authentication.

### With Authentication

```json
{
  "name": "authenticated-mcp",
  "url": "https://api.example.com/mcp",
  "token": "sk-xxxxx"
}
```

Uses Bearer token authentication.

## Streamable HTTP Examples

### Public API Server

```json
{
  "name": "anthropic-mcp",
  "url": "https://api.anthropic.com/v1/mcp",
  "token": "sk-ant-api03-xxxxx",
  "transport_type": "streamable-http",
  "timeout": 60.0
}
```

### Internal Corporate Server

```json
{
  "name": "corp-knowledge-base",
  "url": "https://internal.company.com/mcp/knowledge",
  "token": "internal-jwt-token-xxxxx",
  "transport_type": "streamable-http",
  "custom_headers": {
    "X-Department": "Engineering",
    "X-Client-ID": "dq-cli-prod",
    "X-API-Version": "2025-03"
  },
  "timeout": 120.0,
  "auto_confirm": ["search_docs", "get_policy"]
}
```

Features:
- Custom department and client identification
- Extended timeout for slow internal network
- Auto-confirm safe read-only tools

### Localhost Development Server

```json
{
  "name": "local-dev-server",
  "url": "http://localhost:8080/mcp",
  "transport_type": "streamable-http",
  "timeout": 30.0
}
```

Development server running locally, no auth required.

### Multi-Region Load Balanced

```json
{
  "name": "global-mcp",
  "url": "https://mcp-global.example.com/api/v1",
  "token": "global-access-token",
  "transport_type": "streamable-http",
  "custom_headers": {
    "X-Region-Preference": "us-west-2",
    "X-Fallback-Region": "us-east-1"
  },
  "timeout": 45.0
}
```

## Legacy SSE Examples

### Older MCP Server (Pre-2025)

```json
{
  "name": "legacy-server",
  "url": "https://old-mcp.example.com/sse",
  "token": "legacy-token",
  "transport_type": "legacy-sse"
}
```

Explicitly uses deprecated HTTP+SSE transport.

### Auto-Detected Legacy

```json
{
  "name": "auto-legacy",
  "url": "https://old-api.example.com/mcp",
  "transport_type": "legacy-sse"
}
```

After auto-detection failed for Streamable HTTP, cached as legacy-sse.

## stdio Examples

### Node.js MCP Server

```json
{
  "name": "mcp-todo",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-todo"],
  "env": {
    "TODO_DB_PATH": "/Users/username/.local/share/dq-cli/todos.json"
  }
}
```

### Python MCP Server

```json
{
  "name": "python-search",
  "command": "uvx",
  "args": ["mcp-server-search"],
  "env": {
    "SEARCH_INDEX_PATH": "/data/search-index",
    "LOG_LEVEL": "info"
  }
}
```

### Custom Binary

```json
{
  "name": "custom-mcp",
  "command": "/usr/local/bin/my-mcp-server",
  "args": ["--config", "/etc/mcp/config.yaml", "--verbose"],
  "env": {
    "MCP_PORT": "9000",
    "MCP_DB": "postgresql://localhost/mcp"
  }
}
```

## Advanced Configurations

### Multi-Tool Server with Auto-Confirm

```json
{
  "name": "productivity-suite",
  "url": "https://tools.example.com/mcp",
  "token": "productivity-token",
  "transport_type": "streamable-http",
  "custom_headers": {
    "X-Workspace-ID": "team-engineering",
    "X-User-Tier": "premium"
  },
  "timeout": 90.0,
  "auto_confirm": [
    "read_calendar",
    "list_emails",
    "search_documents",
    "get_weather"
  ]
}
```

Auto-confirms safe read-only tools, still prompts for write operations.

### Development with Debug Headers

```json
{
  "name": "debug-mcp",
  "url": "http://localhost:3000/mcp",
  "transport_type": "streamable-http",
  "custom_headers": {
    "X-Debug-Mode": "true",
    "X-Trace-ID": "dev-session-123",
    "X-Log-Level": "debug"
  },
  "timeout": 300.0
}
```

Extended timeout and debug headers for development.

### High-Security Production

```json
{
  "name": "production-secure",
  "url": "https://secure-mcp.example.com/api/v2/mcp",
  "token": "prod-rotated-token-xxxxx",
  "transport_type": "streamable-http",
  "custom_headers": {
    "X-Client-Certificate": "cert-hash-xxxxx",
    "X-Request-Signature": "sig-xxxxx",
    "X-Timestamp": "auto",
    "X-Nonce": "auto"
  },
  "timeout": 60.0,
  "auto_confirm": []
}
```

No auto-confirm, all tools require explicit user approval.

### Fallback Chain Configuration

Primary server (Streamable HTTP):
```json
{
  "name": "primary-mcp",
  "url": "https://primary.example.com/mcp",
  "token": "primary-token",
  "transport_type": "streamable-http",
  "timeout": 30.0
}
```

Fallback server (Legacy SSE):
```json
{
  "name": "fallback-mcp",
  "url": "https://fallback.example.com/mcp",
  "token": "fallback-token",
  "transport_type": "legacy-sse",
  "timeout": 30.0
}
```

Use primary first, switch to fallback manually if needed.

### Hybrid Setup (stdio + HTTP)

Local tools (stdio):
```json
{
  "name": "local-tools",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem"],
  "env": {
    "ALLOWED_PATHS": "/Users/username/Documents"
  }
}
```

Remote API (Streamable HTTP):
```json
{
  "name": "remote-api",
  "url": "https://api.example.com/mcp",
  "token": "api-token",
  "transport_type": "streamable-http"
}
```

Best of both worlds: local file access + remote AI capabilities.

## Configuration Templates

### Template: Generic Streamable HTTP

```json
{
  "name": "YOUR-SERVER-NAME",
  "url": "https://YOUR-SERVER-URL/mcp",
  "token": "YOUR-AUTH-TOKEN",
  "transport_type": "streamable-http",
  "custom_headers": {
    "X-Custom-Header": "value"
  },
  "timeout": 60.0,
  "auto_confirm": []
}
```

### Template: Generic stdio

```json
{
  "name": "YOUR-SERVER-NAME",
  "command": "YOUR-COMMAND",
  "args": ["ARG1", "ARG2"],
  "env": {
    "ENV_VAR": "value"
  },
  "auto_confirm": []
}
```

## Tips and Best Practices

### Transport Selection

1. **Use `auto`** for new servers (default)
   - Let dq-cli detect the best transport
   - Automatically caches result for faster future connections

2. **Use `streamable-http`** when you know the server supports it
   - Slightly faster initial connection (skips detection)
   - Explicit configuration for production

3. **Use `legacy-sse`** only for older servers
   - If auto-detection shows deprecation warning
   - Server hasn't upgraded to Streamable HTTP yet

### Timeout Configuration

- **Default (30s)**: Good for most servers
- **Fast servers (15-20s)**: Internal or local servers
- **Slow servers (60-120s)**: Complex queries, slow networks
- **Development (300s)**: Debugging, step-through debugging

### Custom Headers

Use custom headers for:
- API versioning: `X-API-Version: 2025-03`
- Client identification: `X-Client-ID: dq-cli-v0.4.0`
- Workspace/tenant: `X-Workspace-ID: team-name`
- Feature flags: `X-Enable-Beta-Features: true`

### Auto-Confirm

Only auto-confirm tools that are:
- ✅ Read-only (search, list, get)
- ✅ Safe (weather, time, calculator)
- ✅ Non-destructive (preview, validate)

Never auto-confirm:
- ❌ Write operations (create, update, delete)
- ❌ Execute actions (send_email, post_message)
- ❌ Financial transactions (charge, transfer)

## Troubleshooting Configurations

### Server Not Connecting

Check your config:
```bash
# View current configs
dq-cli mcp list

# Check daemon logs for errors
dq-cli daemon log | grep ERROR

# Try manual transport
dq-cli mcp add test --url YOUR-URL --transport streamable-http
```

### Authentication Failing

Verify:
- Token is current and not expired
- Token format matches server requirements
- Required custom headers are present

### Timeout Issues

Increase timeout gradually:
```json
"timeout": 30.0  // Start here
"timeout": 60.0  // If still timing out
"timeout": 120.0 // Last resort
```

If still timing out, check server health.

## See Also

- [MCP Streamable HTTP Guide](./MCP_STREAMABLE_HTTP.md)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
