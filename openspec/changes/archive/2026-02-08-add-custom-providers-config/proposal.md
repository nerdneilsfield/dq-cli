# Add Custom Providers Configuration

## Why

Currently, dq-cli only supports provider configurations through individual bot configs. Users need a centralized way to define multiple OpenAI-compatible providers with their models, allowing them to easily switch between providers and models during chat sessions. This enables better organization and reusability of provider configurations.

## What Changes

- Add TOML-based provider configuration support at `~/.config/dq-cli/config.toml`
- Enable defining multiple providers, each with:
  - Provider name and base_url
  - API key
  - List of available models
- Implement `/model` command in chat interface to switch between models dynamically
- Load and validate provider configurations on startup
- Integrate provider configs with existing bot system

## Capabilities

### New Capabilities
- `provider-configuration`: Manage multiple OpenAI-compatible providers via TOML config
- `model-switching`: Switch between models during active chat sessions using `/model` command

### Modified Capabilities
<!-- No existing capabilities are being modified at the requirements level -->

## Impact

- `~/.config/dq-cli/config.toml`: New provider configuration section
- `src/config.py`: Load and parse provider configurations
- `src/chat/chat_manager.py`: Handle `/model` command for model switching
- `src/chat/app.py`: Initialize with provider-based model selection
- New module `src/provider/` (or extend existing structure):
  - `models.py`: Provider and Model data models
  - `repository.py`: Load providers from TOML config
  - `service.py`: Provider selection and validation logic
- `src/cli/commands/chat/chat.py`: Support provider/model selection flags
