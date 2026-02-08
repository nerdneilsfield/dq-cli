# Design: Add Custom Providers Configuration

## Context

Currently, dq-cli manages provider configurations through the bot config system (`BotConfig`), where each bot has its own `base_url`, `api_key`, and `model` settings. This works but has limitations:

- No centralized provider registry
- Model lists are not grouped by provider
- Switching models requires recreating bot configs
- Duplication when multiple bots use the same provider with different models

The existing config system uses TOML at `~/Library/Preferences/dq-cli/config.toml` (macOS) or `~/.config/dq-cli/config.toml` (Linux), managed by `src/config.py`.

## Goals / Non-Goals

**Goals:**
- Add provider configuration to existing TOML config file
- Support multiple providers, each with multiple models
- Enable in-chat model switching via `/model` command
- Preserve existing bot config system (providers augment, don't replace)
- Validate provider configs on load with clear error messages

**Non-Goals:**
- Removing or replacing the existing bot config system
- Auto-discovering models from provider APIs
- Provider-specific authentication beyond API keys (e.g., OAuth)
- UI for editing config file (users edit TOML directly)
- Provider health checks or uptime monitoring

## Decisions

### Decision 1: Extend existing TOML config with `[[providers]]` section

**Approach**: Add a new `[[providers]]` array of tables to the existing `config.toml` file.

**Rationale**:
- Keeps all configuration in one place
- TOML array of tables syntax is clean for repeated structures
- Existing `config.py` already handles TOML parsing with `toml` library

**Alternative considered**: Separate `providers.toml` file
- Rejected: Adds complexity, users have to manage multiple config files

**Example structure**:
```toml
# Existing config...
storage_type = "file"
# ...

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

### Decision 2: Create separate `Provider` models, keep bot config independent

**Approach**:
- New `Provider` and `ProviderModel` data models (Pydantic)
- `ProviderService` to load from config and manage provider list
- Bot configs remain unchanged, can reference providers optionally

**Rationale**:
- Separation of concerns: providers are a registry, bots are usage instances
- Allows bots to use providers or define their own settings
- Future flexibility: bots could reference `provider_name` + `model` instead of full config

**Alternative considered**: Merge providers into bot config
- Rejected: Mixes concerns, harder to support both centralized and per-bot configs

### Decision 3: Implement `/model` command in `ChatManager`

**Approach**:
- Add `/model` to existing command handling in `ChatManager` (similar to `exit`, `copy`)
- Parse syntax: `/model` (list), `/model <name>` (switch), `/model <provider>/<model>` (switch with provider)
- Update `self.model` and `self.bot_config.model` on switch
- Display confirmation to user via `display_manager`

**Rationale**:
- Consistent with existing special command pattern
- Minimal changes to chat flow
- Keeps logic in `ChatManager` where session state lives

**Alternative considered**: Dedicated command system with plugin architecture
- Rejected: Over-engineering for this feature, current pattern works

### Decision 4: Model switching updates bot_config dynamically

**Approach**: When `/model` switches, update `self.bot_config.model` and `self.bot_config.base_url` / `api_key` if provider changes.

**Rationale**:
- Providers use existing `OpenAIFormatProvider` with updated config
- No new provider implementation needed
- Clean separation: config holds settings, provider makes API calls

**Trade-off**:
- Modifying `bot_config` in-place feels mutable, but avoids recreating provider instances
- Session-local change only, doesn't persist to config file

### Decision 5: Store model metadata in chat messages for export

**Approach**: Add `model` field to `Message` model if not already present. Record which model generated each assistant message.

**Rationale**:
- Enables accurate chat export showing model switches
- Supports future features like model comparison
- Minimal schema change (field is optional for backward compat)

**Alternative considered**: Store model switches as system messages
- Rejected: Clutters message history, harder to query

## Risks / Trade-offs

**Risk**: Users specify models not actually supported by provider
→ **Mitigation**: Allow any model name (provider decides), but warn if not in `models` list

**Risk**: Provider API key exposure in config file
→ **Mitigation**: Document file permissions, recommend `chmod 600` on config.toml. Same risk exists for bot configs already.

**Risk**: Breaking change if config.toml format changes unexpectedly
→ **Mitigation**: Use defensive parsing, skip invalid providers, log errors clearly

**Trade-off**: Model list in config is static, doesn't auto-sync with provider
→ **Acceptable**: Users update config manually. Future enhancement: `dq-cli provider sync` command

**Trade-off**: `/model` command can't autocomplete model names (CLI limitation)
→ **Acceptable**: List all models with `/model` command, users copy-paste or type

## Migration Plan

**Deployment**:
1. Add `Provider` models and service in new `src/provider/` module (or reuse existing structure)
2. Extend `config.py` to load `[[providers]]` section
3. Update `ChatManager` to handle `/model` command
4. Update `Message` model to include optional `model` field
5. Test with example config containing multiple providers

**Rollback**:
- If bugs found, users can remove `[[providers]]` section from config
- System gracefully handles missing providers (empty list)
- No database migrations or destructive changes

**User migration**:
- Existing users: No action required, providers are optional
- New users: Can add `[[providers]]` section to config.toml anytime

## Open Questions

- Should `/model` persist across chat sessions (remember last-used model)?
  → **Decision**: No, always start with bot's configured model. Can revisit later.

- Should we validate `base_url` format (e.g., must end with `/v1`)?
  → **Decision**: No strict validation, accept any URL. Provider compatibility is user's responsibility.

- How to handle provider with no `models` list?
  → **Decision**: Treat as "accepts any model name", user provides model manually.
