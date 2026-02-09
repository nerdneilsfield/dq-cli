# model-switching Specification (Delta)

## MODIFIED Requirements

### Requirement: System SHALL validate model availability

Before switching models, the system SHALL verify the model is available across all transport types.

#### Scenario: Model exists in provider configuration

- **WHEN** a user requests a model listed in a provider's `models` array
- **THEN** the system SHALL allow the switch

#### Scenario: Model not in provider configuration but provider allows it

- **WHEN** a user requests a model not listed in the provider's `models` array
- **THEN** the system SHALL allow the switch with a warning
- **AND** the warning SHALL inform the user the model may not be supported

#### Scenario: Validate model availability across transport types

- **WHEN** switching to a model from a provider using Streamable HTTP transport
- **THEN** the system SHALL verify the Streamable HTTP connection is active
- **AND** if the connection is not active, the system SHALL attempt to reconnect
- **AND** if reconnection fails, the system SHALL report the model is unavailable

#### Scenario: Preserve session when switching models with Streamable HTTP

- **WHEN** switching models within the same MCP server session
- **AND** the server uses Streamable HTTP transport with session management
- **THEN** the system SHALL preserve the Mcp-Session-Id
- **AND** the system SHALL continue using the existing session
- **AND** the system SHALL not reinitialize the MCP connection

## ADDED Requirements

### Requirement: Model switching SHALL support all transport types

The system SHALL allow model switching for providers using any supported transport type (stdio, legacy SSE, or Streamable HTTP).

#### Scenario: Switch to model using stdio transport

- **WHEN** a user switches to a model from a provider using stdio transport
- **THEN** the system SHALL use the existing stdio connection
- **AND** the model switch SHALL complete successfully

#### Scenario: Switch to model using Streamable HTTP transport

- **WHEN** a user switches to a model from a provider using Streamable HTTP transport
- **THEN** the system SHALL use the existing Streamable HTTP connection
- **AND** the system SHALL include the Mcp-Session-Id if available
- **AND** the model switch SHALL complete successfully

#### Scenario: Switch to model using legacy SSE transport

- **WHEN** a user switches to a model from a provider using legacy HTTP+SSE transport
- **THEN** the system SHALL use the existing SSE connection
- **AND** the model switch SHALL complete successfully

#### Scenario: Handle transport reconnection during model switch

- **WHEN** switching to a model from a provider whose transport is disconnected
- **THEN** the system SHALL attempt to reconnect using the appropriate transport
- **AND** if using Streamable HTTP, the system SHALL establish a new session
- **AND** if reconnection succeeds, the model switch SHALL proceed
- **AND** if reconnection fails, the system SHALL report the error and keep the current model
