"""
Unit tests for TaskValidator class.

Tests validation logic for tasks and projects.
"""

import pytest
from ticktick_mcp.src.ticktick_client import TaskValidator


class TestTaskValidator:
    """Test cases for TaskValidator class."""

    def test_validate_task_title_valid(self):
        """Test that valid task titles pass validation."""
        TaskValidator.validate_task_title("Buy groceries")
        TaskValidator.validate_task_title("A" * 500)  # Max length

    def test_validate_task_title_empty(self):
        """Test that empty task titles raise ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            TaskValidator.validate_task_title("")

        with pytest.raises(ValueError, match="Task title cannot be empty"):
            TaskValidator.validate_task_title("   ")

    def test_validate_task_title_too_long(self):
        """Test that titles exceeding max length raise ValueError."""
        long_title = "A" * 501
        with pytest.raises(ValueError, match="must be 500 characters or less"):
            TaskValidator.validate_task_title(long_title)

    def test_validate_project_name_valid(self):
        """Test that valid project names pass validation."""
        TaskValidator.validate_project_name("Work")
        TaskValidator.validate_project_name("A" * 200)  # Max length

    def test_validate_project_name_empty(self):
        """Test that empty project names raise ValueError."""
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            TaskValidator.validate_project_name("")

    def test_validate_project_name_too_long(self):
        """Test that project names exceeding max length raise ValueError."""
        long_name = "A" * 201
        with pytest.raises(ValueError, match="must be 200 characters or less"):
            TaskValidator.validate_project_name(long_name)

    def test_validate_content_valid(self):
        """Test that valid content passes validation."""
        TaskValidator.validate_content(None)
        TaskValidator.validate_content("Some content")
        TaskValidator.validate_content("A" * 10000)  # Max length

    def test_validate_content_too_long(self):
        """Test that content exceeding max length raises ValueError."""
        long_content = "A" * 10001
        with pytest.raises(ValueError, match="must be 10000 characters or less"):
            TaskValidator.validate_content(long_content)

    def test_validate_priority_valid(self):
        """Test that valid priority values pass validation."""
        TaskValidator.validate_priority(0)
        TaskValidator.validate_priority(1)
        TaskValidator.validate_priority(3)
        TaskValidator.validate_priority(5)

    def test_validate_priority_invalid(self):
        """Test that invalid priority values raise ValueError."""
        with pytest.raises(ValueError, match="Priority must be one of"):
            TaskValidator.validate_priority(2)

        with pytest.raises(ValueError, match="Priority must be one of"):
            TaskValidator.validate_priority(10)

    def test_validate_date_valid(self):
        """Test that valid date strings pass validation."""
        TaskValidator.validate_date(None, "test_date")
        TaskValidator.validate_date("2025-01-15", "test_date")
        TaskValidator.validate_date("2025-01-15T10:30:00", "test_date")
        TaskValidator.validate_date("2025-01-15T10:30:00Z", "test_date")
        TaskValidator.validate_date("2025-01-15T10:30:00+00:00", "test_date")

    def test_validate_date_invalid(self):
        """Test that invalid date strings raise ValueError."""
        with pytest.raises(ValueError, match="must be in ISO format"):
            TaskValidator.validate_date("invalid-date", "test_date")

        with pytest.raises(ValueError, match="must be in ISO format"):
            TaskValidator.validate_date("2025-13-01", "test_date")  # Invalid month
