"""Tests for Streamable HTTP manager"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from contextlib import AsyncExitStack

from src.mcp_daemon.streamable_http import StreamableHTTPManager
from src.mcp_daemon.models import SessionState


class TestStreamableHTTPManager:
    """Tests for StreamableHTTPManager"""

    @pytest.fixture
    def exit_stack(self):
        """Create an AsyncExitStack for testing"""
        return AsyncExitStack()

    @pytest.fixture
    def manager(self, exit_stack):
        """Create a StreamableHTTPManager instance"""
        return StreamableHTTPManager(exit_stack)

    def test_manager_initialization(self, manager):
        """Test StreamableHTTPManager initializes correctly"""
        assert manager.exit_stack is not None
        assert manager.default_timeout is not None
        assert manager.client is None

    def test_is_localhost_true(self, manager):
        """Test _is_localhost recognizes localhost URLs"""
        assert manager._is_localhost('http://localhost:8080/mcp') is True
        assert manager._is_localhost('http://127.0.0.1:8080/mcp') is True
        assert manager._is_localhost('http://[::1]:8080/mcp') is True

    def test_is_localhost_false(self, manager):
        """Test _is_localhost rejects non-localhost URLs"""
        assert manager._is_localhost('https://example.com/mcp') is False
        assert manager._is_localhost('https://api.anthropic.com/mcp') is False
        assert manager._is_localhost('http://192.168.1.1/mcp') is False

    def test_validate_origin_localhost(self, manager):
        """Test _validate_origin for localhost servers"""
        # Should not raise an exception
        manager._validate_origin('http://localhost:8080/mcp')
        manager._validate_origin('http://127.0.0.1:8080/mcp')

    def test_validate_origin_remote(self, manager):
        """Test _validate_origin for remote servers"""
        # Should not raise an exception
        manager._validate_origin('https://example.com/mcp')

    def test_create_http_client_basic(self, manager):
        """Test _create_http_client with basic configuration"""
        client = manager._create_http_client()

        assert client is not None
        assert client.timeout == manager.default_timeout
        assert client.follow_redirects is True

    def test_create_http_client_with_auth_token(self, manager):
        """Test _create_http_client with authentication token"""
        client = manager._create_http_client(auth_token='test-token-123')

        assert 'Authorization' in client.headers
        assert client.headers['Authorization'] == 'Bearer test-token-123'

    def test_create_http_client_with_custom_headers(self, manager):
        """Test _create_http_client with custom headers"""
        custom_headers = {
            'X-Custom-Header': 'custom-value',
            'X-Another-Header': 'another-value'
        }
        client = manager._create_http_client(custom_headers=custom_headers)

        assert 'X-Custom-Header' in client.headers
        assert client.headers['X-Custom-Header'] == 'custom-value'
        assert 'X-Another-Header' in client.headers

    def test_create_http_client_filters_mcp_headers(self, manager):
        """Test _create_http_client filters out MCP-specific headers"""
        custom_headers = {
            'X-Custom-Header': 'custom-value',
            'Mcp-Session-Id': 'should-be-filtered',
            'Accept': 'should-be-filtered',
            'Content-Type': 'should-be-filtered'
        }
        client = manager._create_http_client(custom_headers=custom_headers)

        # Custom header should be included
        assert 'X-Custom-Header' in client.headers
        # MCP headers should NOT be included (lowercase comparison)
        assert 'Mcp-Session-Id' not in client.headers

    @pytest.mark.asyncio
    async def test_connect_validates_origin(self, manager):
        """Test connect validates origin for localhost servers"""
        with patch.object(manager, '_validate_origin') as mock_validate:
            with patch('src.mcp_daemon.streamable_http.streamable_http_client', new_callable=AsyncMock):
                await manager.connect(
                    'test-server',
                    'http://localhost:8080/mcp'
                )

                mock_validate.assert_called_once_with('http://localhost:8080/mcp')

    @pytest.mark.asyncio
    async def test_close_session_updates_state(self, manager):
        """Test close_session updates session state"""
        mock_session = Mock()
        mock_session.session_id = 'test-123'
        mock_session.state = SessionState.ACTIVE

        await manager.close_session(mock_session)

        assert mock_session.state == SessionState.DISCONNECTED


class TestStreamableHTTPManagerIntegration:
    """Integration tests for StreamableHTTPManager with MCP SDK"""

    @pytest.fixture
    async def exit_stack(self):
        """Create and cleanup AsyncExitStack"""
        stack = AsyncExitStack()
        yield stack
        await stack.aclose()

    @pytest.fixture
    def manager(self, exit_stack):
        """Create a StreamableHTTPManager instance"""
        return StreamableHTTPManager(exit_stack)

    @pytest.mark.asyncio
    async def test_connect_creates_http_client(self, manager):
        """Test that connect creates HTTP client with proper configuration"""
        with patch('src.mcp_daemon.streamable_http.streamable_http_client') as mock_client:
            # Mock the async context manager
            mock_client.return_value.__aenter__ = AsyncMock(return_value=(
                AsyncMock(),  # read_stream
                AsyncMock(),  # write_stream
                Mock(return_value=None)  # get_session_id
            ))
            mock_client.return_value.__aexit__ = AsyncMock()

            with patch('src.mcp_daemon.streamable_http.ClientSession') as mock_session_cls:
                mock_session = AsyncMock()
                mock_session.initialize = AsyncMock()
                mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session_cls.return_value.__aexit__ = AsyncMock()

                result = await manager.connect(
                    'test-server',
                    'https://example.com/mcp',
                    auth_token='test-token',
                    custom_headers={'X-Test': 'value'},
                    timeout=60.0
                )

                # Verify streamable_http_client was called
                assert mock_client.called

    @pytest.mark.asyncio
    async def test_connect_handles_http_error(self, manager):
        """Test connect handles HTTP errors gracefully"""
        import httpx

        with patch('src.mcp_daemon.streamable_http.streamable_http_client') as mock_client:
            # Simulate HTTP error
            mock_client.side_effect = httpx.HTTPStatusError(
                'Not Found',
                request=Mock(),
                response=Mock(status_code=404)
            )

            result = await manager.connect(
                'test-server',
                'https://example.com/mcp'
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_connect_handles_general_exception(self, manager):
        """Test connect handles general exceptions gracefully"""
        with patch('src.mcp_daemon.streamable_http.streamable_http_client') as mock_client:
            # Simulate general exception
            mock_client.side_effect = Exception('Connection failed')

            result = await manager.connect(
                'test-server',
                'https://example.com/mcp'
            )

            assert result is None
