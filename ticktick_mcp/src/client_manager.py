"""
Client manager for TickTick MCP server.

This module manages the singleton TickTickClient instance, avoiding
circular dependencies between server.py and tool modules.
"""

import os
import logging
from typing import Union, List, Dict, Any

from .ticktick_client import TickTickClient
from .utils.errors import (
    TickTickAuthenticationError,
    TickTickAPIError,
    TickTickNetworkError
)

logger = logging.getLogger(__name__)

# Module-level client instance (process-scoped, not global across users)
# In LibreChat multi-user mode, each user gets a separate process with their own instance
_client_instance: Union[TickTickClient, None] = None


def get_client() -> TickTickClient:
    """
    Get or create the TickTick client for this process.

    In LibreChat multi-user mode:
    - Each user gets a separate process spawned by LibreChat
    - Process has user-specific tokens in environment variables
    - Client is lazily initialized on first tool call
    - Client instance is reused for subsequent calls in same process

    Returns:
        TickTickClient: Initialized client with user's tokens

    Raises:
        TickTickAuthenticationError: If tokens are missing or invalid
        TickTickAPIError: If TickTick API returns an error
        TickTickNetworkError: If network connectivity fails
    """
    global _client_instance

    if _client_instance is not None:
        return _client_instance

    try:
        # Check if tokens are available (should be set by LibreChat)
        if os.getenv("TICKTICK_ACCESS_TOKEN") is None:
            raise TickTickAuthenticationError(
                "TICKTICK_ACCESS_TOKEN not found in environment. "
                "Please authenticate with TickTick in LibreChat."
            )

        # Initialize client (reads from env vars)
        try:
            _client_instance = TickTickClient()
            logger.info("TickTick client initialized successfully")
        except ValueError as e:
            # TickTickClient raises ValueError for missing tokens
            raise TickTickAuthenticationError(str(e))

        # Test API connectivity
        try:
            projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = _client_instance.get_projects()
            if isinstance(projects_result, dict) and 'error' in projects_result:
                error_msg = projects_result['error']
                logger.error(f"Failed to connect to TickTick API: {error_msg}")
                _client_instance = None  # Reset on failure

                # Determine error type from message
                if 'auth' in error_msg.lower() or 'token' in error_msg.lower() or '401' in error_msg:
                    raise TickTickAuthenticationError(f"Authentication failed: {error_msg}")
                else:
                    raise TickTickAPIError(f"TickTick API error: {error_msg}")

            # Type narrowing: projects_result must be a List
            projects: List[Dict[str, Any]] = projects_result if isinstance(projects_result, list) else []
            logger.info(f"Connected to TickTick API with {len(projects)} projects")
            return _client_instance

        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Network error connecting to TickTick: {e}")
            _client_instance = None
            raise TickTickNetworkError(f"Network connectivity issue: {str(e)}")

    except (TickTickAuthenticationError, TickTickAPIError, TickTickNetworkError):
        # Re-raise our custom exceptions
        _client_instance = None
        raise
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error initializing TickTick client: {e}")
        _client_instance = None
        raise TickTickAPIError(f"Unexpected error: {str(e)}")


def initialize_client() -> bool:
    """
    Initialize client and return success status.
    Kept for backward compatibility with Claude Desktop.

    Returns:
        True if client initialized successfully, False otherwise
    """
    try:
        get_client()
        return True
    except Exception as e:
        logger.error(f"Client initialization failed: {e}")
        return False


def reset_client() -> None:
    """
    Reset the client instance.

    Useful for testing or when tokens are refreshed.
    """
    global _client_instance
    if _client_instance is not None:
        _client_instance.close()  # Close session if client has close method
        _client_instance = None
