# Implementation Tasks

## 1. Create Provider Data Models

- [x] 1.1 Create `src/provider/models.py` with `Provider` Pydantic model
- [x] 1.2 Add fields: name, base_url, api_key, models (list of strings)
- [x] 1.3 Add validation for required fields (name, base_url, api_key)
- [x] 1.4 Create `src/provider/__init__.py` to export models

## 2. Implement Provider Configuration Loading

- [x] 2.1 Create `src/provider/repository.py` with `ProviderRepository` class
- [x] 2.2 Implement `load_providers()` method to read from TOML config
- [x] 2.3 Parse `[[providers]]` array from config using toml library
- [x] 2.4 Handle missing providers section gracefully (return empty list)
- [x] 2.5 Add error handling for invalid TOML syntax with clear error messages
- [x] 2.6 Add warning for duplicate provider names (keep last one)

## 3. Create Provider Service Layer

- [x] 3.1 Create `src/provider/service.py` with `ProviderService` class
- [x] 3.2 Implement `get_all_providers()` method
- [x] 3.3 Implement `get_provider(name)` method to find by name
- [x] 3.4 Implement `get_model_from_provider(provider_name, model_name)` method
- [x] 3.5 Implement `list_all_models()` method returning provider/model pairs

## 4. Integrate Provider Loading in Config

- [x] 4.1 Update `src/config.py` to import and initialize `ProviderService`
- [x] 4.2 Create global `provider_service` instance (similar to bot_service)
- [x] 4.3 Load providers during config initialization
- [x] 4.4 Add provider_service to module exports

## 5. Add Model Field to Message Model

- [x] 5.1 Update `src/chat/models.py` Message model
- [x] 5.2 Add optional `model: Optional[str]` field to Message
- [x] 5.3 Update `create_message()` helper to accept model parameter
- [x] 5.4 Test backward compatibility with existing messages without model field

## 6. Implement /model Command in ChatManager

- [x] 6.1 Update `src/chat/chat_manager.py` to import provider_service
- [x] 6.2 Add `/model` command detection in input handling loop
- [x] 6.3 Implement `/model` (no args) - list all available models
- [x] 6.4 Display current active model highlighted in the list
- [x] 6.5 Implement `/model <model-name>` - switch to model from current provider
- [x] 6.6 Implement `/model <provider>/<model>` - switch provider and model
- [x] 6.7 Update `self.model` and `self.bot_config.model` on successful switch
- [x] 6.8 Update `self.bot_config.base_url` and `api_key` when provider changes
- [x] 6.9 Display confirmation message via display_manager
- [x] 6.10 Display error message for invalid model/provider names

## 7. Update Message Creation to Track Model

- [x] 7.1 Update assistant message creation to include current model
- [x] 7.2 Store model info when processing API responses
- [x] 7.3 Ensure model field is persisted to repository

## 8. Update Documentation

- [x] 8.1 Add provider configuration example to README.md
- [x] 8.2 Create docs/PROVIDER_CONFIGURATION.md with TOML format guide
- [x] 8.3 Document `/model` command usage in README or docs
- [x] 8.4 Update openspec/project.md with provider system context

## 9. Testing and Validation

- [x] 9.1 Create example config.toml with multiple providers
- [x] 9.2 Test loading providers from config
- [x] 9.3 Test `/model` command with valid model names
- [x] 9.4 Test `/model` command with provider/model syntax
- [x] 9.5 Test error handling for invalid provider/model names
- [x] 9.6 Test model switching preserves conversation context
- [x] 9.7 Verify model field appears in exported chat data
