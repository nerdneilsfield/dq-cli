# dq-cli Project Context

## Overview

dq-cli is a command-line AI chat application supporting multiple bot configurations, MCP (Model Context Protocol) tool integration, streaming response display, with both local file and Cloudflare D1 storage options.

## Tech Stack

- **Language**: Python 3.x
- **CLI Framework**: Click
- **UI Libraries**:
  - Rich (terminal rich text display)
  - prompt-toolkit (interactive input)
- **HTTP Client**: httpx (async API calls)
- **Data Validation**: Pydantic
- **Configuration**: TOML
- **Logging**: loguru
- **Async I/O**: aiofiles
- **MCP**: Model Context Protocol SDK

## Architecture

### Core Components

1. **CLI Entry Point** (`src/cli/`)
   - Command registration and routing
   - Commands: chat, list, share, import, bot, mcp, daemon, prompt

2. **Chat System** (`src/chat/`)
   - `ChatApp`: Application assembly
   - `ChatManager`: Core state machine, message processing loop
   - `ChatService`: Business logic, history management
   - `models.py`: Pydantic data models (Chat, Message, ContentPart)

3. **Provider Layer** (`src/chat/provider/`)
   - `BaseProvider`: Abstract interface
   - `OpenAIFormatProvider`: OpenAI format (OpenRouter, DeepSeek, Claude, etc.)
   - `DifyProvider`: Dify Chat-Messages streaming
   - `TopiaOrchProvider`: Topia Orchestrator

4. **Repository Layer** (`src/chat/repository/`)
   - `factory.py`: Repository factory based on config
   - `file.py`: JSONL local file storage
   - `cloudflare_d1.py`: Cloudflare D1 + R2 backup

5. **MCP System**
   - **MCPManager** (`src/mcp_server/mcp_manager.py`): Client-side MCP operations
   - **MCPDaemonServer** (`src/mcp_daemon/`): Persistent daemon managing MCP connections
     - SSEManager: SSE-type MCP servers
     - StdioManager: stdio-type MCP servers
   - **MCPDaemonClient** (`src/daemon_client/`): Unix Socket IPC with connection pool

6. **Configuration Management** (`src/config.py`)
   - Global singleton services: bot_service, mcp_service, prompt_service
   - Platform-specific config paths (macOS/Linux)
   - Proxy settings support

7. **Provider System** (`src/provider/`)
   - `Provider`: Pydantic model for provider configuration
   - `ProviderRepository`: Load providers from TOML config
   - `ProviderService`: Provider selection and model management
   - Supports multiple OpenAI-compatible providers with dynamic model switching

8. **UI Components** (`src/cli/`)
   - `DisplayManager`: Streaming output, Markdown rendering, code highlighting
   - `InputManager`: Multi-line input, history, copy command

## Conventions

### Code Style
- Python PEP 8 compliant
- Async/await for I/O operations
- Type hints using Pydantic models
- Descriptive variable and function names

### File Organization
- Service-Repository pattern for data access
- Provider pattern for API abstraction
- Manager pattern for complex subsystems
- Centralized provider registry with TOML configuration

### Configuration
- **macOS**:
  - Config: `~/Library/Preferences/dq-cli/config.toml`
  - Data: `~/Library/Application Support/dq-cli/`
  - Cache: `~/Library/Caches/dq-cli/`
- **Linux**:
  - Config: `~/.config/dq-cli/config.toml`
  - Data: `~/.local/share/dq-cli/`

### Message Flow
1. User input → InputManager
2. Handle special commands (`/model`, `copy`, `exit`)
3. Create user message → ChatManager.process_user_message()
4. Call provider API → streaming response
5. Display via DisplayManager
6. Check for tool use → MCP execution if needed (recursive)
7. Persist to repository (including model metadata)

### MCP Integration
- Tool confirmation required (unless auto_confirm configured)
- Daemon-based persistent connections
- Unix Socket IPC for client-daemon communication
- Support for both stdio and SSE server types

## Domain Knowledge

### Key Concepts

- **Bot Config**: API configuration (base_url, api_key, model, mcp_servers, etc.)
- **MCP Server**: External tool provider (stdio or SSE connection type)
- **Chat Session**: Conversation with messages, persisted with unique 6-char ID
- **Provider**: OpenAI-compatible API provider with base_url, api_key, and models list
- **Model Switching**: Runtime ability to change models via `/model` command
- **Tool Use**: MCP tool invocation within assistant response, requires execution and result feeding back
- **Streaming Response**: SSE-based real-time token streaming from providers
- **Reasoning Content**: Special handling for models like DeepSeek-R1 that emit reasoning traces

### Storage Types

1. **File Storage** (`storage_type: "file"`)
   - JSONL format for chats, bots, MCP configs, prompts
   - Local filesystem, easy to sync and backup

2. **Cloudflare D1** (`storage_type: "cloudflare_d1"`)
   - Serverless SQL database
   - R2 backup for data durability

### Provider API Formats

- **OpenAI Format**: Most common, supports tool use, cache_control, reasoning_content
- **Dify Format**: Dify-specific streaming chat-messages endpoint
- **Topia Orch**: Custom orchestrator format

## File Paths

### Core Modules
- Entry: `src/cli.py`, `src/cli/__init__.py`
- Chat: `src/chat/chat_manager.py`, `src/chat/app.py`, `src/chat/service.py`
- Providers: `src/chat/provider/openai_format_provider.py`, etc.
- Repositories: `src/chat/repository/file.py`, `src/chat/repository/cloudflare_d1.py`
- MCP: `src/mcp_server/mcp_manager.py`, `src/mcp_daemon/server.py`, `src/daemon_client/main.py`
- Config: `src/config.py`
- Utilities: `src/util.py`

### Configuration Files
- Main config: `~/Library/Preferences/dq-cli/config.toml` (macOS)
- Bot configs: `~/Library/Application Support/dq-cli/bot_config.jsonl`
- MCP configs: `~/Library/Application Support/dq-cli/mcp_config.jsonl`
- Prompt configs: `~/Library/Application Support/dq-cli/prompt_config.jsonl`

## Testing Considerations

- No tests currently exist (noted from codebase scan)
- When adding tests, consider:
  - Mock external API calls (httpx)
  - Mock MCP daemon connections
  - Test file/D1 repository implementations separately
  - Test message flow with fixture data

## Common Patterns

### Async Context Managers
```python
async with AsyncExitStack() as exit_stack:
    # MCP connections, cleanup on exit
```

### Repository Factory
```python
repository = get_chat_repository(config)  # Returns File or D1 based on config
```

### Service Pattern
```python
service = ChatService(repository)
chat = await service.get_chat(chat_id)
```

### Recursive Tool Execution
```python
# Assistant response with tool use → execute tool → feed result back → get new response
await self.process_user_message(tool_result_message)  # Recursive call
```

## References

- Detailed architecture: `codemaps/codemap.md`
- Main specs: `openspec/specs/` (when populated)
