"""
Task management tools for TickTick MCP server.

This module contains all MCP tools related to managing TickTick tasks,
including CRUD operations and search/filter functionality.
"""

from typing import Dict, List, Any, Union, Optional
from datetime import datetime, timezone, timedelta

from ..utils.errors import handle_mcp_errors, parse_error_response, ensure_list_response
from ..utils.formatting import format_task, PRIORITY_MAP
from ..client_manager import get_client


# Helper Functions for Task Filtering

def _is_task_due_today(task: Dict[str, Any]) -> bool:
    """Check if a task is due today."""
    due_date = task.get('dueDate')
    if not due_date:
        return False

    try:
        task_due_date = datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%S.%f%z").date()
        today_date = datetime.now(timezone.utc).date()
        return task_due_date == today_date
    except (ValueError, TypeError):
        return False


def _is_task_overdue(task: Dict[str, Any]) -> bool:
    """Check if a task is overdue."""
    due_date = task.get('dueDate')
    if not due_date:
        return False

    try:
        task_due = datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        return task_due < datetime.now(timezone.utc)
    except (ValueError, TypeError):
        return False


def _is_task_due_in_days(task: Dict[str, Any], days: int) -> bool:
    """Check if a task is due in exactly X days."""
    due_date = task.get('dueDate')
    if not due_date:
        return False

    try:
        task_due_date = datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%S.%f%z").date()
        target_date = (datetime.now(timezone.utc) + timedelta(days=days)).date()
        return task_due_date == target_date
    except (ValueError, TypeError):
        return False


def _task_matches_search(task: Dict[str, Any], search_term: str) -> bool:
    """Check if a task matches the search term (case-insensitive)."""
    search_term = search_term.lower()

    # Search in title
    title = task.get('title', '').lower()
    if search_term in title:
        return True

    # Search in content
    content = task.get('content', '').lower()
    if search_term in content:
        return True

    # Search in subtasks
    items = task.get('items', [])
    for item in items:
        item_title = item.get('title', '').lower()
        if search_term in item_title:
            return True

    return False


def _validate_task_data(task_data: Dict[str, Any], task_index: int) -> Optional[str]:
    """
    Validate a single task's data for batch creation.

    Returns:
        None if valid, error message string if invalid
    """
    # Check required fields
    if 'title' not in task_data or not task_data['title']:
        return f"Task {task_index + 1}: 'title' is required and cannot be empty"

    if 'project_id' not in task_data or not task_data['project_id']:
        return f"Task {task_index + 1}: 'project_id' is required and cannot be empty"

    # Validate priority if provided
    priority = task_data.get('priority')
    if priority is not None and priority not in [0, 1, 3, 5]:
        return f"Task {task_index + 1}: Invalid priority {priority}. Must be 0 (None), 1 (Low), 3 (Medium), or 5 (High)"

    # Validate dates if provided
    for date_field in ['start_date', 'due_date']:
        date_str = task_data.get(date_field)
        if date_str:
            try:
                # Try to parse the date to validate it
                if date_str.endswith('Z'):
                    datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                elif '+' in date_str or date_str.endswith(('00', '30')):
                    datetime.fromisoformat(date_str)
                else:
                    datetime.fromisoformat(date_str)
            except ValueError:
                return f"Task {task_index + 1}: Invalid {date_field} format '{date_str}'. Use ISO format: YYYY-MM-DDTHH:mm:ss or with timezone"

    return None


def _get_project_tasks_by_filter(projects: List[Dict], filter_func, filter_name: str) -> str:
    """
    Helper function to filter tasks across all projects.

    Args:
        projects: List of project dictionaries
        filter_func: Function that takes a task and returns True if it matches the filter
        filter_name: Name of the filter for output formatting

    Returns:
        Formatted string of filtered tasks
    """
    if not projects:
        return "No projects found."

    client = get_client()
    result = f"Found {len(projects)} projects:\n\n"

    for i, project in enumerate(projects, 1):
        if project.get('closed'):
            continue

        project_id = project.get('id', 'No ID')
        project_data = client.get_project_with_data(project_id)
        tasks = project_data.get('tasks', [])

        if not tasks:
            from ..utils.formatting import format_project
            result += f"Project {i}:\n{format_project(project)}"
            result += f"With 0 tasks that are to be '{filter_name}' in this project :\n\n\n"
            continue

        # Filter tasks using the provided function
        filtered_tasks = [(t, task) for t, task in enumerate(tasks, 1) if filter_func(task)]

        from ..utils.formatting import format_project
        result += f"Project {i}:\n{format_project(project)}"
        result += f"With {len(filtered_tasks)} tasks that are to be '{filter_name}' in this project :\n"

        for t, task in filtered_tasks:
            result += f"Task {t}:\n{format_task(task)}\n"

        result += "\n\n"

    return result


# Task CRUD Tools

@handle_mcp_errors
async def get_task_tool(project_id: str, task_id: str) -> str:
    """
    Get details about a specific task.

    Args:
        project_id: ID of the project
        task_id: ID of the task
    """
    client = get_client()
    task = client.get_task(project_id, task_id)

    if 'error' in task:
        return parse_error_response(task)

    return format_task(task)


@handle_mcp_errors
async def create_task_tool(
    title: str,
    project_id: str,
    content: Optional[str] = None,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: int = 0
) -> str:
    """
    Create a new task in TickTick.

    Args:
        title: Task title
        project_id: ID of the project to add the task to
        content: Task description/content (optional)
        start_date: Start date in ISO format YYYY-MM-DDThh:mm:ss+0000 (optional)
        due_date: Due date in ISO format YYYY-MM-DDThh:mm:ss+0000 (optional)
        priority: Priority level (0: None, 1: Low, 3: Medium, 5: High) (optional)
    """
    # Validate priority
    if priority not in [0, 1, 3, 5]:
        return "Invalid priority. Must be 0 (None), 1 (Low), 3 (Medium), or 5 (High)."

    # Validate dates if provided
    for date_str, date_name in [(start_date, "start_date"), (due_date, "due_date")]:
        if date_str:
            try:
                datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                return f"Invalid {date_name} format. Use ISO format: YYYY-MM-DDThh:mm:ss+0000"

    client = get_client()
    task = client.create_task(
        title=title,
        project_id=project_id,
        content=content,
        start_date=start_date,
        due_date=due_date,
        priority=priority
    )

    if 'error' in task:
        return parse_error_response(task)

    return f"Task created successfully:\n\n" + format_task(task)


@handle_mcp_errors
async def update_task_tool(
    task_id: str,
    project_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[int] = None
) -> str:
    """
    Update an existing task in TickTick.

    Args:
        task_id: ID of the task to update
        project_id: ID of the project the task belongs to
        title: New task title (optional)
        content: New task description/content (optional)
        start_date: New start date in ISO format YYYY-MM-DDThh:mm:ss+0000 (optional)
        due_date: New due date in ISO format YYYY-MM-DDThh:mm:ss+0000 (optional)
        priority: New priority level (0: None, 1: Low, 3: Medium, 5: High) (optional)
    """
    # Validate priority if provided
    if priority is not None and priority not in [0, 1, 3, 5]:
        return "Invalid priority. Must be 0 (None), 1 (Low), 3 (Medium), or 5 (High)."

    # Validate dates if provided
    for date_str, date_name in [(start_date, "start_date"), (due_date, "due_date")]:
        if date_str:
            try:
                datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                return f"Invalid {date_name} format. Use ISO format: YYYY-MM-DDThh:mm:ss+0000"

    client = get_client()
    task = client.update_task(
        task_id=task_id,
        project_id=project_id,
        title=title,
        content=content,
        start_date=start_date,
        due_date=due_date,
        priority=priority
    )

    if 'error' in task:
        return parse_error_response(task)

    return f"Task updated successfully:\n\n" + format_task(task)


@handle_mcp_errors
async def complete_task_tool(project_id: str, task_id: str) -> str:
    """
    Mark a task as complete.

    Args:
        project_id: ID of the project
        task_id: ID of the task
    """
    client = get_client()
    result = client.complete_task(project_id, task_id)

    if 'error' in result:
        return parse_error_response(result)

    return f"✅ Task {task_id} marked as complete."


@handle_mcp_errors
async def delete_task_tool(project_id: str, task_id: str) -> str:
    """
    Delete a task.

    Args:
        project_id: ID of the project
        task_id: ID of the task
    """
    client = get_client()
    result = client.delete_task(project_id, task_id)

    if 'error' in result:
        return parse_error_response(result)

    return f"✅ Task {task_id} deleted successfully."


@handle_mcp_errors
async def create_subtask_tool(
    subtask_title: str,
    parent_task_id: str,
    project_id: str,
    content: Optional[str] = None,
    priority: int = 0
) -> str:
    """
    Create a subtask for a parent task within the same project.

    Args:
        subtask_title: Title of the subtask
        parent_task_id: ID of the parent task
        project_id: ID of the project (must be same for both parent and subtask)
        content: Optional content/description for the subtask
        priority: Priority level (0: None, 1: Low, 3: Medium, 5: High) (optional)
    """
    # Validate priority
    if priority not in [0, 1, 3, 5]:
        return "Invalid priority. Must be 0 (None), 1 (Low), 3 (Medium), or 5 (High)."

    client = get_client()
    subtask = client.create_subtask(
        subtask_title=subtask_title,
        parent_task_id=parent_task_id,
        project_id=project_id,
        content=content,
        priority=priority
    )

    if 'error' in subtask:
        return parse_error_response(subtask)

    return f"✅ Subtask created successfully:\n\n" + format_task(subtask)


# Task Search and Filter Tools

@handle_mcp_errors
async def get_all_tasks_tool() -> str:
    """Get all tasks from TickTick. Ignores closed projects."""
    client = get_client()
    projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = client.get_projects()

    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    def all_tasks_filter(task: Dict[str, Any]) -> bool:
        return True  # Include all tasks

    return _get_project_tasks_by_filter(projects, all_tasks_filter, "included")


@handle_mcp_errors
async def get_tasks_by_priority_tool(priority_id: int) -> str:
    """
    Get all tasks from TickTick by priority. Ignores closed projects.

    Args:
        priority_id: Priority of tasks to retrieve {0: "None", 1: "Low", 3: "Medium", 5: "High"}
    """
    if priority_id not in PRIORITY_MAP:
        return f"Invalid priority_id. Valid values: {list(PRIORITY_MAP.keys())}"

    client = get_client()
    projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = client.get_projects()

    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    def priority_filter(task: Dict[str, Any]) -> bool:
        return task.get('priority', 0) == priority_id

    priority_name = f"{PRIORITY_MAP[priority_id]} ({priority_id})"
    return _get_project_tasks_by_filter(projects, priority_filter, f"priority '{priority_name}'")


@handle_mcp_errors
async def get_tasks_due_today_tool() -> str:
    """Get all tasks from TickTick that are due today. Ignores closed projects."""
    client = get_client()
    projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = client.get_projects()

    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    return _get_project_tasks_by_filter(projects, _is_task_due_today, "due today")


@handle_mcp_errors
async def get_overdue_tasks_tool() -> str:
    """Get all overdue tasks from TickTick. Ignores closed projects."""
    client = get_client()
    projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = client.get_projects()

    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    return _get_project_tasks_by_filter(projects, _is_task_overdue, "overdue")


@handle_mcp_errors
async def get_tasks_due_tomorrow_tool() -> str:
    """Get all tasks from TickTick that are due tomorrow. Ignores closed projects."""
    client = get_client()
    projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = client.get_projects()

    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    def tomorrow_filter(task: Dict[str, Any]) -> bool:
        return _is_task_due_in_days(task, 1)

    return _get_project_tasks_by_filter(projects, tomorrow_filter, "due tomorrow")


@handle_mcp_errors
async def get_tasks_due_in_days_tool(days: int) -> str:
    """
    Get all tasks from TickTick that are due in exactly X days. Ignores closed projects.

    Args:
        days: Number of days from today (0 = today, 1 = tomorrow, etc.)
    """
    if days < 0:
        return "Days must be a non-negative integer."

    client = get_client()
    projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = client.get_projects()

    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    def days_filter(task: Dict[str, Any]) -> bool:
        return _is_task_due_in_days(task, days)

    day_description = "today" if days == 0 else f"in {days} day{'s' if days != 1 else ''}"
    return _get_project_tasks_by_filter(projects, days_filter, f"due {day_description}")


@handle_mcp_errors
async def get_tasks_due_this_week_tool() -> str:
    """Get all tasks from TickTick that are due within the next 7 days. Ignores closed projects."""
    client = get_client()
    projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = client.get_projects()

    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    def week_filter(task: Dict[str, Any]) -> bool:
        due_date = task.get('dueDate')
        if not due_date:
            return False

        try:
            task_due_date = datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%S.%f%z").date()
            today = datetime.now(timezone.utc).date()
            week_from_today = today + timedelta(days=7)
            return today <= task_due_date <= week_from_today
        except (ValueError, TypeError):
            return False

    return _get_project_tasks_by_filter(projects, week_filter, "due this week")


@handle_mcp_errors
async def search_tasks_tool(search_term: str) -> str:
    """
    Search for tasks in TickTick by title, content, or subtask titles. Ignores closed projects.

    Args:
        search_term: Text to search for (case-insensitive)
    """
    if not search_term.strip():
        return "Search term cannot be empty."

    client = get_client()
    projects_result: Union[List[Dict[str, Any]], Dict[str, Any]] = client.get_projects()

    projects = ensure_list_response(projects_result)
    if isinstance(projects, str):
        return projects  # Error message

    def search_filter(task: Dict[str, Any]) -> bool:
        return _task_matches_search(task, search_term)

    return _get_project_tasks_by_filter(projects, search_filter, f"matching '{search_term}'")


@handle_mcp_errors
async def batch_create_tasks_tool(tasks: List[Dict[str, Any]]) -> str:
    """
    Create multiple tasks in TickTick at once

    Args:
        tasks: List of task dictionaries. Each task must contain:
            - title (required): Task Name
            - project_id (required): ID of the project for the task
            - content (optional): Task description
            - start_date (optional): Start date in user timezone (YYYY-MM-DDTHH:mm:ss or with timezone)
            - due_date (optional): Due date in user timezone (YYYY-MM-DDTHH:mm:ss or with timezone)
            - priority (optional): Priority level {0: "None", 1: "Low", 3: "Medium", 5: "High"}
    """
    if not tasks:
        return "No tasks provided. Please provide a list of tasks to create."

    if not isinstance(tasks, list):
        return "Tasks must be provided as a list of dictionaries."

    # Validate all tasks before creating any
    validation_errors = []
    for i, task_data in enumerate(tasks):
        if not isinstance(task_data, dict):
            validation_errors.append(f"Task {i + 1}: Must be a dictionary")
            continue

        error = _validate_task_data(task_data, i)
        if error:
            validation_errors.append(error)

    if validation_errors:
        return "Validation errors found:\n" + "\n".join(validation_errors)

    # Create tasks one by one and collect results
    created_tasks = []
    failed_tasks = []

    client = get_client()

    for i, task_data in enumerate(tasks):
        try:
            # Extract task parameters with defaults
            title = task_data['title']
            project_id = task_data['project_id']
            content = task_data.get('content')
            start_date = task_data.get('start_date')
            due_date = task_data.get('due_date')
            priority = task_data.get('priority', 0)

            # Create the task
            result = client.create_task(
                title=title,
                project_id=project_id,
                content=content,
                start_date=start_date,
                due_date=due_date,
                priority=priority
            )

            if 'error' in result:
                error_type = result.get('type', 'unknown')
                error_msg = result['error']

                if error_type == 'auth':
                    failed_tasks.append(f"Task {i + 1} ('{title}'): Authentication failed (401)")
                elif error_type == 'permission':
                    failed_tasks.append(f"Task {i + 1} ('{title}'): Permission denied (403)")
                elif error_type == 'not_found':
                    failed_tasks.append(f"Task {i + 1} ('{title}'): Project not found (404)")
                elif error_type == 'network':
                    failed_tasks.append(f"Task {i + 1} ('{title}'): Network error")
                else:
                    failed_tasks.append(f"Task {i + 1} ('{title}'): {error_msg}")
            else:
                created_tasks.append((i + 1, title, result))

        except Exception as e:
            failed_tasks.append(f"Task {i + 1} ('{task_data.get('title', 'Unknown')}'): {str(e)}")

    # Format the results
    result_message = f"Batch task creation completed.\n\n"
    result_message += f"Successfully created: {len(created_tasks)} tasks\n"
    result_message += f"Failed: {len(failed_tasks)} tasks\n\n"

    if created_tasks:
        result_message += "✅ Successfully Created Tasks:\n"
        for task_num, title, task_obj in created_tasks:
            result_message += f"{task_num}. {title} (ID: {task_obj.get('id', 'Unknown')})\n"
        result_message += "\n"

    if failed_tasks:
        result_message += "❌ Failed Tasks:\n"
        for error in failed_tasks:
            result_message += f"{error}\n"

    return result_message
