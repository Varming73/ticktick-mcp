"""
Integration tests for MCP tools.

Tests actual tool invocation with mocked TickTick API responses.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from ticktick_mcp.src.tools.projects import (
    get_projects_tool,
    get_project_tool,
    create_project_tool
)
from ticktick_mcp.src.tools.tasks import (
    get_all_tasks_tool,
    create_task_tool,
    complete_task_tool
)
from ticktick_mcp.src.tools.gtd import (
    get_engaged_tasks_tool,
    get_next_tasks_tool
)


class TestProjectToolsIntegration:
    """Integration tests for project tools."""

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.projects.get_client')
    async def test_get_projects_success(self, mock_get_client):
        """Test successful get_projects tool invocation."""
        # Mock the client
        mock_client = Mock()
        mock_client.get_projects.return_value = [
            {"id": "proj1", "name": "Work", "color": "#FF0000"},
            {"id": "proj2", "name": "Personal", "color": "#00FF00"}
        ]
        mock_get_client.return_value = mock_client

        # Call the tool
        result = await get_projects_tool()

        # Verify result
        assert "Found 2 projects" in result
        assert "Work" in result
        assert "Personal" in result
        mock_client.get_projects.assert_called_once()

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.projects.get_client')
    async def test_get_projects_empty(self, mock_get_client):
        """Test get_projects with no projects."""
        mock_client = Mock()
        mock_client.get_projects.return_value = []
        mock_get_client.return_value = mock_client

        result = await get_projects_tool()

        assert "No projects found" in result

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.projects.get_client')
    async def test_get_projects_api_error(self, mock_get_client):
        """Test get_projects with API error."""
        mock_client = Mock()
        mock_client.get_projects.return_value = {
            "error": "API Error",
            "type": "api",
            "status_code": 500
        }
        mock_get_client.return_value = mock_client

        result = await get_projects_tool()

        assert "❌ API Error" in result

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.projects.get_client')
    async def test_create_project_success(self, mock_get_client):
        """Test successful project creation."""
        mock_client = Mock()
        mock_client.create_project.return_value = {
            "id": "new_proj",
            "name": "New Project",
            "color": "#F18181"
        }
        mock_get_client.return_value = mock_client

        result = await create_project_tool("New Project")

        assert "✅ Project created successfully" in result
        assert "New Project" in result
        mock_client.create_project.assert_called_once_with(
            name="New Project",
            color="#F18181",
            view_mode="list"
        )

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.projects.get_client')
    async def test_create_project_validation_error(self, mock_get_client):
        """Test project creation with validation error."""
        # This should be caught by the decorator
        from ticktick_mcp.src.ticktick_client import TaskValidator

        # Test empty name (should raise ValueError which decorator catches)
        mock_client = Mock()
        mock_client.create_project.side_effect = ValueError("Project name cannot be empty")
        mock_get_client.return_value = mock_client

        result = await create_project_tool("")

        assert "❌ Validation Error" in result


class TestTaskToolsIntegration:
    """Integration tests for task tools."""

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.tasks.get_client')
    async def test_get_all_tasks_success(self, mock_get_client):
        """Test successful get_all_tasks tool invocation."""
        mock_client = Mock()
        mock_client.get_projects.return_value = [
            {"id": "proj1", "name": "Work", "closed": False}
        ]
        mock_client.get_project_with_data.return_value = {
            "project": {"id": "proj1", "name": "Work"},
            "tasks": [
                {"id": "task1", "title": "Task 1", "priority": 5},
                {"id": "task2", "title": "Task 2", "priority": 0}
            ]
        }
        mock_get_client.return_value = mock_client

        result = await get_all_tasks_tool()

        assert "Found 1 projects" in result
        assert "Task 1" in result
        assert "Task 2" in result

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.tasks.get_client')
    async def test_create_task_success(self, mock_get_client):
        """Test successful task creation."""
        mock_client = Mock()
        mock_client.create_task.return_value = {
            "id": "new_task",
            "title": "New Task",
            "projectId": "proj1",
            "priority": 3
        }
        mock_get_client.return_value = mock_client

        result = await create_task_tool(
            title="New Task",
            project_id="proj1",
            priority=3
        )

        assert "Task created successfully" in result
        assert "New Task" in result

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.tasks.get_client')
    async def test_complete_task_success(self, mock_get_client):
        """Test successful task completion."""
        mock_client = Mock()
        mock_client.complete_task.return_value = {}
        mock_get_client.return_value = mock_client

        result = await complete_task_tool(
            project_id="proj1",
            task_id="task1"
        )

        assert "✅ Task task1 marked as complete" in result
        mock_client.complete_task.assert_called_once_with("proj1", "task1")


class TestGTDToolsIntegration:
    """Integration tests for GTD tools."""

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.gtd.get_client')
    async def test_get_engaged_tasks_success(self, mock_get_client):
        """Test get_engaged_tasks with high priority tasks."""
        from datetime import datetime, timezone

        mock_client = Mock()
        mock_client.get_projects.return_value = [
            {"id": "proj1", "name": "Work", "closed": False}
        ]

        # Create a task due today (high priority for engaged)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"

        mock_client.get_project_with_data.return_value = {
            "project": {"id": "proj1", "name": "Work"},
            "tasks": [
                {
                    "id": "task1",
                    "title": "Urgent Task",
                    "priority": 5,  # High priority
                    "dueDate": today
                }
            ]
        }
        mock_get_client.return_value = mock_client

        result = await get_engaged_tasks_tool()

        assert "Urgent Task" in result
        assert "engaged" in result.lower()

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.gtd.get_client')
    async def test_get_next_tasks_success(self, mock_get_client):
        """Test get_next_tasks with medium priority tasks."""
        from datetime import datetime, timezone, timedelta

        mock_client = Mock()
        mock_client.get_projects.return_value = [
            {"id": "proj1", "name": "Work", "closed": False}
        ]

        # Create a task due tomorrow (medium priority for next)
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"

        mock_client.get_project_with_data.return_value = {
            "project": {"id": "proj1", "name": "Work"},
            "tasks": [
                {
                    "id": "task1",
                    "title": "Next Task",
                    "priority": 3,  # Medium priority
                    "dueDate": tomorrow
                }
            ]
        }
        mock_get_client.return_value = mock_client

        result = await get_next_tasks_tool()

        assert "Next Task" in result
        assert "next" in result.lower()


class TestErrorHandlingIntegration:
    """Integration tests for error handling through decorator."""

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.projects.get_client')
    async def test_authentication_error_handling(self, mock_get_client):
        """Test that authentication errors are properly handled."""
        from ticktick_mcp.src.utils.errors import TickTickAuthenticationError

        mock_get_client.side_effect = TickTickAuthenticationError("Token expired")

        result = await get_projects_tool()

        assert "❌ Authentication Error" in result
        assert "Token expired" in result

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.projects.get_client')
    async def test_network_error_handling(self, mock_get_client):
        """Test that network errors are properly handled."""
        from ticktick_mcp.src.utils.errors import TickTickNetworkError

        mock_get_client.side_effect = TickTickNetworkError("Connection timeout")

        result = await get_projects_tool()

        assert "❌ Network Error" in result
        assert "Connection timeout" in result

    @pytest.mark.asyncio
    @patch('ticktick_mcp.src.tools.projects.get_client')
    async def test_rate_limit_error_handling(self, mock_get_client):
        """Test that rate limit errors are properly handled."""
        from ticktick_mcp.src.utils.errors import TickTickRateLimitError

        mock_get_client.side_effect = TickTickRateLimitError(
            "Rate limit exceeded",
            retry_after=60
        )

        result = await get_projects_tool()

        assert "❌ Rate Limit Exceeded" in result
        assert "60 seconds" in result
