"""
TickTick MCP Server - Main entry point.

This module initializes the FastMCP server and registers all tools,
resources, and prompts for TickTick integration.
"""

import logging
from datetime import datetime

from mcp.server.fastmcp import FastMCP

from .client_manager import get_client, initialize_client

# Import tool functions from modularized files
from .tools.projects import (
    get_projects_tool,
    get_project_tool,
    get_project_tasks_tool,
    create_project_tool,
    update_project_tool,
    delete_project_tool
)
from .tools.tasks import (
    get_task_tool,
    create_task_tool,
    update_task_tool,
    complete_task_tool,
    delete_task_tool,
    create_subtask_tool,
    get_all_tasks_tool,
    get_tasks_by_priority_tool,
    get_tasks_due_today_tool,
    get_overdue_tasks_tool,
    get_tasks_due_tomorrow_tool,
    get_tasks_due_in_days_tool,
    get_tasks_due_this_week_tool,
    search_tasks_tool,
    batch_create_tasks_tool
)
from .tools.gtd import (
    get_engaged_tasks_tool,
    get_next_tasks_tool
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server with capabilities
mcp = FastMCP("ticktick")


# ============================================================================
# MCP TOOL REGISTRATION
# ============================================================================

# Project Tools
@mcp.tool()
async def get_projects() -> str:
    """Get all projects from TickTick."""
    return await get_projects_tool()


@mcp.tool()
async def get_project(project_id: str) -> str:
    """Get details about a specific project."""
    return await get_project_tool(project_id)


@mcp.tool()
async def get_project_tasks(project_id: str) -> str:
    """Get all tasks in a specific project."""
    return await get_project_tasks_tool(project_id)


@mcp.tool()
async def create_project(name: str, color: str = "#F18181", view_mode: str = "list") -> str:
    """Create a new project in TickTick."""
    return await create_project_tool(name, color, view_mode)


@mcp.tool()
async def update_project(
    project_id: str,
    name: str = None,
    color: str = None,
    view_mode: str = None
) -> str:
    """Update an existing project in TickTick."""
    return await update_project_tool(project_id, name, color, view_mode)


@mcp.tool()
async def delete_project(project_id: str) -> str:
    """Delete a project."""
    return await delete_project_tool(project_id)


# Task CRUD Tools
@mcp.tool()
async def get_task(project_id: str, task_id: str) -> str:
    """Get details about a specific task."""
    return await get_task_tool(project_id, task_id)


@mcp.tool()
async def create_task(
    title: str,
    project_id: str,
    content: str = None,
    start_date: str = None,
    due_date: str = None,
    priority: int = 0
) -> str:
    """Create a new task in TickTick."""
    return await create_task_tool(title, project_id, content, start_date, due_date, priority)


@mcp.tool()
async def update_task(
    task_id: str,
    project_id: str,
    title: str = None,
    content: str = None,
    start_date: str = None,
    due_date: str = None,
    priority: int = None
) -> str:
    """Update an existing task in TickTick."""
    return await update_task_tool(task_id, project_id, title, content, start_date, due_date, priority)


@mcp.tool()
async def complete_task(project_id: str, task_id: str) -> str:
    """Mark a task as complete."""
    return await complete_task_tool(project_id, task_id)


@mcp.tool()
async def delete_task(project_id: str, task_id: str) -> str:
    """Delete a task."""
    return await delete_task_tool(project_id, task_id)


@mcp.tool()
async def create_subtask(
    subtask_title: str,
    parent_task_id: str,
    project_id: str,
    content: str = None,
    priority: int = 0
) -> str:
    """Create a subtask for a parent task."""
    return await create_subtask_tool(subtask_title, parent_task_id, project_id, content, priority)


# Task Search and Filter Tools
@mcp.tool()
async def get_all_tasks() -> str:
    """Get all tasks from TickTick."""
    return await get_all_tasks_tool()


@mcp.tool()
async def get_tasks_by_priority(priority_id: int) -> str:
    """Get all tasks from TickTick by priority."""
    return await get_tasks_by_priority_tool(priority_id)


@mcp.tool()
async def get_tasks_due_today() -> str:
    """Get all tasks from TickTick that are due today."""
    return await get_tasks_due_today_tool()


@mcp.tool()
async def get_overdue_tasks() -> str:
    """Get all overdue tasks from TickTick."""
    return await get_overdue_tasks_tool()


@mcp.tool()
async def get_tasks_due_tomorrow() -> str:
    """Get all tasks from TickTick that are due tomorrow."""
    return await get_tasks_due_tomorrow_tool()


@mcp.tool()
async def get_tasks_due_in_days(days: int) -> str:
    """Get all tasks from TickTick that are due in exactly X days."""
    return await get_tasks_due_in_days_tool(days)


@mcp.tool()
async def get_tasks_due_this_week() -> str:
    """Get all tasks from TickTick that are due within the next 7 days."""
    return await get_tasks_due_this_week_tool()


@mcp.tool()
async def search_tasks(search_term: str) -> str:
    """Search for tasks in TickTick by title, content, or subtask titles."""
    return await search_tasks_tool(search_term)


@mcp.tool()
async def batch_create_tasks(tasks: List[Dict[str, Any]]) -> str:
    """Create multiple tasks in TickTick at once."""
    return await batch_create_tasks_tool(tasks)


# GTD Framework Tools
@mcp.tool()
async def get_engaged_tasks() -> str:
    """Get all tasks from TickTick that are 'Engaged' (high priority, due today, or overdue)."""
    return await get_engaged_tasks_tool()


@mcp.tool()
async def get_next_tasks() -> str:
    """Get all tasks from TickTick that are 'Next' (medium priority or due tomorrow)."""
    return await get_next_tasks_tool()


# ============================================================================
# MCP RESOURCES
# ============================================================================

@mcp.resource("ticktick://projects")
async def list_projects_resource() -> str:
    """
    Expose all projects as an MCP resource.

    Resources allow LLMs to access data without explicitly calling tools.
    This resource provides a list of all projects in JSON format.
    """
    client = get_client()
    projects_result = client.get_projects()

    if isinstance(projects_result, dict) and 'error' in projects_result:
        return f"Error: {projects_result['error']}"

    import json
    return json.dumps(projects_result, indent=2)


@mcp.resource("ticktick://project/{project_id}")
async def get_project_resource(project_id: str) -> str:
    """
    Expose a specific project with its tasks as an MCP resource.

    Args:
        project_id: The project ID to retrieve
    """
    client = get_client()
    project_data = client.get_project_with_data(project_id)

    if 'error' in project_data:
        return f"Error: {project_data['error']}"

    import json
    return json.dumps(project_data, indent=2)


# ============================================================================
# MCP PROMPTS
# ============================================================================

@mcp.prompt()
async def daily_review() -> str:
    """
    Generate a daily review prompt with today's tasks and priorities.

    This prompt helps users review their engaged and next tasks for the day,
    following GTD (Getting Things Done) methodology.
    """
    # Get engaged tasks (high priority / overdue / due today)
    engaged = await get_engaged_tasks_tool()

    # Get next tasks (medium priority / due tomorrow)
    next_tasks = await get_next_tasks_tool()

    prompt = f"""# Daily Review - {datetime.now().strftime('%Y-%m-%d')}

## 🔥 Engaged Tasks (Do First)
These are your highest priority tasks - high priority items, overdue tasks, and tasks due today:

{engaged}

## 📋 Next Tasks (Do After Engaged)
These are your medium priority tasks and tasks due tomorrow:

{next_tasks}

## Review Questions
1. Which engaged tasks can you complete today?
2. Are there any engaged tasks you need to reschedule or break down?
3. Which next tasks should you prepare for?
4. Do you need to adjust any priorities?
"""
    return prompt


@mcp.prompt()
async def weekly_planning() -> str:
    """
    Generate a weekly planning prompt with tasks due this week.

    This prompt helps users plan their week by reviewing all tasks
    due in the next 7 days.
    """
    from datetime import datetime

    # Get tasks due this week
    weekly_tasks = await get_tasks_due_this_week_tool()

    # Get overdue tasks
    overdue = await get_overdue_tasks_tool()

    prompt = f"""# Weekly Planning - Week of {datetime.now().strftime('%Y-%m-%d')}

## ⚠️ Overdue Tasks
Deal with these first:

{overdue}

## 📅 Tasks Due This Week
Here are all tasks due in the next 7 days:

{weekly_tasks}

## Planning Questions
1. What are your top 3 priorities for this week?
2. Which overdue tasks need immediate attention?
3. Do you need to reschedule or delegate any tasks?
4. What resources or support do you need?
5. Are there any potential blockers?
"""
    return prompt


# ============================================================================
# SERVER STARTUP
# ============================================================================

def main():
    """Main entry point for the MCP server."""
    # Initialize the TickTick client
    if not initialize_client():
        logger.error("Failed to initialize TickTick client. Please check your API credentials.")
        return

    # Run the server
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
