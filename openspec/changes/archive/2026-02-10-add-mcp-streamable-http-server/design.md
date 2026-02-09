## Context

The Model Context Protocol (MCP) specification 2025-03-26 introduced Streamable HTTP transport to replace the deprecated HTTP+SSE transport. dq-cli currently implements:

- **stdio transport** (`stdio.py`) - launches MCP servers as subprocesses
- **HTTP+SSE transport** (`sse.py`) - uses legacy `mcp.client.sse.sse_client`
- **MCP daemon architecture** (`server.py`) - maintains persistent connections to MCP servers via Unix socket IPC

The existing SSE implementation uses the MCP SDK's `sse_client()` which follows the old specification. Modern MCP servers are migrating to Streamable HTTP, which offers:

1. **True bidirectional communication** - servers can initiate requests to clients
2. **Session management** - `Mcp-Session-Id` header for stateful interactions
3. **Resumability** - `Last-Event-ID` header for reconnection after network failures
4. **Better security** - Origin validation, standard CORS, stronger auth patterns

**Current constraints:**
- Must maintain backward compatibility with existing stdio and legacy SSE transports
- MCP daemon runs as a background process managing multiple server connections
- Unix socket IPC interface for chat sessions to interact with MCP tools
- Uses `mcp>=1.2.1` SDK and `httpx` for HTTP operations

**Stakeholders:**
- Chat sessions needing MCP tool access
- MCP server configurations (stdio, legacy SSE, Streamable HTTP)

## Goals / Non-Goals

**Goals:**
- Implement complete Streamable HTTP transport per MCP 2025-03-26 specification
- Support both single JSON responses and SSE streaming modes
- Implement session management with `Mcp-Session-Id` headers
- Implement resumable connections via `Last-Event-ID` headers
- Add Origin validation for security
- Auto-detect transport type (Streamable HTTP vs legacy SSE) when connecting
- Maintain full backward compatibility with existing transports

**Non-Goals:**
- Rewriting existing stdio or legacy SSE transport implementations
- Implementing custom transports beyond the MCP specification
- Supporting the completely deprecated 2024-11-05 HTTP+SSE specification indefinitely (only during migration period)
- Building a general-purpose HTTP server (focus is MCP client implementation)

## Decisions

### Decision 1: Unified Manager Architecture

**Choice:** Create a new `StreamableHTTPManager` class following the same pattern as `SSEManager` and `StdioManager`.

**Rationale:**
- Maintains consistency with existing codebase architecture
- Each transport manager encapsulates its connection logic, session handling, and lifecycle
- Clean separation of concerns - `server.py` orchestrates, managers implement transport-specific logic
- Easy to test and maintain in isolation

**Alternatives considered:**
- ❌ Extend existing `SSEManager` - would create complex conditionals and violate single responsibility
- ❌ Implement directly in `server.py` - would bloat the orchestration layer

### Decision 2: Transport Detection Strategy

**Choice:** Implement auto-detection by attempting Streamable HTTP first, falling back to legacy SSE on failure.

**Detection algorithm:**
```python
1. POST InitializeRequest to server URL with Accept: application/json, text/event-stream
2. If success → Streamable HTTP transport
3. If 4xx error → Try GET for SSE stream expecting 'endpoint' event (legacy)
4. If 'endpoint' event received → Legacy HTTP+SSE transport
5. If all fail → Connection error
```

**Rationale:**
- Follows the backward compatibility pattern from MCP specification
- Prefer modern transport by default
- Graceful degradation to legacy for older servers
- No configuration required from users

**Alternatives considered:**
- ❌ Require explicit transport configuration - adds user burden and complexity
- ❌ Only support Streamable HTTP - breaks existing MCP server connections

### Decision 3: Session State Management

**Choice:** Store session state in `ServerSession` model with session ID, event cursor, and connection metadata.

**Model extension:**
```python
@dataclass
class ServerSession:
    session: ClientSession
    transport_type: str  # 'stdio', 'sse', 'streamable-http'
    session_id: Optional[str] = None  # For Streamable HTTP
    last_event_id: Optional[str] = None  # For resumability
    endpoint_url: Optional[str] = None
```

**Rationale:**
- Minimal extension to existing model
- Session ID enables stateful server interactions
- Event cursor enables resumability
- Transport type enables session-aware routing

**Alternatives considered:**
- ❌ Separate session store - adds complexity without clear benefit
- ❌ Store in manager only - loses session state on manager reload

### Decision 4: HTTP Client Implementation

**Choice:** Use `httpx.AsyncClient` for HTTP operations with custom SSE stream parsing.

**Rationale:**
- `httpx` already in dependencies (`pyproject.toml`)
- Async-native, matches existing `asyncio` architecture
- Supports streaming responses for SSE mode
- Header management (Accept, Mcp-Session-Id, Last-Event-ID) is straightforward

**Implementation approach:**
```python
async with httpx.AsyncClient() as client:
    # POST for requests
    response = await client.post(url, json=request, headers={
        'Accept': 'application/json, text/event-stream',
        'Mcp-Session-Id': session_id
    })

    # Handle JSON or SSE response based on Content-Type
    if response.headers['Content-Type'] == 'application/json':
        return response.json()
    else:  # text/event-stream
        async for event in parse_sse_stream(response):
            yield event
```

**Alternatives considered:**
- ❌ Use MCP SDK's SSE client - designed for legacy transport, not Streamable HTTP
- ❌ Build custom HTTP client - reinvents wheel, httpx is battle-tested

### Decision 5: Multiple Concurrent SSE Streams

**Choice:** Support multiple concurrent GET connections for server-initiated messages, using event IDs to prevent message duplication.

**Rationale:**
- Specification allows multiple SSE streams per session
- Enables parallel request handling (client request stream + server notification stream)
- Event IDs ensure each message delivered exactly once

**Implementation:**
- Track active streams per session in manager state
- Route server messages to only one stream (round-robin or message type-based)
- Support resumability per stream using Last-Event-ID

**Alternatives considered:**
- ❌ Single stream only - limits concurrency and violates spec
- ❌ Broadcast to all streams - causes message duplication

### Decision 6: Origin Validation

**Choice:** Implement Origin validation for locally-bound servers only, skip for remote HTTPS servers.

**Security check:**
```python
if is_local_server(url):
    # Bind to localhost only
    # Validate Origin header matches expected value
    # Reject requests from unexpected origins
else:
    # HTTPS remote servers handle their own CORS
    pass
```

**Rationale:**
- DNS rebinding attacks only affect local servers
- Remote servers implement their own CORS/Origin policies
- Prevents malicious websites from accessing local MCP servers

**Alternatives considered:**
- ❌ No validation - security vulnerability for local servers
- ❌ Validate all origins - interferes with legitimate remote server CORS

## Risks / Trade-offs

**[Risk]** MCP SDK may not fully support Streamable HTTP yet (current version `mcp>=1.2.1`)
→ **Mitigation:** Implement using `httpx` directly; can integrate SDK support later when available

**[Risk]** Legacy SSE servers may not follow backward compatibility pattern correctly
→ **Mitigation:** Comprehensive error handling; log detection failures; allow manual transport configuration as escape hatch

**[Risk]** Session state loss on daemon restart breaks in-progress operations
→ **Mitigation:** Document session lifecycle; implement graceful reconnection; sessions re-initialize on reconnect

**[Risk]** Multiple SSE streams increase connection overhead
→ **Mitigation:** Make concurrent GET connections optional; reuse POST streams when possible; implement connection pooling

**[Risk]** Resumability requires server-side event ID support (optional in spec)
→ **Mitigation:** Gracefully handle servers without event IDs; treat as non-resumable; log capability detection

**[Trade-off]** Auto-detection adds connection latency on first connect
→ **Accepted:** One-time cost; subsequent connections use cached transport type; improves UX over manual config

**[Trade-off]** Maintaining three transports increases code complexity
→ **Accepted:** Clean manager separation minimizes cross-transport complexity; backward compatibility is essential during migration

## Migration Plan

**Phase 1: Implementation** (this change)
1. Implement `StreamableHTTPManager` with full Streamable HTTP support
2. Add transport detection logic to `server.py`
3. Extend `ServerSession` model with session/event state
4. Update configuration schema for Streamable HTTP options
5. Comprehensive testing with mock Streamable HTTP servers

**Phase 2: Deployment**
1. Release with feature flag (default: auto-detect)
2. Monitor connection success rates and transport detection
3. Gather feedback on Streamable HTTP vs legacy SSE performance

**Phase 3: Migration**
1. Update documentation with Streamable HTTP examples
2. Encourage users to upgrade MCP servers to Streamable HTTP
3. Keep legacy SSE support for backward compatibility

**Rollback strategy:**
- Feature flag to disable Streamable HTTP (fall back to legacy SSE only)
- No database migrations or persistent state changes
- Safe to revert code changes without data loss

## Open Questions

1. **Q:** Should we cache transport detection results per server URL?
   **A:** Yes - add to config file after successful detection; reduces connection latency

2. **Q:** How to handle session expiration (HTTP 404 on session ID)?
   **A:** Auto-reinitialize with new session; transparent to chat sessions; log session restart

3. **Q:** Support for DELETE endpoint to terminate sessions?
   **A:** Implement as optional; send on daemon shutdown; graceful fallback if server returns 405
