"""Tests for MCP daemon models"""

import pytest
from mcp import ClientSession
from unittest.mock import Mock

from src.mcp_daemon.models import SessionState, ServerSession


class TestSessionState:
    """Tests for SessionState enum"""

    def test_session_state_values(self):
        """Test SessionState enum has all required values"""
        assert SessionState.INITIALIZING.value == "initializing"
        assert SessionState.ACTIVE.value == "active"
        assert SessionState.EXPIRED.value == "expired"
        assert SessionState.DISCONNECTED.value == "disconnected"

    def test_session_state_count(self):
        """Test SessionState has exactly 4 states"""
        assert len(list(SessionState)) == 4


class TestServerSession:
    """Tests for ServerSession model"""

    def test_server_session_creation_minimal(self):
        """Test creating ServerSession with minimal parameters"""
        mock_session = Mock(spec=ClientSession)
        server_session = ServerSession(
            session=mock_session,
            transport_type='stdio'
        )

        assert server_session.session == mock_session
        assert server_session.transport_type == 'stdio'
        assert server_session.session_id is None
        assert server_session.last_event_id is None
        assert server_session.endpoint_url is None
        assert server_session.state == SessionState.INITIALIZING

    def test_server_session_creation_with_streamable_http(self):
        """Test creating ServerSession with Streamable HTTP parameters"""
        mock_session = Mock(spec=ClientSession)
        server_session = ServerSession(
            session=mock_session,
            transport_type='streamable-http',
            session_id='test-session-123',
            endpoint_url='https://example.com/mcp'
        )

        assert server_session.session == mock_session
        assert server_session.transport_type == 'streamable-http'
        assert server_session.session_id == 'test-session-123'
        assert server_session.endpoint_url == 'https://example.com/mcp'
        assert server_session.state == SessionState.INITIALIZING

    def test_server_session_last_event_id(self):
        """Test setting and getting last_event_id"""
        mock_session = Mock(spec=ClientSession)
        server_session = ServerSession(
            session=mock_session,
            transport_type='streamable-http'
        )

        assert server_session.last_event_id is None

        server_session.last_event_id = 'event-456'
        assert server_session.last_event_id == 'event-456'

    async def test_server_session_close(self):
        """Test closing a ServerSession"""
        mock_session = Mock(spec=ClientSession)
        server_session = ServerSession(
            session=mock_session,
            transport_type='stdio'
        )

        server_session.state = SessionState.ACTIVE
        await server_session.close()

        assert server_session.state == SessionState.DISCONNECTED

    def test_transport_type_values(self):
        """Test all valid transport types"""
        mock_session = Mock(spec=ClientSession)

        for transport in ['stdio', 'sse', 'legacy-sse', 'streamable-http']:
            session = ServerSession(
                session=mock_session,
                transport_type=transport
            )
            assert session.transport_type == transport
