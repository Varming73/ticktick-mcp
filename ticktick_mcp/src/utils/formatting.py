"""
Formatting utilities for TickTick MCP server.

This module provides functions to format TickTick API responses
into human-readable strings for MCP tool responses.
"""

from typing import Dict, Any


def format_task(task: Dict[str, Any]) -> str:
    """
    Format a task object from TickTick for better display.

    Args:
        task: Task dictionary from TickTick API

    Returns:
        Formatted string representation of the task

    Example:
        >>> task = {"id": "123", "title": "Buy groceries", "priority": 5}
        >>> print(format_task(task))
        ID: 123
        Title: Buy groceries
        ...
    """
    formatted = f"ID: {task.get('id', 'No ID')}\n"
    formatted += f"Title: {task.get('title', 'No title')}\n"

    # Add project ID
    formatted += f"Project ID: {task.get('projectId', 'None')}\n"

    # Add dates if available
    if task.get('startDate'):
        formatted += f"Start Date: {task.get('startDate')}\n"
    if task.get('dueDate'):
        formatted += f"Due Date: {task.get('dueDate')}\n"

    # Add priority if available
    priority_map = {0: "None", 1: "Low", 3: "Medium", 5: "High"}
    priority = task.get('priority', 0)
    formatted += f"Priority: {priority_map.get(priority, str(priority))}\n"

    # Add status if available
    status = "Completed" if task.get('status') == 2 else "Active"
    formatted += f"Status: {status}\n"

    # Add content if available
    if task.get('content'):
        formatted += f"\nContent:\n{task.get('content')}\n"

    # Add subtasks if available
    items = task.get('items', [])
    if items:
        formatted += f"\nSubtasks ({len(items)}):\n"
        for i, item in enumerate(items, 1):
            status = "✓" if item.get('status') == 1 else "□"
            formatted += f"{i}. [{status}] {item.get('title', 'No title')}\n"

    return formatted


def format_project(project: Dict[str, Any]) -> str:
    """
    Format a project object from TickTick for better display.

    Args:
        project: Project dictionary from TickTick API

    Returns:
        Formatted string representation of the project

    Example:
        >>> project = {"id": "abc", "name": "Work", "color": "#FF0000"}
        >>> print(format_project(project))
        Name: Work
        ID: abc
        Color: #FF0000
    """
    formatted = f"Name: {project.get('name', 'No name')}\n"
    formatted += f"ID: {project.get('id', 'No ID')}\n"

    # Add color if available
    if project.get('color'):
        formatted += f"Color: {project.get('color')}\n"

    # Add view mode if available
    if project.get('viewMode'):
        formatted += f"View Mode: {project.get('viewMode')}\n"

    # Add closed status if available
    if 'closed' in project:
        formatted += f"Closed: {'Yes' if project.get('closed') else 'No'}\n"

    # Add kind if available
    if project.get('kind'):
        formatted += f"Kind: {project.get('kind')}\n"

    return formatted


# Priority mapping for consistency
PRIORITY_MAP = {0: "None", 1: "Low", 3: "Medium", 5: "High"}
