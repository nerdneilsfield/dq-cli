# MCP Streamable HTTP Troubleshooting Guide

Common issues and solutions for MCP Streamable HTTP transport in dq-cli.

## Connection Issues

### "Failed to connect - no compatible transport"

**Symptoms:**
```
ERROR Failed to connect to server 'my-server' - no compatible transport found
```

**Causes:**
1. Server URL is incorrect or unreachable
2. Server doesn't support MCP protocol
3. Network connectivity issues
4. Server is down

**Solutions:**

1. **Verify server URL**
   ```bash
   # Test with curl
   curl -X POST https://your-server-url/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
   ```

2. **Check server status**
   ```bash
   # Ping server
   ping your-server-domain.com

   # Check if server is responding
   curl -I https://your-server-url/mcp
   ```

3. **Try explicit transport**
   ```bash
   # Force Streamable HTTP
   dq-cli mcp add server --url URL --transport streamable-http

   # Try legacy SSE if server is old
   dq-cli mcp add server --url URL --transport legacy-sse
   ```

4. **Check daemon logs**
   ```bash
   dq-cli daemon log | grep -A 5 "Connecting to HTTP server"
   ```

### "HTTP 404 Not Found"

**Symptoms:**
```
ERROR HTTP 404 - server may not support Streamable HTTP
```

**Causes:**
1. Incorrect endpoint path
2. Server uses different URL structure
3. Session expired (for subsequent requests)

**Solutions:**

1. **Verify endpoint path**
   - Correct: `https://api.example.com/mcp`
   - Incorrect: `https://api.example.com/` (missing `/mcp`)

2. **Check server documentation**
   - Some servers use `/api/mcp`, `/v1/mcp`, etc.

3. **For session expiration**
   ```bash
   # Restart daemon to establish new sessions
   dq-cli daemon restart
   ```

### "HTTP 401 Unauthorized"

**Symptoms:**
```
ERROR HTTP error connecting to 'server': 401
```

**Causes:**
1. Missing or invalid authentication token
2. Token expired
3. Wrong authentication method

**Solutions:**

1. **Check token**
   ```bash
   # Verify token is set
   dq-cli mcp list  # Look for 'token' field

   # Update token
   dq-cli mcp delete old-server
   dq-cli mcp add server --url URL --token NEW-TOKEN
   ```

2. **Try different auth methods**
   ```bash
   # Bearer token (default)
   dq-cli mcp add server --url URL --token sk-xxxxx

   # Custom header
   dq-cli mcp add server --url URL --header "X-API-Key: xxxxx"

   # Basic auth (if required)
   dq-cli mcp add server --url https://user:pass@example.com/mcp
   ```

3. **Check token expiration**
   - Regenerate token from server dashboard
   - Update config with new token

### "Connection timeout"

**Symptoms:**
```
ERROR Connection error: Timeout
```

**Causes:**
1. Server is slow to respond
2. Network latency
3. Server is processing heavy workload
4. Default timeout too short

**Solutions:**

1. **Increase timeout**
   ```bash
   # Try 60 seconds
   dq-cli mcp add server --url URL --timeout 60

   # Try 120 seconds for very slow servers
   dq-cli mcp add server --url URL --timeout 120
   ```

2. **Edit config directly**
   ```bash
   # Edit: ~/.local/share/dq-cli/mcp_config.jsonl
   # Add: "timeout": 120.0
   ```

3. **Check network**
   ```bash
   # Test network latency
   time curl https://your-server-url/mcp
   ```

## Session Management Issues

### "Session expired and reinitialization failed"

**Symptoms:**
```
ERROR HTTP 404 on session ID - reinitialization failed
```

**Causes:**
1. Server restarted
2. Session TTL expired
3. Server lost session state

**Solutions:**

1. **Restart daemon**
   ```bash
   dq-cli daemon restart
   ```

2. **Check server health**
   - Verify server is running
   - Check server logs for errors

3. **Increase session timeout on server**
   - Configure server to keep sessions longer
   - Contact server administrator

### "Multiple session IDs detected"

**Symptoms:**
Multiple connections with different session IDs

**Causes:**
1. Daemon restarted mid-session
2. Multiple dq-cli instances running

**Solutions:**

1. **Clean restart**
   ```bash
   dq-cli daemon stop
   # Wait 5 seconds
   dq-cli daemon start
   ```

2. **Check for multiple processes**
   ```bash
   ps aux | grep dq-cli
   # Kill any duplicate processes
   ```

## Transport Detection Issues

### "Auto-detection always uses legacy SSE"

**Symptoms:**
```
WARNING Connected to 'server' using legacy HTTP+SSE (deprecated)
```

**Causes:**
1. Server doesn't support Streamable HTTP yet
2. Server's Streamable HTTP endpoint is misconfigured
3. Auto-detection incorrectly falls back

**Solutions:**

1. **Verify server supports Streamable HTTP**
   ```bash
   # Test Streamable HTTP directly
   curl -X POST https://server/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
   ```

2. **Force Streamable HTTP to test**
   ```bash
   dq-cli mcp add server --url URL --transport streamable-http
   ```

3. **If server truly doesn't support it**
   - Contact server maintainer to upgrade
   - Or explicitly use legacy: `--transport legacy-sse`

### "Cached wrong transport type"

**Symptoms:**
Server was upgraded but still using old transport

**Causes:**
Cached `transport_type` in config from previous detection

**Solutions:**

1. **Clear cached transport**
   ```bash
   # Edit: ~/.local/share/dq-cli/mcp_config.jsonl
   # Remove: "transport_type": "legacy-sse"
   # Save and restart daemon
   ```

2. **Or delete and re-add server**
   ```bash
   dq-cli mcp delete server
   dq-cli mcp add server --url URL  # Will re-detect
   ```

## Custom Headers Issues

### "Custom headers not being sent"

**Symptoms:**
Server reports missing required headers

**Causes:**
1. Headers not properly configured
2. Header names case-sensitive
3. MCP-specific headers being filtered

**Solutions:**

1. **Check header configuration**
   ```bash
   # View current config
   dq-cli mcp list

   # Re-add with correct headers
   dq-cli mcp add server \
     --url URL \
     --header "X-API-Key: value" \
     --header "X-Client-ID: dq-cli"
   ```

2. **Don't use MCP reserved headers**
   ```
   ❌ Mcp-Session-Id  (managed automatically)
   ❌ Accept           (set by MCP SDK)
   ❌ Content-Type     (set by MCP SDK)

   ✅ X-API-Key
   ✅ X-Custom-Header
   ✅ Authorization (if not using --token)
   ```

3. **Check header format**
   ```json
   {
     "custom_headers": {
       "X-API-Key": "value",  // ✅ Correct
       "X-ANOTHER": "value"   // ✅ Uppercase OK
     }
   }
   ```

## Performance Issues

### "Slow initial connection"

**Symptoms:**
First connection takes 10-30 seconds

**Causes:**
1. Auto-detection trying multiple transports
2. Network latency
3. Server slow to initialize

**Solutions:**

1. **Use explicit transport to skip detection**
   ```bash
   dq-cli mcp add server --url URL --transport streamable-http
   ```

2. **Connection will be cached and faster next time**

3. **Check network and server performance**

### "Slow subsequent requests"

**Symptoms:**
Every MCP tool call is slow

**Causes:**
1. Server processing is slow
2. Network latency
3. Large response payloads

**Solutions:**

1. **Check server performance**
   - Monitor server CPU/memory
   - Check server logs for slow queries

2. **Optimize network**
   - Use server geographically closer
   - Check for network bottlenecks

3. **Not a dq-cli issue**
   - MCP SDK passes requests through efficiently
   - Investigate server-side performance

## Logging and Debugging

### Enable Debug Logging

1. **Check daemon logs**
   ```bash
   dq-cli daemon log

   # Filter for specific server
   dq-cli daemon log | grep "server-name"

   # Filter for errors
   dq-cli daemon log | grep ERROR
   ```

2. **Increase log verbosity**
   Edit daemon config (if available) to set log level to DEBUG

3. **Monitor real-time**
   ```bash
   tail -f ~/.local/share/dq-cli/logs/daemon.log
   ```

### Test Connection Manually

```bash
# Test Streamable HTTP endpoint
curl -v -X POST https://your-server/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR-TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test", "version": "1.0"}
    }
  }'
```

Expected response:
- Status: 200 OK
- Headers: May include `Mcp-Session-Id`
- Content-Type: `application/json` or `text/event-stream`
- Body: InitializeResult JSON

## Common Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| `HTTP 400` | Bad request format | Check request JSON structure |
| `HTTP 401` | Unauthorized | Verify token/credentials |
| `HTTP 404` | Endpoint not found OR session expired | Check URL OR restart daemon |
| `HTTP 405` | Method not allowed | Server may not support Streamable HTTP |
| `HTTP 500` | Server error | Check server logs, contact admin |
| `Connection refused` | Server not running | Start server, check firewall |
| `Timeout` | Slow response | Increase timeout, check network |

## Getting Help

If you're still stuck:

1. **Collect diagnostic info**
   ```bash
   dq-cli mcp list > mcp-config.txt
   dq-cli daemon log | tail -100 > daemon-log.txt
   dq-cli daemon status > daemon-status.txt
   ```

2. **Create minimal reproduction**
   ```bash
   # Try with a known-working public MCP server
   # If that works, issue is with your server
   # If that fails, issue may be with dq-cli
   ```

3. **Check resources**
   - [MCP Specification](https://modelcontextprotocol.io/)
   - [dq-cli GitHub Issues](https://github.com/yourusername/dq-cli/issues)
   - Server-specific documentation

4. **File an issue**
   Include:
   - dq-cli version
   - MCP server type and version
   - Sanitized config
   - Relevant logs
   - Steps to reproduce
