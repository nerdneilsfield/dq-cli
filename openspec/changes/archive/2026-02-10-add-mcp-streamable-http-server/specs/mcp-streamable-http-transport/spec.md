# mcp-streamable-http-transport Specification

## Purpose

This specification defines the implementation of MCP Streamable HTTP transport as per the Model Context Protocol specification revision 2025-03-26. It enables dq-cli to connect to modern MCP servers using HTTP POST/GET-based message exchange with optional SSE streaming, session management, and resumable connections.

## Requirements

### Requirement: HTTP POST for client-to-server messages

The system SHALL send every JSON-RPC message from client to server as an HTTP POST request to the MCP endpoint.

#### Scenario: Send single request

- **WHEN** the client sends a JSON-RPC request to the server
- **THEN** the system SHALL create an HTTP POST request to the MCP endpoint
- **AND** the request body SHALL contain the JSON-RPC message
- **AND** the Accept header SHALL include both `application/json` and `text/event-stream`

#### Scenario: Send batch requests

- **WHEN** the client sends multiple JSON-RPC requests in a batch
- **THEN** the system SHALL create a single HTTP POST request
- **AND** the request body SHALL contain a JSON array of all requests
- **AND** the Accept header SHALL include both content types

#### Scenario: Send notifications

- **WHEN** the client sends a JSON-RPC notification
- **THEN** the system SHALL create an HTTP POST request
- **AND** the request body SHALL contain the notification
- **AND** the server SHALL respond with HTTP 202 Accepted with no body

#### Scenario: Send responses

- **WHEN** the client sends a JSON-RPC response to a server request
- **THEN** the system SHALL create an HTTP POST request
- **AND** the request body SHALL contain the response
- **AND** the server SHALL respond with HTTP 202 Accepted with no body

### Requirement: Handle single JSON and SSE stream responses

The system SHALL support both single JSON responses and Server-Sent Events streaming responses from the server.

#### Scenario: Receive single JSON response

- **WHEN** the server returns Content-Type `application/json`
- **THEN** the system SHALL parse the response body as a single JSON-RPC response
- **AND** the system SHALL return the response to the caller

#### Scenario: Receive SSE stream response

- **WHEN** the server returns Content-Type `text/event-stream`
- **THEN** the system SHALL open an SSE stream parser
- **AND** the system SHALL process events as they arrive
- **AND** each event data SHALL be parsed as JSON-RPC message(s)

#### Scenario: Server sends multiple responses in SSE stream

- **WHEN** receiving an SSE stream with multiple JSON-RPC responses
- **THEN** the system SHALL deliver each response to the corresponding request caller
- **AND** the system SHALL maintain request-response correlation via JSON-RPC id field

#### Scenario: Server sends requests before responses in SSE stream

- **WHEN** the server sends JSON-RPC requests in the SSE stream before sending responses
- **THEN** the system SHALL process the server requests
- **AND** the system SHALL send responses to server requests via new HTTP POST
- **AND** the system SHALL continue waiting for the original client request responses

### Requirement: Session management with Mcp-Session-Id header

The system SHALL support stateful sessions using the Mcp-Session-Id header.

#### Scenario: Initialize session and receive session ID

- **WHEN** the client sends an InitializeRequest
- **THEN** the system SHALL send HTTP POST with the request
- **AND** if the server response includes an Mcp-Session-Id header, the system SHALL store the session ID
- **AND** the system SHALL associate the session ID with this server connection

#### Scenario: Include session ID in subsequent requests

- **WHEN** the client sends requests after initialization with a session ID
- **THEN** the system SHALL include the Mcp-Session-Id header in all HTTP requests
- **AND** the header value SHALL be the stored session ID

#### Scenario: Handle session expiration

- **WHEN** the server responds with HTTP 404 to a request with a session ID
- **THEN** the system SHALL detect session expiration
- **AND** the system SHALL reinitialize by sending a new InitializeRequest without session ID
- **AND** the system SHALL obtain a new session ID
- **AND** the system SHALL retry the original request with the new session

#### Scenario: Terminate session on disconnect

- **WHEN** the client disconnects or the daemon shuts down
- **THEN** the system SHALL send HTTP DELETE to the MCP endpoint with the Mcp-Session-Id header
- **AND** if the server responds with HTTP 405, the system SHALL accept that sessions cannot be terminated
- **AND** the system SHALL clean up local session state

### Requirement: HTTP GET for server-to-client message stream

The system SHALL support HTTP GET to open an SSE stream for receiving server-initiated messages.

#### Scenario: Open server notification stream

- **WHEN** the client connects to a Streamable HTTP server
- **THEN** the system MAY send HTTP GET to the MCP endpoint
- **AND** the request SHALL include Accept header with `text/event-stream`
- **AND** the request SHALL include Mcp-Session-Id header if session exists

#### Scenario: Receive server-initiated requests

- **WHEN** the server sends JSON-RPC requests on the GET SSE stream
- **THEN** the system SHALL process the requests
- **AND** the system SHALL send responses via HTTP POST
- **AND** the responses SHALL include the Mcp-Session-Id header

#### Scenario: Server does not support GET endpoint

- **WHEN** the client sends HTTP GET and receives HTTP 405 Method Not Allowed
- **THEN** the system SHALL accept that server does not offer GET endpoint
- **AND** the system SHALL rely solely on POST request SSE streams for bidirectional communication

### Requirement: Resumable connections with Last-Event-ID

The system SHALL support resuming SSE streams after disconnection using event IDs.

#### Scenario: Server assigns event IDs to SSE events

- **WHEN** receiving SSE events with id field
- **THEN** the system SHALL track the last event ID received per stream
- **AND** the system SHALL store the event ID in the session state

#### Scenario: Resume broken connection

- **WHEN** an SSE stream disconnects before completing
- **AND** the last event ID is known
- **THEN** the system SHALL send a new HTTP request (POST or GET) to resume
- **AND** the request SHALL include Last-Event-ID header with the last received event ID
- **AND** the server MAY replay messages after the last event ID

#### Scenario: Server replays missed messages

- **WHEN** resuming with Last-Event-ID header
- **THEN** the system SHALL receive events that would have been sent after the last event
- **AND** the system SHALL process replayed events normally
- **AND** the system SHALL continue with new events after replay completes

#### Scenario: Server does not support resumability

- **WHEN** the server does not assign event IDs to SSE events
- **THEN** the system SHALL treat streams as non-resumable
- **AND** on disconnection, the system SHALL restart the request from the beginning if needed

### Requirement: Multiple concurrent SSE streams

The system SHALL support multiple concurrent SSE streams per session.

#### Scenario: Parallel client requests with separate streams

- **WHEN** the client sends multiple requests in parallel
- **THEN** the system MAY create separate HTTP POST requests for each
- **AND** each request MAY open its own SSE stream
- **AND** the system SHALL route responses correctly using JSON-RPC id correlation

#### Scenario: Concurrent POST stream and GET stream

- **WHEN** a POST request opens an SSE stream
- **AND** a GET request opens a concurrent SSE stream
- **THEN** the system SHALL maintain both streams
- **AND** server messages SHALL appear on only one stream (no duplication)
- **AND** the system SHALL process messages from both streams

#### Scenario: Avoid message duplication across streams

- **WHEN** multiple SSE streams are open for the same session
- **THEN** each server message SHALL be delivered on exactly one stream
- **AND** the system SHALL not process duplicate messages

### Requirement: Origin validation for local servers

The system SHALL validate Origin headers to prevent DNS rebinding attacks on local servers.

#### Scenario: Local server connection

- **WHEN** connecting to a server on localhost (127.0.0.1 or ::1)
- **THEN** the system SHALL validate the Origin header on all HTTP requests
- **AND** the system SHALL reject requests with unexpected origins
- **AND** the system SHALL only accept origins matching the expected local application

#### Scenario: Remote HTTPS server connection

- **WHEN** connecting to a remote server via HTTPS
- **THEN** the system SHALL NOT perform Origin validation
- **AND** the system SHALL rely on the server's CORS and authentication mechanisms

#### Scenario: Reject malicious origin on local server

- **WHEN** a request to a local server has an unexpected Origin
- **THEN** the system SHALL reject the connection
- **AND** the system SHALL log the security violation

### Requirement: Error handling for HTTP failures

The system SHALL handle HTTP errors gracefully and provide meaningful diagnostics.

#### Scenario: HTTP 400 Bad Request

- **WHEN** the server responds with HTTP 400
- **THEN** the system SHALL parse the response body for a JSON-RPC error
- **AND** the system SHALL return the error to the caller
- **AND** the system SHALL log the malformed request details

#### Scenario: HTTP 404 Not Found on non-session request

- **WHEN** the server responds with HTTP 404 and no session ID was sent
- **THEN** the system SHALL treat it as a connection error
- **AND** the system SHALL report the endpoint does not exist

#### Scenario: Network failure during request

- **WHEN** a network error occurs during an HTTP request
- **THEN** the system SHALL detect the failure
- **AND** the system SHALL attempt to reconnect if resumability is supported
- **AND** the system SHALL report the failure if reconnection fails

#### Scenario: SSE stream disconnects prematurely

- **WHEN** an SSE stream closes before sending all expected responses
- **THEN** the system SHALL attempt to resume using Last-Event-ID if available
- **AND** if resumption fails, the system SHALL report incomplete response error

### Requirement: Header management

The system SHALL correctly manage HTTP headers for all Streamable HTTP interactions.

#### Scenario: Set Accept header on all requests

- **WHEN** sending any HTTP POST or GET request
- **THEN** the system SHALL include an Accept header
- **AND** for POST with requests, Accept SHALL include `application/json, text/event-stream`
- **AND** for GET, Accept SHALL include `text/event-stream`

#### Scenario: Set Content-Type for POST requests

- **WHEN** sending HTTP POST with JSON-RPC message(s)
- **THEN** the system SHALL set Content-Type header to `application/json`
- **AND** the request body SHALL be valid JSON

#### Scenario: Include authentication headers

- **WHEN** the server configuration includes an auth token
- **THEN** the system SHALL include Authorization header with the token
- **AND** the header SHALL be sent on all HTTP requests to that server

#### Scenario: Preserve custom headers from configuration

- **WHEN** the server configuration specifies custom headers
- **THEN** the system SHALL include those headers in all HTTP requests
- **AND** custom headers SHALL not override required MCP headers
