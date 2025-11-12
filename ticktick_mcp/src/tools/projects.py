"""
Project management tools for TickTick MCP server.

This module contains all MCP tools related to managing TickTick projects.
"""

from typing import Dict, List, Any, Union, Optional

from ..utils.errors import handle_mcp_errors, parse_error_response, ensure_list_response
from ..utils.formatting import format_project
from ..client_manager import get_client


@handle_mcp_errors
async def get_projects_tool() -> str:
    """Get all projects from TickTick."""
    client = get_client()
    projects_result = client.get_projects()

    # Check if result is valid or an error
    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    if not projects:
        return "No projects found."

    result = f"Found {len(projects)} projects:\n\n"
    for i, project in enumerate(projects, 1):
        result += f"Project {i}:\n" + format_project(project) + "\n"

    return result


@handle_mcp_errors
async def get_project_tool(project_id: str) -> str:
    """
    Get details about a specific project.

    Args:
        project_id: ID of the project
    """
    client = get_client()
    project = client.get_project(project_id)

    if 'error' in project:
        return parse_error_response(project)

    return format_project(project)


@handle_mcp_errors
async def get_project_tasks_tool(project_id: str) -> str:
    """
    Get all tasks in a specific project.

    Args:
        project_id: ID of the project
    """
    from ..utils.formatting import format_task  # Import here to avoid circular dependency

    client = get_client()
    project_data = client.get_project_with_data(project_id)

    if 'error' in project_data:
        return parse_error_response(project_data)

    tasks = project_data.get('tasks', [])
    if not tasks:
        return f"No tasks found in project '{project_data.get('project', {}).get('name', project_id)}'."

    result = f"Found {len(tasks)} tasks in project '{project_data.get('project', {}).get('name', project_id)}':\n\n"
    for i, task in enumerate(tasks, 1):
        result += f"Task {i}:\n" + format_task(task) + "\n"

    return result


@handle_mcp_errors
async def create_project_tool(
    name: str,
    color: str = "#F18181",
    view_mode: str = "list"
) -> str:
    """
    Create a new project in TickTick.

    Args:
        name: Project name
        color: Color code (hex format) (optional)
        view_mode: View mode - one of list, kanban, or timeline (optional)
    """
    # Validate view_mode
    if view_mode not in ["list", "kanban", "timeline"]:
        return "Invalid view_mode. Must be one of: list, kanban, timeline."

    client = get_client()
    project = client.create_project(
        name=name,
        color=color,
        view_mode=view_mode
    )

    if 'error' in project:
        return parse_error_response(project)

    return f"✅ Project created successfully:\n\n" + format_project(project)


@handle_mcp_errors
async def update_project_tool(
    project_id: str,
    name: Optional[str] = None,
    color: Optional[str] = None,
    view_mode: Optional[str] = None
) -> str:
    """
    Update an existing project in TickTick.

    Args:
        project_id: ID of the project to update
        name: New project name (optional)
        color: New color code (hex format) (optional)
        view_mode: New view mode - one of list, kanban, or timeline (optional)
    """
    # Validate view_mode if provided
    if view_mode and view_mode not in ["list", "kanban", "timeline"]:
        return "Invalid view_mode. Must be one of: list, kanban, timeline."

    # Check that at least one field is being updated
    if not any([name, color, view_mode]):
        return "❌ No updates provided. Please specify at least one field to update (name, color, or view_mode)."

    client = get_client()
    project = client.update_project(
        project_id=project_id,
        name=name,
        color=color,
        view_mode=view_mode
    )

    if 'error' in project:
        return parse_error_response(project)

    return f"✅ Project updated successfully:\n\n" + format_project(project)


@handle_mcp_errors
async def delete_project_tool(project_id: str) -> str:
    """
    Delete a project.

    Args:
        project_id: ID of the project
    """
    client = get_client()
    result = client.delete_project(project_id)

    if 'error' in result:
        return parse_error_response(result)

    return f"✅ Project {project_id} deleted successfully."
