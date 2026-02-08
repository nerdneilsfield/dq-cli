# Provider Configuration for dq-cli

This document explains how to configure and use custom OpenAI-compatible providers in dq-cli.

## Overview

dq-cli supports defining multiple OpenAI-compatible providers in your configuration file. This allows you to:

- Centrally manage multiple AI providers
- Easily switch between providers and models during chat sessions
- Organize models by provider
- Reuse provider configurations across different bot configs

## Configuration Format

Providers are defined in your `config.toml` file using TOML's array of tables syntax.

### Location

- **macOS**: `~/Library/Preferences/dq-cli/config.toml`
- **Linux**: `~/.config/dq-cli/config.toml`

### Basic Example

```toml
[[providers]]
name = "openai"
base_url = "https://api.openai.com/v1"
api_key = "sk-proj-..."
models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"]

[[providers]]
name = "anthropic"
base_url = "https://api.anthropic.com/v1"
api_key = "sk-ant-..."
models = ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"]

[[providers]]
name = "deepseek"
base_url = "https://api.deepseek.com"
api_key = "sk-..."
models = ["deepseek-chat", "deepseek-coder"]
```

## Provider Fields

### Required Fields

- **name** (string): Unique identifier for the provider. Used when switching providers with `/model <provider>/<model>`.

- **base_url** (string): The base URL for the provider's API endpoint. Should typically end with `/v1` for OpenAI-compatible APIs.

- **api_key** (string): Authentication key for the provider's API.

### Optional Fields

- **models** (array of strings): List of model identifiers available from this provider.
  - If empty or omitted, you can still specify any model name manually when switching.
  - Used for validation and listing available models with `/model` command.

## Using Providers

### Switching Models During Chat

Once providers are configured, you can switch models during an active chat session using the `/model` command.

#### List Available Models

```
/model
```

This displays a table of all providers and their models, with the current model highlighted.

#### Switch to Model (Same Provider)

```
/model gpt-4o
```

Switches to a different model from the currently active provider.

#### Switch Provider and Model

```
/model anthropic/claude-3-5-sonnet-20241022
```

Switches both the provider and model. The format is `<provider-name>/<model-name>`.

### Model Validation

- If you specify a model that's **in the provider's models list**, it switches immediately.
- If you specify a model that's **not in the list**, you'll see a warning but the switch still proceeds (the provider may support unlisted models).
- If you specify a **non-existent provider**, you'll see an error and the switch is cancelled.

## Example Workflows

### Using OpenRouter

```toml
[[providers]]
name = "openrouter"
base_url = "https://openrouter.ai/api/v1"
api_key = "sk-or-v1-..."
models = [
  "anthropic/claude-3.7-sonnet",
  "google/gemini-2.0-flash-001",
  "deepseek/deepseek-chat-v3-0324:free",
  "openai/o3-mini"
]
```

In chat:
```
/model openrouter/google/gemini-2.0-flash-001
```

### Using Local LLM Server

```toml
[[providers]]
name = "local"
base_url = "http://localhost:1234/v1"
api_key = "not-needed"
models = ["llama-3.1-8b", "mistral-7b"]
```

### Using Custom Gateway

```toml
[[providers]]
name = "cloudflare-gateway"
base_url = "https://gateway.ai.cloudflare.com/v1/account-id/gateway-id/openai"
api_key = "sk-..."
models = ["gpt-4", "gpt-3.5-turbo"]
```

## Relationship with Bot Configs

- **Providers** are a centralized registry of AI services
- **Bot configs** are usage instances that reference providers or define their own settings
- Switching providers with `/model <provider>/<model>` temporarily overrides the bot's config for the current session only
- Changes made with `/model` are not persisted - next chat session starts with the bot's configured model

## Troubleshooting

### "No providers configured with models"

This message appears when:
- No `[[providers]]` section exists in `config.toml`
- All providers have empty `models` arrays

**Solution**: Add at least one provider with a `models` list to your config file.

### "Provider 'xyz' not found"

You tried to switch to a provider that doesn't exist in your config.

**Solution**:
1. Check provider name spelling
2. Use `/model` without arguments to see available providers
3. Add the provider to your `config.toml` if needed

### Model not working after switch

If a provider doesn't actually support the model you switched to:

**Solution**:
- Check the provider's documentation for supported models
- Update the `models` list in your config to match what the provider supports
- Use `/model` to see what's configured

## Security Notes

- API keys are stored in plain text in `config.toml`
- Recommended file permissions: `chmod 600 ~/.config/dq-cli/config.toml` (Linux)
- Keep your config file out of version control (add to `.gitignore`)

## See Also

- [Main Documentation](../README.md)
- [MCP Daemon](./MCP_DAEMON.md)
- [Cloudflare D1 Storage](./CLOUDFLARE_D1.md)
