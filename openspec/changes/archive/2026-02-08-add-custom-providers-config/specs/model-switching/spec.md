# Model Switching Specification

## ADDED Requirements

### Requirement: Chat interface SHALL support /model command

The chat interface SHALL provide a `/model` command that allows users to switch the active model during a chat session.

#### Scenario: Switch to a different model

- **WHEN** a user types `/model <model-name>` in the chat interface
- **THEN** the system SHALL switch the active model to the specified model
- **AND** subsequent messages SHALL use the new model
- **AND** the system SHALL display a confirmation message

#### Scenario: Switch to model from different provider

- **WHEN** a user types `/model <provider-name>/<model-name>`
- **THEN** the system SHALL switch to the specified provider and model
- **AND** the system SHALL use the new provider's base_url and api_key
- **AND** subsequent messages SHALL use the new provider and model

#### Scenario: List available models

- **WHEN** a user types `/model` without arguments
- **THEN** the system SHALL display a list of all available models from all providers
- **AND** the list SHALL show provider names and model names
- **AND** the current active model SHALL be highlighted or marked

#### Scenario: Invalid model name

- **WHEN** a user specifies a model that doesn't exist in any provider
- **THEN** the system SHALL display an error message
- **AND** the active model SHALL remain unchanged

### Requirement: Model switching SHALL preserve conversation context

When switching models during a chat session, the conversation history SHALL be maintained.

#### Scenario: Switch model mid-conversation

- **WHEN** a user switches models after several messages
- **THEN** the conversation history SHALL be preserved
- **AND** the new model SHALL receive the full conversation context
- **AND** the chat SHALL continue seamlessly with the new model

### Requirement: System SHALL validate model availability

Before switching models, the system SHALL verify the model is available.

#### Scenario: Model exists in provider configuration

- **WHEN** a user requests a model listed in a provider's `models` array
- **THEN** the system SHALL allow the switch

#### Scenario: Model not in provider configuration but provider allows it

- **WHEN** a user requests a model not listed in the provider's `models` array
- **THEN** the system SHALL allow the switch with a warning
- **AND** the warning SHALL inform the user the model may not be supported

### Requirement: Model switching SHALL update session metadata

When a model is switched, the system SHALL update the current session's metadata.

#### Scenario: Track model changes in session

- **WHEN** a user switches models during a chat
- **THEN** the system SHALL record the model change
- **AND** the chat history SHALL reflect which model was used for each message
- **AND** exported chat data SHALL include model information per message
