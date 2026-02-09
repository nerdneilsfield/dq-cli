# dq-cli Tests

This directory contains tests for the dq-cli project, with a focus on the MCP Streamable HTTP transport implementation.

## Running Tests

### Install Test Dependencies

```bash
uv pip install pytest pytest-asyncio pytest-mock
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test Files

```bash
# Test MCP daemon models
pytest tests/mcp_daemon/test_models.py

# Test Streamable HTTP manager
pytest tests/mcp_daemon/test_streamable_http.py

# Test MCP server configuration
pytest tests/test_mcp_server_config.py
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html tests/
```

### Run with Verbose Output

```bash
pytest -v tests/
```

## Test Structure

```
tests/
├── __init__.py
├── README.md                          # This file
├── mcp_daemon/
│   ├── __init__.py
│   ├── test_models.py                # Tests for SessionState and ServerSession
│   └── test_streamable_http.py       # Tests for StreamableHTTPManager
└── test_mcp_server_config.py         # Tests for McpServerConfig model
```

## Test Coverage

### MCP Daemon Models (`test_models.py`)
- ✅ SessionState enum values and count
- ✅ ServerSession creation (minimal and full)
- ✅ Session state transitions
- ✅ Transport type validation
- ✅ Session ID and event ID handling

### Streamable HTTP Manager (`test_streamable_http.py`)
- ✅ Manager initialization
- ✅ Localhost detection
- ✅ Origin validation
- ✅ HTTP client creation with auth and custom headers
- ✅ MCP header filtering
- ✅ Connection handling and error cases
- ✅ Session state management

### MCP Server Configuration (`test_mcp_server_config.py`)
- ✅ Config creation for stdio and HTTP servers
- ✅ Streamable HTTP options (transport_type, custom_headers, timeout)
- ✅ Config serialization (to_dict/from_dict)
- ✅ None value exclusion
- ✅ Backward compatibility with old configs

## Integration Testing

To test with a real Streamable HTTP MCP server:

1. Set up a test MCP server that supports Streamable HTTP
2. Configure it in your MCP config:
   ```bash
   dq-cli mcp add my-test-server --url https://localhost:8080/mcp --transport streamable-http
   ```
3. Start the MCP daemon and verify connection in logs

## Notes

- Tests use `pytest-asyncio` for async test support
- Mocks are used extensively to avoid requiring real MCP servers
- Integration tests can be run against localhost test servers
