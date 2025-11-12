"""
Getting Things Done (GTD) workflow tools for TickTick MCP server.

This module contains MCP tools implementing the GTD methodology
for task prioritization and management.
"""

from typing import Dict, List, Any, Union

from ..utils.errors import handle_mcp_errors, parse_error_response, ensure_list_response
from ..client_manager import get_client


def _is_task_due_today(task: Dict[str, Any]) -> bool:
    """Check if a task is due today."""
    from ..tools.tasks import _is_task_due_today as _check
    return _check(task)


def _is_task_overdue(task: Dict[str, Any]) -> bool:
    """Check if a task is overdue."""
    from ..tools.tasks import _is_task_overdue as _check
    return _check(task)


def _is_task_due_in_days(task: Dict[str, Any], days: int) -> bool:
    """Check if a task is due in exactly X days."""
    from ..tools.tasks import _is_task_due_in_days as _check
    return _check(task, days)


def _get_project_tasks_by_filter(projects: List[Dict], filter_func, filter_name: str) -> str:
    """Helper function to filter tasks across all projects."""
    from ..tools.tasks import _get_project_tasks_by_filter as _filter
    return _filter(projects, filter_func, filter_name)


@handle_mcp_errors
async def get_engaged_tasks_tool() -> str:
    """
    Get all tasks from TickTick that are "Engaged".
    This includes tasks marked as high priority (5), due today or overdue.

    This follows the GTD (Getting Things Done) methodology where "engaged"
    tasks are the highest priority items requiring immediate attention.
    """
    client = get_client()
    projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = client.get_projects()

    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    def engaged_filter(task: Dict[str, Any]) -> bool:
        is_high_priority = task.get('priority', 0) == 5
        is_overdue = _is_task_overdue(task)
        is_today = _is_task_due_today(task)
        return is_high_priority or is_overdue or is_today

    return _get_project_tasks_by_filter(projects, engaged_filter, "engaged")


@handle_mcp_errors
async def get_next_tasks_tool() -> str:
    """
    Get all tasks from TickTick that are "Next".
    This includes tasks marked as medium priority (3) or due tomorrow.

    This follows the GTD (Getting Things Done) methodology where "next"
    tasks are items to focus on after completing engaged tasks.
    """
    client = get_client()
    projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = client.get_projects()

    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    def next_filter(task: Dict[str, Any]) -> bool:
        is_medium_priority = task.get('priority', 0) == 3
        is_due_tomorrow = _is_task_due_in_days(task, 1)
        return is_medium_priority or is_due_tomorrow

    return _get_project_tasks_by_filter(projects, next_filter, "next")
