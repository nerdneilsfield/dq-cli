# mcp-transport-detection Specification

## Purpose

This specification defines the automatic detection and selection of the appropriate MCP transport protocol (Streamable HTTP vs legacy HTTP+SSE) when connecting to MCP servers. This enables seamless backward compatibility while preferring modern transport protocols.

## Requirements

### Requirement: Auto-detect transport type on connection

The system SHALL automatically detect which transport protocol a server supports.

#### Scenario: Detect Streamable HTTP server

- **WHEN** connecting to a new MCP server via URL
- **THEN** the system SHALL attempt to POST an InitializeRequest to the URL
- **AND** the system SHALL include Accept header with `application/json, text/event-stream`
- **AND** if the server responds with success (2xx), the system SHALL identify it as Streamable HTTP transport

#### Scenario: Detect legacy HTTP+SSE server

- **WHEN** the initial POST receives HTTP 4xx error (405 or 404)
- **THEN** the system SHALL attempt HTTP GET to the URL
- **AND** the system SHALL expect Content-Type `text/event-stream`
- **AND** if the first SSE event is named "endpoint", the system SHALL identify it as legacy HTTP+SSE transport
- **AND** the system SHALL extract the endpoint URL from the event data

#### Scenario: Connection failure for unsupported server

- **WHEN** both Streamable HTTP POST and legacy SSE GET fail
- **THEN** the system SHALL report connection failure
- **AND** the error message SHALL indicate which attempts were made
- **AND** the system SHALL log diagnostic information about the failures

### Requirement: Cache detected transport type

The system SHALL cache the detected transport type to avoid repeated detection on reconnection.

#### Scenario: Store transport type in configuration

- **WHEN** transport detection succeeds for a server
- **THEN** the system SHALL store the detected transport type
- **AND** the transport type SHALL be persisted in the server configuration
- **AND** the stored value SHALL be one of: `streamable-http`, `legacy-sse`, or `stdio`

#### Scenario: Use cached transport on reconnection

- **WHEN** reconnecting to a server with known transport type
- **THEN** the system SHALL skip detection
- **AND** the system SHALL directly use the cached transport type
- **AND** if connection fails, the system MAY retry detection

#### Scenario: Manual transport override

- **WHEN** the user explicitly configures a transport type for a server
- **THEN** the system SHALL use the configured transport
- **AND** the system SHALL NOT perform auto-detection
- **AND** if the configured transport fails, the system SHALL report an error without fallback

### Requirement: Prefer Streamable HTTP over legacy transports

The system SHALL prefer modern Streamable HTTP transport when available.

#### Scenario: Server supports both transports

- **WHEN** a server supports both Streamable HTTP and legacy HTTP+SSE
- **THEN** the detection algorithm SHALL identify it as Streamable HTTP
- **AND** the system SHALL use Streamable HTTP for all connections

#### Scenario: Graceful degradation to legacy

- **WHEN** Streamable HTTP detection fails
- **THEN** the system SHALL automatically attempt legacy HTTP+SSE detection
- **AND** the user SHALL not need to reconfigure
- **AND** the system SHALL log which transport was selected

### Requirement: Report transport capabilities

The system SHALL inform users about detected transport capabilities.

#### Scenario: Log transport detection result

- **WHEN** transport detection completes successfully
- **THEN** the system SHALL log the detected transport type
- **AND** the log message SHALL include the server name and transport
- **AND** for Streamable HTTP, the log SHALL note if session management is supported

#### Scenario: Display transport in server list

- **WHEN** the user lists configured MCP servers
- **THEN** the system SHALL display the transport type for each server
- **AND** the display SHALL show `streamable-http`, `legacy-sse`, or `stdio`

#### Scenario: Warning for legacy transport

- **WHEN** a server is detected as legacy HTTP+SSE
- **THEN** the system SHALL log a warning that the transport is deprecated
- **AND** the warning SHALL recommend upgrading the server to Streamable HTTP
- **AND** the connection SHALL proceed normally despite the warning

### Requirement: Handle detection edge cases

The system SHALL handle ambiguous or error cases during detection.

#### Scenario: Server responds with unexpected status

- **WHEN** the initial POST returns a 3xx redirect
- **THEN** the system SHALL follow the redirect up to a configured limit
- **AND** the system SHALL retry detection at the redirected URL

#### Scenario: Server returns HTML instead of JSON

- **WHEN** a POST or GET request returns Content-Type `text/html`
- **THEN** the system SHALL treat it as an invalid MCP server
- **AND** the error message SHALL indicate the server is not MCP-compatible
- **AND** the system SHALL include the response content type in the error

#### Scenario: Timeout during detection

- **WHEN** a detection request times out
- **THEN** the system SHALL retry up to a configured maximum
- **AND** if all retries fail, the system SHALL report connection timeout
- **AND** the system SHALL suggest checking network connectivity and server URL

#### Scenario: Server requires authentication

- **WHEN** the server responds with HTTP 401 Unauthorized during detection
- **THEN** the system SHALL check if authentication credentials are configured
- **AND** if credentials exist, the system SHALL retry with authentication headers
- **AND** if credentials are missing, the system SHALL report authentication required

### Requirement: Support stdio transport without detection

The system SHALL directly use stdio transport for subprocess-based servers without attempting HTTP detection.

#### Scenario: Server configured with command

- **WHEN** an MCP server configuration includes a `command` field
- **THEN** the system SHALL identify the transport as stdio
- **AND** the system SHALL NOT attempt HTTP-based detection
- **AND** the system SHALL launch the subprocess with the configured command and arguments

#### Scenario: Stdio transport in server list

- **WHEN** displaying a server using stdio transport
- **THEN** the system SHALL show transport type as `stdio`
- **AND** the display SHALL include the command being executed
