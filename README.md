# dq-cli 🚀

A tiny command-line interface chat application that brings AI conversations to your terminal.

Check out [y-gui](https://github.com/luohy15/y-gui) for a web-based version of dq-cli.

## ✨ Features

- 📝 Flexible storage options:
  - Local JSONL files for easy access and sync
  - Cloudflare D1 for cloud storage
- 💬 Interactive chat interface with tool execution visualization
- 🤖 Support for multiple bot configurations (any base_url/api_key/model combination). Supported api format type:
  - [OpenAI chat completion streaming format](https://platform.openai.com/docs/api-reference/chat/streaming)
  - [Dify chat-messages streaming format](https://docs.dify.ai/guides/application-publishing/developing-with-apis)
- 🤔 Support for reasoning model
  - [Deepseek-r1 reasoning_content](https://api-docs.deepseek.com/guides/reasoning_model) output print
  - [OpenAI o3-mini reasoning_effort](https://platform.openai.com/docs/guides/reasoning) configuration 
- 🔗 MCP (Model Context Protocol) integration:
  - Client support with multiple transport types:
    - **Streamable HTTP** (modern, recommended - MCP 2025-03-26 spec)
    - stdio (traditional subprocess-based)
    - Legacy SSE (deprecated, for compatibility)
  - Automatic transport detection with caching
  - Session management and resumable connections
  - Persistent daemon
  - Custom prompt configurations
- 🧐 Simple "Deep Research" mode by prompt configuration
  - [Demo](https://cdn.luohy15.com/chat/660831.html)

## Demo

![demo](.github/visuals/demo.png)

![demo](.github/visuals/demo.gif)

[asciicast](https://asciinema.org/a/709735)

### Multiple bot configurations
```
➜  ~ dq-cli bot list
Name         API Key      API Type    Base URL                             Model                                Print Speed    Description    OpenRouter Config    MCP Servers    Reasoning Effort
-----------  -----------  ----------  -----------------------------------  -----------------------------------  -------------  -------------  -------------------  -------------  ------------------
default      sk-or-v1...  N/A         https://gateway.ai.cloudflare.co...  google/gemini-2.0-flash-001          None            N/A            Yes                  No             N/A
claude       sk-or-v1...  N/A         https://gateway.ai.cloudflare.co...  anthropic/claude-3.7-sonnet:beta     None             N/A            Yes                  todo           N/A
o3-mini      sk-or-v1...  N/A         https://gateway.ai.cloudflare.co...  openai/o3-mini                       None             N/A            Yes                  No             low
ds-chat        sk-or-v1...  N/A         https://gateway.ai.cloudflare.co...  deepseek/deepseek-chat-v3-0324:free                 None            N/A            Yes                  tavily         N/A
dify-bot     app-2drF...  dify        https://api.dify.ai/v1                                                    None             N/A            No                   No             N/A
```

### Multiple MCP servers

Supports modern **Streamable HTTP** transport alongside traditional stdio and legacy SSE:

```
➜  ~ dq-cli mcp list
Name              Type              Command/URL          Arguments/Token    Environment     Auto-Confirm
----------------  ----------------  -------------------  -----------------  --------------  --------------
anthropic-mcp     streamable-http   https://api.anth...   sk-ant-xxxxx                       safe_tools...
brave-search      legacy-sse        https://router.m...                                      brave_web_s...
todo              stdio             uvx                  mcp-todo
exa-mcp-server    stdio             npx                  exa-mcp-server     EXA_API_KEY...
```

**Add Streamable HTTP server** (auto-detects transport):
```bash
dq-cli mcp add my-server --url https://api.example.com/mcp --token your-token
```

**With custom headers and timeout**:
```bash
dq-cli mcp add my-server \
  --url https://api.example.com/mcp \
  --token your-token \
  --transport streamable-http \
  --timeout 60 \
  --header "X-API-Key: key123"
```

See [MCP Streamable HTTP Guide](docs/MCP_STREAMABLE_HTTP.md) for detailed documentation.

## ⚡ Quick Start

### Prerequisites

Required:
1. uv
2. OpenRouter API key

Setup Instructions:
1. **uv**
   - Follow the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/)
   - uv will automatically manage Python installation

2. **OpenRouter API key**
   - Visit [OpenRouter Settings](https://openrouter.ai/settings/keys)
   - Create a new API key
   - Save it for the initialization step

### Run without Installation
```bash
uvx dq-cli
```

### Install with uv tool
```bash
uv tool install dq-cli
```

### Initialize
```bash
dq-cli init
```

### Start Chat
```bash
dq-cli chat
```

### Configure Custom Providers (Optional)

Add OpenAI-compatible providers to your `config.toml`:

```toml
[[providers]]
name = "openai"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."
models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]

[[providers]]
name = "deepseek"
base_url = "https://api.deepseek.com"
api_key = "sk-..."
models = ["deepseek-chat", "deepseek-coder"]
```

Switch models during chat:
- `/model` - List all available models
- `/model gpt-4` - Switch to a different model
- `/model deepseek/deepseek-chat` - Switch provider and model

## 🛠️ Usage

```bash
dq-cli [OPTIONS] COMMAND [ARGS]...
```

### Commands
- `chat`   Start a new chat conversation or continue an existing one
- `list`   List chat conversations with optional filtering
- `share`  Share a chat conversation by generating a shareable link
- `import` Import chats from an external file (useful for storage migration)
- `bot`    Manage bot configurations:
  - `add`     Add a new bot configuration
  - `list`    List all configured bots
  - `delete`  Delete a bot configuration
- `mcp`    Manage MCP server configurations:
  - `add`     Add a new MCP server (supports stdio, SSE, and Streamable HTTP)
    - Options: `--url`, `--token`, `--transport`, `--timeout`, `--header`
  - `list`    List all configured MCP servers with transport types
  - `delete`  Delete an MCP server configuration
- `daemon`  Manage the MCP daemon:
  - `start`    Start the MCP daemon
  - `stop`     Stop the MCP daemon
  - `status`   Check daemon status
  - `log`      View daemon logs
  - `restart`  Restart the daemon
- `prompt` Manage prompt configurations:
  - `add`     Add a new prompt configuration
  - `list`    List all configured prompts
  - `delete`  Delete a prompt configuration

### Options
- `--help`  Show help message and exit

## 📚 Documentation

### MCP Streamable HTTP Transport

dq-cli supports the modern **MCP Streamable HTTP** transport (MCP spec 2025-03-26):

- ✅ **True bidirectional communication** - Servers can initiate requests
- ✅ **Session management** - Persistent sessions with automatic reconnection
- ✅ **Resumable connections** - Recover from network failures
- ✅ **Better security** - Origin validation, enhanced authentication
- ✅ **Automatic transport detection** - Tries Streamable HTTP first, falls back to legacy SSE

**Quick Start:**
```bash
# Add a Streamable HTTP server (auto-detects transport)
dq-cli mcp add my-server --url https://api.example.com/mcp --token sk-xxxxx

# Start daemon (establishes connections)
dq-cli daemon start

# Use in chat
dq-cli chat -b claude  # If claude bot has MCP servers configured
```

**Documentation:**
- [MCP Streamable HTTP Guide](docs/MCP_STREAMABLE_HTTP.md) - Complete user guide
- [Configuration Examples](docs/MCP_CONFIGURATION_EXAMPLES.md) - Real-world examples
- [Troubleshooting](docs/TROUBLESHOOTING_MCP.md) - Common issues and solutions

**Additional Resources:**
- [deepwiki page](https://deepwiki.com/luohy15/dq-cli) - Comprehensive project documentation
- [MCP Specification](https://modelcontextprotocol.io/) - Official MCP documentation
