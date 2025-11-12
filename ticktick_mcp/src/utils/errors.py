"""
Error handling utilities for TickTick MCP server.

This module provides custom exception classes and decorators for
consistent error handling across all MCP tools.
"""

import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


# Custom exceptions for better error handling
class TickTickAuthenticationError(Exception):
    """Raised when authentication with TickTick fails or tokens are missing."""
    pass


class TickTickAPIError(Exception):
    """Raised when TickTick API returns an error response."""
    pass


class TickTickNetworkError(Exception):
    """Raised when network connectivity issues prevent API communication."""
    pass


class TickTickRateLimitError(Exception):
    """Raised when TickTick API rate limit is exceeded."""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


def handle_mcp_errors(func: Callable) -> Callable:
    """
    Decorator to handle common TickTick errors in MCP tools.

    This decorator catches TickTick-specific exceptions and returns
    user-friendly error messages in a consistent format.

    Args:
        func: The async function to wrap (typically an MCP tool)

    Returns:
        Wrapped function that handles errors gracefully

    Example:
        @mcp.tool()
        @handle_mcp_errors
        async def get_projects() -> str:
            client = get_client()
            projects = client.get_projects()
            return format_projects(projects)
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            return await func(*args, **kwargs)
        except TickTickAuthenticationError as e:
            logger.error(f"Authentication error in {func.__name__}: {e}")
            return (
                f"❌ Authentication Error: {str(e)}\n\n"
                "Please authenticate with TickTick in the LibreChat UI."
            )
        except TickTickRateLimitError as e:
            logger.warning(f"Rate limit error in {func.__name__}: {e}")
            retry_msg = f" Please retry after {e.retry_after} seconds." if e.retry_after else ""
            return (
                f"❌ Rate Limit Exceeded: {str(e)}\n\n"
                f"You've made too many requests to TickTick.{retry_msg}"
            )
        except TickTickAPIError as e:
            logger.error(f"API error in {func.__name__}: {e}")
            return (
                f"❌ TickTick API Error: {str(e)}\n\n"
                "The TickTick service may be experiencing issues. Please try again later."
            )
        except TickTickNetworkError as e:
            logger.error(f"Network error in {func.__name__}: {e}")
            return (
                f"❌ Network Error: {str(e)}\n\n"
                "Please check your internet connection and try again."
            )
        except ValueError as e:
            # Validation errors from TaskValidator
            logger.error(f"Validation error in {func.__name__}: {e}")
            return f"❌ Validation Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            return f"❌ Unexpected Error: {str(e)}"

    return wrapper


def ensure_list_response(response: Any) -> Any:
    """
    Ensure API response is a list, returning error string if not.

    This helper function handles the common pattern of checking if an API
    response is an error dict or an unexpected format, providing proper
    type narrowing without using # type: ignore.

    Args:
        response: API response that should be a list

    Returns:
        The list if valid, or an error message string if error/invalid

    Example:
        projects = client.get_projects()
        result = ensure_list_response(projects)
        if isinstance(result, str):
            return result  # Error message
        # result is now definitely a list
    """
    # Check if it's an error dict
    if isinstance(response, dict) and 'error' in response:
        return parse_error_response(response)

    # Check if it's a list
    if not isinstance(response, list):
        return "❌ Unexpected response format from TickTick API"

    return response


def parse_error_response(response_dict: dict) -> str:
    """
    Parse an error response from the TickTick API client and return a user-friendly message.

    Args:
        response_dict: Error dictionary with 'error', 'type', and optionally 'status_code'

    Returns:
        Formatted error message string

    Example:
        error = {"error": "Not found", "type": "not_found", "status_code": 404}
        message = parse_error_response(error)
    """
    error_type = response_dict.get('type', 'unknown')
    error_msg = response_dict.get('error', 'Unknown error')
    status_code = response_dict.get('status_code')

    if error_type == 'auth':
        return (
            f"❌ Authentication Error: {error_msg}\n\n"
            "Please re-authenticate with TickTick in LibreChat."
        )
    elif error_type == 'permission':
        return (
            f"❌ Permission Denied: {error_msg}\n\n"
            "You don't have access to this resource."
        )
    elif error_type == 'not_found':
        return (
            f"❌ Resource Not Found: {error_msg}\n\n"
            "The requested resource may have been deleted."
        )
    elif error_type == 'rate_limit':
        retry_after = response_dict.get('retry_after', 'unknown')
        return (
            f"❌ Rate Limit Exceeded: {error_msg}\n\n"
            f"Please retry after {retry_after} seconds."
        )
    elif error_type == 'network':
        return (
            f"❌ Network Error: {error_msg}\n\n"
            "Please check your internet connection and try again."
        )
    elif error_type == 'server_error':
        return (
            f"❌ Server Error ({status_code}): {error_msg}\n\n"
            "TickTick is experiencing issues. Please try again later."
        )
    else:
        return f"❌ API Error: {error_msg}"
