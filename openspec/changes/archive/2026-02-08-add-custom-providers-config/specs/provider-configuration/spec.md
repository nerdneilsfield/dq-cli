# Provider Configuration Specification

## ADDED Requirements

### Requirement: System SHALL support TOML-based provider configuration

The system SHALL allow users to define multiple OpenAI-compatible providers in a TOML configuration file located at `~/.config/dq-cli/config.toml` (on Linux) or `~/Library/Preferences/dq-cli/config.toml` (on macOS).

#### Scenario: Valid provider configuration loaded

- **WHEN** the system starts and a valid TOML config exists with provider definitions
- **THEN** the system SHALL load all provider configurations
- **AND** each provider SHALL have a name, base_url, api_key, and list of models

#### Scenario: Multiple providers defined

- **WHEN** the config file contains multiple `[[providers]]` entries
- **THEN** the system SHALL load all providers
- **AND** each provider SHALL be accessible by its unique name

#### Scenario: Missing required provider fields

- **WHEN** a provider definition is missing required fields (name, base_url, or api_key)
- **THEN** the system SHALL log a validation error
- **AND** the system SHALL skip that provider and continue loading others

### Requirement: Provider configuration SHALL include model definitions

Each provider configuration SHALL support defining multiple models with their identifiers.

#### Scenario: Provider with multiple models

- **WHEN** a provider configuration includes a `models` array with model identifiers
- **THEN** the system SHALL make all models available for that provider
- **AND** users SHALL be able to select any model from that provider's list

#### Scenario: Provider with no models specified

- **WHEN** a provider configuration has an empty or missing `models` array
- **THEN** the system SHALL treat it as having no predefined models
- **AND** users MAY still specify a model name manually when using that provider

### Requirement: Configuration file SHALL follow TOML array syntax

Provider configurations SHALL use TOML's array of tables syntax (`[[providers]]`).

#### Scenario: TOML config format example

- **WHEN** a user creates a config file with the following structure:
  ```toml
  [[providers]]
  name = "openai"
  base_url = "https://api.openai.com/v1"
  api_key = "sk-..."
  models = ["gpt-4", "gpt-3.5-turbo"]

  [[providers]]
  name = "custom-provider"
  base_url = "https://api.custom.com/v1"
  api_key = "custom-key"
  models = ["model-1", "model-2"]
  ```
- **THEN** the system SHALL parse and load both providers correctly
- **AND** each provider SHALL be independently accessible

### Requirement: System SHALL validate provider configurations on load

The system SHALL validate provider configurations and report errors clearly.

#### Scenario: Invalid TOML syntax

- **WHEN** the config file contains invalid TOML syntax
- **THEN** the system SHALL log a clear error message
- **AND** the system SHALL fall back to empty provider list or fail gracefully

#### Scenario: Duplicate provider names

- **WHEN** multiple providers have the same `name` field
- **THEN** the system SHALL log a warning
- **AND** the system SHALL keep only the last provider with that name
