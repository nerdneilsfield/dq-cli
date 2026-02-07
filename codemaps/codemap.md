# dq-cli 代码地图 (Codemap)

> 项目概述：dq-cli 是一个命令行 AI 聊天应用，支持多 Bot 配置、MCP (Model Context Protocol) 工具集成、流式响应显示，并提供本地文件和 Cloudflare D1 两种存储方式。

---

## 1. 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     CLI Entry Point                                      │
│                                   (src/cli/__init__.py)                                  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬──────────────┐ │
│  │    chat     │    list     │    share    │   import    │    bot      │     mcp      │ │
│  │   (聊天)    │  (列表)     │  (分享)     │  (导入)     │  (机器人)   │  (MCP服务)   │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴──────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Chat Application                                       │
│                                    (src/chat/app.py)                                     │
│                              ChatApp - 应用程序主控制器                                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
           ┌─────────────────────────────┼─────────────────────────────┐
           │                             │                             │
           ▼                             ▼                             ▼
┌─────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────────┐
│   Chat Manager      │    │     Display Manager     │    │      Input Manager          │
│ (src/chat/chat_     │    │  (src/cli/display_      │    │   (src/cli/input_           │
│     manager.py)     │    │      manager.py)        │    │       manager.py)           │
│                     │    │                         │    │                             │
│ • 消息处理流程控制   │    │ • 实时流式输出显示       │    │ • 用户输入处理              │
│ • 工具调用递归处理   │    │ • 富文本/Markdown渲染   │    │ • 多行输入支持              │
│ • 会话持久化管理     │    │ • 消息面板展示          │    │ • 复制命令处理              │
└──────────┬──────────┘    └─────────────────────────┘    └─────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    Chat Service Layer                                    │
│                                   (src/chat/service.py)                                  │
│                    聊天业务逻辑 - 历史记录管理、分享HTML生成                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  Provider Layer                                          │
│                           (src/chat/provider/)                                           │
│  ┌─────────────────────────────┬─────────────────────────────┬────────────────────────┐ │
│  │   OpenAIFormatProvider      │      DifyProvider           │   TopiaOrchProvider    │ │
│  │  (openai_format_            │    (dify_provider.py)       │  (topia_orch_          │ │
│  │       provider.py)          │                             │     provider.py)       │ │
│  │                             │                             │                        │ │
│  │ • OpenAI API 格式          │ • Dify API 格式            │ • Topia Orch API       │ │
│  │ • 支持 reasoning_content   │                             │                        │ │
│  │ • 支持 cache_control       │                             │                        │ │
│  └─────────────────────────────┴─────────────────────────────┴────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                Repository Layer                                          │
│                          (src/chat/repository/)                                          │
│         ┌────────────────────────┐          ┌────────────────────────┐                  │
│         │    FileRepository      │          │ CloudflareD1Repository │                  │
│         │      (file.py)         │          │   (cloudflare_d1.py)   │                  │
│         │                        │          │                        │                  │
│         │ • 本地 JSONL 存储      │          │ • Cloudflare D1 云端   │                  │
│         │ • 文件系统操作         │          │ • R2 备份同步          │                  │
│         └────────────────────────┘          └────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. MCP 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MCP Client Side                                          │
│                                                                                          │
│   ┌─────────────────────────┐        ┌─────────────────────────────────────────────────┐ │
│   │     MCPManager          │◄───────┤           ChatManager                           │ │
│   │ (src/mcp_server/        │        │     • 初始化时连接 MCP                          │ │
│   │       mcp_manager.py)   │        │     • 处理工具调用请求                          │ │
│   │                         │        │     • 获取系统 Prompt                           │ │
│   │ • 管理 MCP 会话         │        └─────────────────────────────────────────────────┘ │
│   │ • 提取工具调用          │                              │                             │
│   │ • 执行工具              │                              │                             │
│   │ • 格式化系统 Prompt     │                              ▼                             │
│   └───────────┬─────────────┘               ┌─────────────────────────┐                  │
│               │                             │   MCPDaemonClient       │                  │
│               │                             │  (src/daemon_client/    │                  │
│               │                             │          main.py)       │                  │
│               │                             │                         │                  │
│               │                             │ • Unix Socket 连接      │                  │
│               │                             │ • 连接池管理            │                  │
│               │                             │ • 结构化请求/响应       │                  │
│               │                             └───────────┬─────────────┘                  │
│               │                                         │                                │
│               │         ┌───────────────────────────────┘                                │
│               │         │         ▲ (如果 Daemon 未运行，直接连接)                        │
│               │         │         │                                                      │
│               └─────────┼─────────┘                                                      │
│                         │                                                                │
└─────────────────────────┼────────────────────────────────────────────────────────────────┘
                          │ Unix Socket IPC
                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MCP Daemon Side                                          │
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                        MCPDaemonServer                                          │   │
│   │                       (src/mcp_daemon/                                          │   │
│   │                            server.py)                                           │   │
│   │                                                                                 │   │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────────┐  │   │
│   │  │   SSEManager    │  │  StdioManager   │  │      RequestHandler             │  │   │
│   │  │    (sse.py)     │  │   (stdio.py)    │  │       (handlers.py)             │  │   │
│   │  │                 │  │                 │  │                                 │  │   │
│   │  │ • SSE 连接管理  │  │ • 子进程管理    │  │ • 处理 execute_tool             │  │   │
│   │  │ • URL/Token 认证│  │ • stdin/stdout  │  │ • 处理 list_servers             │  │   │
│   │  │                 │  │ • 环境变量注入  │  │ • 处理 list_server_tools        │  │   │
│   │  └────────┬────────┘  └────────┬────────┘  └─────────────────────────────────┘  │   │
│   │           │                    │                                                │   │
│   │           └────────────────────┘                                                │   │
│   │                      │                                                          │   │
│   │                      ▼                                                          │   │
│   │           ┌─────────────────────┐                                               │   │
│   │           │   External MCP      │                                               │   │
│   │           │      Servers        │                                               │   │
│   │           │  • mcp-todo         │                                               │   │
│   │           │  • brave-search     │                                               │   │
│   │           │  • exa-mcp-server   │                                               │   │
│   │           │  • ...              │                                               │   │
│   │           └─────────────────────┘                                               │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 配置管理架构

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              Configuration System                                        │
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                          config.py                                               │   │
│   │                                                                                  │   │
│   │  • 加载 ~/Library/Preferences/dq-cli/config.toml (macOS)                         │   │
│   │  • 加载 ~/.config/dq-cli/config.toml (Linux)                                     │   │
│   │  • 代理设置 (http_proxy/https_proxy)                                            │   │
│   │  • 存储类型配置 (file/cloudflare_d1)                                            │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
                                           │
           ┌───────────────────────────────┼───────────────────────────────┐
           │                               │                               │
           ▼                               ▼                               ▼
   ┌─────────────────┐          ┌─────────────────┐              ┌─────────────────┐
   │   BotService    │          │  McpServerConfig │             │  PromptService  │
   │ (src/bot/       │          │     Service      │             │ (src/prompt/    │
   │  service.py)    │          │ (src/mcp_server/ │             │  service.py)    │
   │                 │          │  service.py)     │             │                 │
   │ • 多 Bot 配置   │          │                  │             │ • 提示词模板    │
   │ • API 配置管理  │          │ • MCP 服务器配置 │             │ • MCP 系统提示  │
   │ • 模型参数      │          │ • 自动确认工具  │             │ • 自定义提示    │
   └────────┬────────┘          └────────┬────────┘             └────────┬────────┘
            │                            │                               │
            ▼                            ▼                               ▼
   ┌─────────────────┐          ┌─────────────────┐              ┌─────────────────┐
   │  BotRepository  │          │ McpServerConfig │              │ PromptRepository│
   │                 │          │   Repository    │              │                 │
   │ • bot_config.   │          │                 │              │ • prompt_config.│
   │     jsonl       │          │ • mcp_config.   │              │     jsonl       │
   └─────────────────┘          │     jsonl       │              └─────────────────┘
                                └─────────────────┘
```

---

## 4. 消息处理流程

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              Message Flow Diagram                                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    User Input
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  ChatManager.run()                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │ 1. 加载历史会话 (如果是继续对话)                                                 │    │
│  │ 2. 初始化 MCP 连接 (如果配置了 mcp_servers)                                      │    │
│  │ 3. 构建系统 Prompt (time_prompt + mcp_prompt + custom_prompts)                  │    │
│  │ 4. 显示历史消息                                                                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                                  │
│                                      ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │ While Loop: 等待用户输入                                                         │    │
│  │                                                                                  │    │
│  │   InputManager.get_input() ──► 处理多行输入 / copy 命令 / exit                   │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                                  │
│                                      ▼                                                  │
│  process_user_message(user_message)  │                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │ 1. 添加用户消息到 messages 列表                                                  │    │
│  │ 2. display_manager.display_message_panel() 显示消息                              │    │
│  │ 3. provider.call_chat_completions() 调用 API                                     │    │
│  │    └─► 流式响应处理 (SSE)                                                        │    │
│  │        └─► display_manager.stream_response() 实时显示                           │    │
│  │ 4. process_assistant_message(assistant_message)                                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                                  │
│                                      ▼                                                  │
│  process_assistant_message()         │                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                                  │    │
│  │   检查是否包含工具调用                                                            │    │
│  │          │                                                                       │    │
│  │    ┌─────┴─────┐                                                                 │    │
│  │    │           │                                                                 │    │
│  │    ▼           ▼                                                                 │    │
│  │   否          是                                                                  │    │
│  │    │           │                                                                 │    │
│  │    │    ┌──────┴─────────────────────────────────────────────────────────┐       │    │
│  │    │    │ 1. 提取工具信息 (server_name, tool_name, arguments)             │       │    │
│  │    │    │ 2. 显示工具调用信息                                            │       │    │
│  │    │    │ 3. get_user_confirmation() 获取用户确认                        │       │    │
│  │    │    │ 4. mcp_manager.execute_tool() 执行工具                         │       │    │
│  │    │    │    └─► MCPDaemonClient.execute_tool_structured()               │       │    │
│  │    │    │ 5. 创建工具结果消息                                            │       │    │
│  │    │    │ 6. ────────┐                                                   │       │    │
│  │    │    │           │ (递归调用)                                          │       │    │
│  │    │    │           ▼                                                   │       │    │
│  │    │    │    process_user_message(tool_result_message)                   │       │    │
│  │    │    │           │                                                   │       │    │
│  │    │    └───────────┘                                                   │       │    │
│  │    │                                                                     │       │    │
│  │    ▼                                                                     │       │    │
│  │  正常显示助手消息                                                         │       │    │
│  │                                                                           │       │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                                  │
│                                      ▼                                                  │
│  persist_chat()                      │                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │ • ChatService.create_chat() 或 update_chat()                                     │    │
│  │ • Repository.add_chat() 或 update_chat()                                         │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                                  │
│                                      ▼                                                  │
│                               等待下一轮输入                                             │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. 核心模块详细说明

### 5.1 CLI 命令模块 (`src/cli/commands/`)

| 命令组 | 文件 | 功能描述 |
|--------|------|----------|
| **init** | `init.py` | 初始化配置目录和默认配置文件 |
| **chat** | `chat/chat.py` | 主聊天入口，创建 ChatApp 实例 |
| | `chat/list.py` | 列出历史聊天记录 |
| | `chat/share.py` | 生成分享 HTML 文件 |
| | `chat/import_chat.py` | 从 OpenRouter 导入聊天记录 |
| **bot** | `bot/add.py` | 添加新的 Bot 配置 |
| | `bot/list.py` | 列出所有 Bot 配置 |
| | `bot/delete.py` | 删除 Bot 配置 |
| **mcp** | `mcp/add.py` | 添加 MCP 服务器配置 (stdio/SSE) |
| | `mcp/list.py` | 列出 MCP 服务器配置 |
| | `mcp/delete.py` | 删除 MCP 服务器配置 |
| **daemon** | `daemon/start.py` | 启动 MCP 守护进程 |
| | `daemon/stop.py` | 停止 MCP 守护进程 |
| | `daemon/status.py` | 检查守护进程状态 |
| | `daemon/log.py` | 查看守护进程日志 |
| | `daemon/restart.py` | 重启守护进程 |
| **prompt** | `prompt/add.py` | 添加自定义提示词 |
| | `prompt/list.py` | 列出提示词配置 |
| | `prompt/delete.py` | 删除提示词配置 |

### 5.2 Chat 核心模块 (`src/chat/`)

| 文件 | 职责 | 关键类/函数 |
|------|------|-------------|
| `app.py` | 应用程序组装 | `ChatApp` - 初始化所有管理器，组合依赖 |
| `chat_manager.py` | 聊天流程控制 | `ChatManager` - 核心状态机，消息处理循环 |
| `service.py` | 业务逻辑 | `ChatService` - 历史记录管理，HTML分享生成 |
| `models.py` | 数据模型 | `Chat`, `Message`, `ContentPart` - Pydantic 模型 |

### 5.3 Provider 模块 (`src/chat/provider/`)

| 文件 | 功能 | 支持的 API |
|------|------|------------|
| `base_provider.py` | 抽象基类 | `BaseProvider` 接口定义 |
| `openai_format_provider.py` | OpenAI 格式 | OpenRouter, DeepSeek, Claude 等 |
| `dify_provider.py` | Dify API | Dify Chat-Messages 流式接口 |
| `topia_orch_provider.py` | Topia API | Topia Orchestrator 接口 |
| `display_manager_mixin.py` | 显示混入 | `DisplayManagerMixin` - 设置 display_manager |

### 5.4 Repository 模块 (`src/chat/repository/`)

| 文件 | 功能 | 存储方式 |
|------|------|----------|
| `factory.py` | 仓库工厂 | `get_chat_repository()` - 根据配置返回对应仓库 |
| `file.py` | 文件存储 | JSONL 格式，本地文件系统 |
| `cloudflare_d1.py` | 数据库存储 | Cloudflare D1 + R2 备份 |
| `cloudflare_d1_util.py` | D1 工具 | SQL 查询构建，数据序列化 |

### 5.5 MCP 系统模块

#### 5.5.1 MCP Manager (`src/mcp_server/mcp_manager.py`)
```python
class MCPManager:
    - check_daemon_running()      # 检查 Daemon 是否运行
    - connect_to_servers()        # 连接配置的 MCP 服务器
    - extract_mcp_tool_use()      # 从响应中提取工具调用
    - execute_tool()              # 通过 Daemon 执行工具
    - get_mcp_prompt()            # 生成 MCP 系统提示词
    - format_server_info()        # 格式化服务器信息
```

#### 5.5.2 MCP Daemon Server (`src/mcp_daemon/`)
```python
class MCPDaemonServer:
    - connect_to_all_servers()    # 启动时连接所有配置的服务器
    - handle_client()             # 处理 IPC 客户端请求
    - start_server()              # 启动 Unix Socket 服务
    
# 子模块:
SSEManager    - 管理 SSE 类型的 MCP 服务器连接
StdioManager  - 管理 stdio 类型的 MCP 服务器连接
RequestHandler - 处理具体的 MCP 请求类型
```

#### 5.5.3 Daemon Client (`src/daemon_client/`)
```python
class MCPDaemonClient:
    - connect()                   # 初始化连接池
    - execute_tool()              # 执行工具（向后兼容）
    - execute_tool_structured()   # 执行工具（结构化响应）
    - list_servers()              # 获取服务器列表
    - list_server_tools()         # 获取工具列表
    - is_daemon_running()         # 静态方法检查 Daemon 状态

class ConnectionPool:
    - 管理多个 Unix Socket 连接
    - 实现连接复用
```

### 5.6 UI 模块 (`src/cli/`)

| 文件 | 功能 | 关键特性 |
|------|------|----------|
| `display_manager.py` | 显示管理 | 流式输出、Markdown 渲染、代码高亮、 reasoning_content 显示 |
| `input_manager.py` | 输入管理 | 多行输入、历史记录、copy 命令 |

---

## 6. 数据流与依赖关系

### 6.1 主要依赖图

```
cli/__init__.py
    ├──► cli/commands/chat/chat.py
    │         └──► chat/app.py
    │               ├──► chat/repository/factory.py
    │               │         ├──► [配置: storage_type]
    │               │         ├──► chat/repository/file.py
    │               │         └──► chat/repository/cloudflare_d1.py
    │               ├──► cli/display_manager.py
    │               ├──► cli/input_manager.py
    │               ├──► mcp_server/mcp_manager.py
    │               │         ├──► daemon_client/main.py (MCPDaemonClient)
    │               │         │         └──► daemon_client/connection_pool.py
    │               │         └──► config.py (mcp_service, prompt_service)
    │               ├──► chat/provider/openai_format_provider.py
    │               │         ├──► chat/provider/base_provider.py
    │               │         └──► chat/provider/display_manager_mixin.py
    │               ├──► chat/chat_manager.py
    │               │         ├──► chat/service.py
    │               │         │         └──► chat/repository/*.py
    │               │         ├──► mcp_server/mcp_manager.py
    │               │         └──► config.py (prompt_service, mcp_service)
    │               └──► bot/service.py (bot_service)
    │
    ├──► cli/commands/bot/*.py ──► bot/service.py
    │                                     └──► bot/repository.py
    │
    ├──► cli/commands/mcp/*.py ──► mcp_server/service.py
    │                                     └──► mcp_server/repository.py
    │
    ├──► cli/commands/prompt/*.py ──► prompt/service.py
    │                                        └──► prompt/repository.py
    │
    └──► cli/commands/daemon/*.py ──► daemon_client/main.py
```

### 6.2 配置依赖关系

```
config.py (全局单例)
    ├──► bot_service = BotService(BotRepository)
    ├──► mcp_service = McpServerConfigService(McpServerConfigRepository)
    └──► prompt_service = PromptService(PromptRepository)
```

---

## 7. 关键执行路径

### 7.1 聊天主循环

```python
# 入口: src/cli/commands/chat/chat.py::chat()
async def chat(chat_id, latest, model, verbose, bot):
    bot_config = bot_service.get_config(bot or "default")
    chat_app = ChatApp(bot_config=bot_config, chat_id=chat_id, verbose=verbose)
    await chat_app.chat()  # -> ChatManager.run()

# 核心循环: src/chat/chat_manager.py::ChatManager.run()
async def run(self):
    async with AsyncExitStack() as exit_stack:
        # 1. 初始化
        if self.continue_exist:
            await self._load_chat(self.chat_id)
        
        # 2. 连接 MCP
        if self.bot_config.mcp_servers:
            await self.mcp_manager.connect_to_servers(self.bot_config.mcp_servers)
            self.system_prompt += await self.mcp_manager.get_mcp_prompt(...)
        
        # 3. 主循环
        while True:
            user_input, is_multi_line, line_count = self.input_manager.get_input()
            if self.input_manager.is_exit_command(user_input):
                break
            
            user_message = create_message("user", user_input)
            await self.process_user_message(user_message)
```

### 7.2 MCP 工具执行流程

```python
# 1. 检测工具调用
# src/chat/chat_manager.py::process_assistant_message()
if contains_tool_use(content):
    plain_content, tool_content = split_content(content)
    mcp_tool = self.mcp_manager.extract_mcp_tool_use(tool_content)
    server_name, tool_name, arguments = mcp_tool

# 2. 用户确认
if not self.get_user_confirmation(tool_content, server_name, tool_name):
    # 用户取消，添加取消消息
    return

# 3. 执行工具
# src/mcp_server/mcp_manager.py::execute_tool()
tool_results = await self.mcp_manager.execute_tool(server_name, tool_name, arguments)
    # -> daemon_client/main.py::execute_tool_structured()
    #    -> _send_request({"type": "execute_tool", ...})

# 4. 递归处理结果
user_message = create_message("user", tool_results, server=server_name, tool=tool_name)
await self.process_user_message(user_message)  # 递归调用
```

### 7.3 Daemon 启动流程

```python
# src/mcp_daemon/main.py::main()
# 1. 确定 socket 路径和日志路径
socket_path = ~/Library/Application Support/dq-cli/mcp_daemon.sock
log_file = ~/Library/Logs/dq-cli/mcp_daemon.log

# 2. 创建并启动服务器
daemon = MCPDaemonServer(socket_path, log_file)
await daemon.start_server()

# 3. 内部启动流程
async def start_server(self):
    # 3.1 清理旧 socket
    if os.path.exists(self.socket_path):
        os.unlink(self.socket_path)
    
    # 3.2 启动 Unix Socket 服务
    self.server = await asyncio.start_unix_server(self.handle_client, self.socket_path)
    os.chmod(self.socket_path, 0o777)
    
    # 3.3 连接所有配置的 MCP 服务器
    await self.connect_to_all_servers()
        for config in mcp_service.get_all_configs():
            if config.url:  # SSE
                session = await self.sse_manager.connect(...)
            else:  # stdio
                session = await self.stdio_manager.connect(...)
```

---

## 8. 文件结构总览

```
src/
├── cli.py                      # 入口文件包装器
├── cli/
│   ├── __init__.py            # CLI 主入口，命令注册
│   ├── __main__.py            # python -m cli 入口
│   ├── display_manager.py     # 显示管理 (Rich)
│   ├── input_manager.py       # 输入管理 (prompt-toolkit)
│   └── commands/
│       ├── init.py            # 初始化命令
│       ├── chat/              # 聊天相关命令
│       ├── bot/               # Bot 配置命令
│       ├── mcp/               # MCP 配置命令
│       ├── daemon/            # Daemon 管理命令
│       └── prompt/            # Prompt 配置命令
├── chat/
│   ├── app.py                 # ChatApp 主应用
│   ├── chat_manager.py        # 聊天流程管理
│   ├── service.py             # 聊天业务逻辑
│   ├── models.py              # 数据模型
│   ├── provider/              # API Provider 实现
│   ├── repository/            # 数据持久化
│   └── utils/                 # 工具函数
├── bot/                       # Bot 配置管理
├── mcp_server/                # MCP 客户端管理
├── mcp_daemon/                # MCP 守护进程
├── daemon_client/             # Daemon 客户端
├── prompt/                    # 提示词管理
├── config.py                  # 全局配置
└── util.py                    # 通用工具
```

---

## 9. 外部依赖

| 库 | 用途 |
|----|------|
| `click` | CLI 框架 |
| `rich` | 终端富文本显示 |
| `prompt-toolkit` | 交互式输入 |
| `httpx` | HTTP 客户端 (API 调用) |
| `mcp` | Model Context Protocol SDK |
| `pydantic` | 数据模型验证 |
| `toml` | 配置文件解析 |
| `loguru` | 日志记录 |
| `aiofiles` | 异步文件操作 |

---

*生成时间: 2026-02-07*
*版本: dq-cli v0.4.0*
