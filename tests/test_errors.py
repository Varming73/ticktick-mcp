"""
Unit tests for error handling utilities.

Tests custom exceptions and error decorators.
"""

import pytest
from unittest.mock import AsyncMock, patch
from ticktick_mcp.src.utils.errors import (
    TickTickAuthenticationError,
    TickTickAPIError,
    TickTickNetworkError,
    TickTickRateLimitError,
    handle_mcp_errors,
    parse_error_response
)


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_authentication_error(self):
        """Test TickTickAuthenticationError."""
        error = TickTickAuthenticationError("Invalid token")
        assert str(error) == "Invalid token"
        assert isinstance(error, Exception)

    def test_api_error(self):
        """Test TickTickAPIError."""
        error = TickTickAPIError("API failed")
        assert str(error) == "API failed"
        assert isinstance(error, Exception)

    def test_network_error(self):
        """Test TickTickNetworkError."""
        error = TickTickNetworkError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, Exception)

    def test_rate_limit_error(self):
        """Test TickTickRateLimitError with retry_after."""
        error = TickTickRateLimitError("Rate limit exceeded", retry_after=60)
        assert str(error) == "Rate limit exceeded"
        assert error.retry_after == 60
        assert isinstance(error, Exception)


class TestHandleMCPErrors:
    """Test handle_mcp_errors decorator."""

    @pytest.mark.asyncio
    async def test_successful_function(self):
        """Test decorator with successful function."""
        @handle_mcp_errors
        async def test_func():
            return "Success"

        result = await test_func()
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_authentication_error(self):
        """Test decorator handles authentication error."""
        @handle_mcp_errors
        async def test_func():
            raise TickTickAuthenticationError("Token expired")

        result = await test_func()
        assert "❌ Authentication Error" in result
        assert "Token expired" in result

    @pytest.mark.asyncio
    async def test_rate_limit_error(self):
        """Test decorator handles rate limit error."""
        @handle_mcp_errors
        async def test_func():
            raise TickTickRateLimitError("Too many requests", retry_after=120)

        result = await test_func()
        assert "❌ Rate Limit Exceeded" in result
        assert "120 seconds" in result

    @pytest.mark.asyncio
    async def test_api_error(self):
        """Test decorator handles API error."""
        @handle_mcp_errors
        async def test_func():
            raise TickTickAPIError("Server error")

        result = await test_func()
        assert "❌ TickTick API Error" in result
        assert "Server error" in result

    @pytest.mark.asyncio
    async def test_network_error(self):
        """Test decorator handles network error."""
        @handle_mcp_errors
        async def test_func():
            raise TickTickNetworkError("Connection timeout")

        result = await test_func()
        assert "❌ Network Error" in result
        assert "Connection timeout" in result

    @pytest.mark.asyncio
    async def test_validation_error(self):
        """Test decorator handles validation error."""
        @handle_mcp_errors
        async def test_func():
            raise ValueError("Invalid input")

        result = await test_func()
        assert "❌ Validation Error" in result
        assert "Invalid input" in result

    @pytest.mark.asyncio
    async def test_unexpected_error(self):
        """Test decorator handles unexpected error."""
        @handle_mcp_errors
        async def test_func():
            raise RuntimeError("Unexpected issue")

        result = await test_func()
        assert "❌ Unexpected Error" in result
        assert "Unexpected issue" in result


class TestParseErrorResponse:
    """Test parse_error_response function."""

    def test_auth_error(self):
        """Test parsing authentication error."""
        error = {"error": "Unauthorized", "type": "auth", "status_code": 401}
        result = parse_error_response(error)
        assert "❌ Authentication Error" in result
        assert "Unauthorized" in result

    def test_permission_error(self):
        """Test parsing permission error."""
        error = {"error": "Forbidden", "type": "permission", "status_code": 403}
        result = parse_error_response(error)
        assert "❌ Permission Denied" in result
        assert "Forbidden" in result

    def test_not_found_error(self):
        """Test parsing not found error."""
        error = {"error": "Not found", "type": "not_found", "status_code": 404}
        result = parse_error_response(error)
        assert "❌ Resource Not Found" in result

    def test_rate_limit_error(self):
        """Test parsing rate limit error."""
        error = {"error": "Too many requests", "type": "rate_limit", "retry_after": 60}
        result = parse_error_response(error)
        assert "❌ Rate Limit Exceeded" in result
        assert "60 seconds" in result

    def test_network_error(self):
        """Test parsing network error."""
        error = {"error": "Connection failed", "type": "network"}
        result = parse_error_response(error)
        assert "❌ Network Error" in result

    def test_server_error(self):
        """Test parsing server error."""
        error = {"error": "Internal server error", "type": "server_error", "status_code": 500}
        result = parse_error_response(error)
        assert "❌ Server Error (500)" in result

    def test_unknown_error(self):
        """Test parsing unknown error."""
        error = {"error": "Something went wrong", "type": "unknown"}
        result = parse_error_response(error)
        assert "❌ API Error" in result
