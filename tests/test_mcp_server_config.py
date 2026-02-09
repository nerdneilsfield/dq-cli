"""Tests for MCP server configuration models"""

import pytest
from src.mcp_server.models import McpServerConfig


class TestMcpServerConfig:
    """Tests for McpServerConfig model"""

    def test_config_creation_minimal_stdio(self):
        """Test creating minimal stdio server config"""
        config = McpServerConfig(
            name='test-server',
            command='node',
            args=['server.js']
        )

        assert config.name == 'test-server'
        assert config.command == 'node'
        assert config.args == ['server.js']
        assert config.env == {}
        assert config.url is None
        assert config.token is None
        assert config.transport_type is None
        assert config.custom_headers == {}
        assert config.timeout is None

    def test_config_creation_http_server(self):
        """Test creating HTTP server config"""
        config = McpServerConfig(
            name='test-http-server',
            url='https://example.com/mcp',
            token='test-token'
        )

        assert config.name == 'test-http-server'
        assert config.url == 'https://example.com/mcp'
        assert config.token == 'test-token'
        assert config.command is None

    def test_config_creation_with_streamable_http_options(self):
        """Test creating config with Streamable HTTP options"""
        config = McpServerConfig(
            name='streamable-server',
            url='https://api.example.com/mcp',
            token='auth-token-123',
            transport_type='streamable-http',
            custom_headers={
                'X-API-Key': 'key-123',
                'X-Client-Version': '1.0.0'
            },
            timeout=120.0
        )

        assert config.name == 'streamable-server'
        assert config.url == 'https://api.example.com/mcp'
        assert config.token == 'auth-token-123'
        assert config.transport_type == 'streamable-http'
        assert config.custom_headers == {
            'X-API-Key': 'key-123',
            'X-Client-Version': '1.0.0'
        }
        assert config.timeout == 120.0

    def test_config_transport_type_values(self):
        """Test all valid transport_type values"""
        for transport in ['auto', 'streamable-http', 'legacy-sse', 'stdio']:
            config = McpServerConfig(
                name='test',
                transport_type=transport
            )
            assert config.transport_type == transport

    def test_config_to_dict_excludes_none(self):
        """Test to_dict excludes None values"""
        config = McpServerConfig(
            name='test-server',
            command='node',
            args=['server.js']
        )

        config_dict = config.to_dict()

        assert 'name' in config_dict
        assert 'command' in config_dict
        assert 'args' in config_dict
        # None values should be excluded
        assert 'url' not in config_dict
        assert 'token' not in config_dict
        assert 'transport_type' not in config_dict

    def test_config_to_dict_includes_all_set_values(self):
        """Test to_dict includes all set values"""
        config = McpServerConfig(
            name='full-config',
            command='python',
            args=['-m', 'server'],
            env={'DEBUG': '1'},
            url='https://example.com/mcp',
            token='token-123',
            auto_confirm=['tool1', 'tool2'],
            transport_type='streamable-http',
            custom_headers={'X-Test': 'value'},
            timeout=60.0
        )

        config_dict = config.to_dict()

        assert config_dict['name'] == 'full-config'
        assert config_dict['command'] == 'python'
        assert config_dict['args'] == ['-m', 'server']
        assert config_dict['env'] == {'DEBUG': '1'}
        assert config_dict['url'] == 'https://example.com/mcp'
        assert config_dict['token'] == 'token-123'
        assert config_dict['auto_confirm'] == ['tool1', 'tool2']
        assert config_dict['transport_type'] == 'streamable-http'
        assert config_dict['custom_headers'] == {'X-Test': 'value'}
        assert config_dict['timeout'] == 60.0

    def test_config_from_dict(self):
        """Test creating config from dictionary"""
        data = {
            'name': 'dict-config',
            'url': 'https://api.example.com/mcp',
            'transport_type': 'streamable-http',
            'custom_headers': {'X-Custom': 'header'},
            'timeout': 90.0
        }

        config = McpServerConfig.from_dict(data)

        assert config.name == 'dict-config'
        assert config.url == 'https://api.example.com/mcp'
        assert config.transport_type == 'streamable-http'
        assert config.custom_headers == {'X-Custom': 'header'}
        assert config.timeout == 90.0

    def test_config_auto_confirm_list(self):
        """Test auto_confirm list handling"""
        config = McpServerConfig(
            name='test',
            auto_confirm=['tool1', 'tool2', 'tool3']
        )

        assert len(config.auto_confirm) == 3
        assert 'tool1' in config.auto_confirm
        assert 'tool2' in config.auto_confirm
        assert 'tool3' in config.auto_confirm

    def test_config_empty_custom_headers(self):
        """Test config with empty custom_headers"""
        config = McpServerConfig(
            name='test',
            custom_headers={}
        )

        assert config.custom_headers == {}
        config_dict = config.to_dict()
        # Empty dict should be excluded
        assert 'custom_headers' not in config_dict or config_dict['custom_headers'] == {}

    def test_config_backward_compatibility(self):
        """Test config maintains backward compatibility with old configs"""
        # Old config without new fields
        old_config_data = {
            'name': 'old-server',
            'command': 'uvx',
            'args': ['mcp-server'],
            'env': {},
            'url': None,
            'token': None,
            'auto_confirm': []
        }

        config = McpServerConfig.from_dict(old_config_data)

        # Should work fine with defaults
        assert config.name == 'old-server'
        assert config.command == 'uvx'
        assert config.transport_type is None
        assert config.custom_headers == {}
        assert config.timeout is None
