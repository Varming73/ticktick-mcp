import os
import json
import base64
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Set up logging
logger = logging.getLogger(__name__)


class TaskValidator:
    """Validator for task and project input data."""
    
    MAX_TITLE_LENGTH = 500
    MAX_CONTENT_LENGTH = 10000
    MAX_PROJECT_NAME_LENGTH = 200
    VALID_PRIORITIES = (0, 1, 3, 5)
    
    @staticmethod
    def validate_task_title(title: str) -> None:
        """
        Validate task title.
        
        Args:
            title: Task title to validate
            
        Raises:
            ValueError: If title is invalid
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        if len(title) > TaskValidator.MAX_TITLE_LENGTH:
            raise ValueError(
                f"Task title must be {TaskValidator.MAX_TITLE_LENGTH} characters or less "
                f"(current: {len(title)} characters)"
            )
    
    @staticmethod
    def validate_project_name(name: str) -> None:
        """
        Validate project name.
        
        Args:
            name: Project name to validate
            
        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")
        if len(name) > TaskValidator.MAX_PROJECT_NAME_LENGTH:
            raise ValueError(
                f"Project name must be {TaskValidator.MAX_PROJECT_NAME_LENGTH} characters or less "
                f"(current: {len(name)} characters)"
            )
    
    @staticmethod
    def validate_content(content: Optional[str]) -> None:
        """
        Validate content field.
        
        Args:
            content: Content to validate
            
        Raises:
            ValueError: If content is invalid
        """
        if content and len(content) > TaskValidator.MAX_CONTENT_LENGTH:
            raise ValueError(
                f"Content must be {TaskValidator.MAX_CONTENT_LENGTH} characters or less "
                f"(current: {len(content)} characters)"
            )
    
    @staticmethod
    def validate_priority(priority: int) -> None:
        """
        Validate priority value.
        
        Args:
            priority: Priority value to validate
            
        Raises:
            ValueError: If priority is invalid
        """
        if priority not in TaskValidator.VALID_PRIORITIES:
            raise ValueError(
                f"Priority must be one of {TaskValidator.VALID_PRIORITIES} "
                f"(0=None, 1=Low, 3=Medium, 5=High), got {priority}"
            )
    
    @staticmethod
    def validate_date(date_str: Optional[str], field_name: str) -> None:
        """
        Validate date format.
        
        Args:
            date_str: Date string to validate (ISO format)
            field_name: Name of the field for error messages
            
        Raises:
            ValueError: If date format is invalid
        """
        if not date_str:
            return
        
        try:
            # Try parsing with timezone
            if date_str.endswith('Z'):
                datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            elif '+' in date_str or date_str.count(':') >= 2:
                datetime.fromisoformat(date_str)
            else:
                # Try as date only
                datetime.fromisoformat(date_str)
        except (ValueError, AttributeError) as e:
            raise ValueError(
                f"{field_name} must be in ISO format (e.g., 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:mm:ss' or with timezone). "
                f"Got: {date_str}"
            )

class TickTickClient:
    """
    Client for the TickTick API using OAuth2 authentication.
    """
    
    def __init__(self):
        """
        Initialize TickTick client from environment variables.

        In LibreChat multi-user mode:
        - TICKTICK_CLIENT_ID and TICKTICK_CLIENT_SECRET are system-wide (from server env)
        - TICKTICK_ACCESS_TOKEN and TICKTICK_REFRESH_TOKEN are per-user (from LibreChat OAuth)

        LibreChat spawns separate processes per user with user-specific tokens in env vars.
        """
        # Read from environment variables (set by LibreChat per user)
        # No load_dotenv() - LibreChat sets process env directly
        self.client_id = os.getenv("TICKTICK_CLIENT_ID")
        self.client_secret = os.getenv("TICKTICK_CLIENT_SECRET")
        self.access_token = os.getenv("TICKTICK_ACCESS_TOKEN")
        self.refresh_token = os.getenv("TICKTICK_REFRESH_TOKEN")

        if not self.access_token:
            raise ValueError(
                "TICKTICK_ACCESS_TOKEN environment variable is not set. "
                "In LibreChat, this should be provided automatically via OAuth. "
                "Please authenticate with TickTick in the LibreChat UI. "
                "For Claude Desktop, run 'uv run -m ticktick_mcp.cli auth' to set up credentials."
            )

        self.base_url = os.getenv("TICKTICK_BASE_URL") or "https://api.ticktick.com/open/v1"
        self.token_url = os.getenv("TICKTICK_TOKEN_URL") or "https://ticktick.com/oauth/token"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept-Encoding": None,
            "User-Agent": 'curl/8.7.1'
        }
        
        # Initialize session with connection pooling and retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,  # Retry up to 3 times
            backoff_factor=1,  # Wait 1s, 2s, 4s between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["GET", "POST", "PUT", "DELETE"]  # Retry on all methods
        )
        adapter = HTTPAdapter(
            pool_connections=10,  # Number of connection pools to cache
            pool_maxsize=20,  # Maximum number of connections to save in the pool
            max_retries=retry_strategy
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def _refresh_access_token(self) -> bool:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.refresh_token:
            logger.warning("No refresh token available. Cannot refresh access token.")
            return False
            
        if not self.client_id or not self.client_secret:
            logger.warning("Client ID or Client Secret missing. Cannot refresh access token.")
            return False
            
        # Prepare the token request
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        # Prepare Basic Auth credentials
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            # Send the token request
            response = requests.post(self.token_url, data=token_data, headers=headers)
            response.raise_for_status()
            
            # Parse the response
            tokens = response.json()
            
            # Update the tokens
            self.access_token = tokens.get('access_token')
            if 'refresh_token' in tokens:
                self.refresh_token = tokens.get('refresh_token')
                
            # Update the headers
            self.headers["Authorization"] = f"Bearer {self.access_token}"
            
            # Save the tokens to the .env file
            self._save_tokens_to_env(tokens)
            
            logger.info("Access token refreshed successfully.")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error refreshing access token: {e}")
            return False
    
    def _save_tokens_to_env(self, tokens: Dict[str, str]) -> None:
        """
        Update instance tokens after refresh.

        NOTE: In LibreChat multi-user mode, tokens cannot be persisted back to
        environment variables. The refreshed tokens only exist for the lifetime
        of this process. Users will need to re-authenticate when tokens expire.

        For production LibreChat deployments, consider implementing external
        token storage with LibreChat's database or a separate token service.

        Args:
            tokens: A dictionary containing the access_token and optionally refresh_token
        """
        # Update instance variables with new tokens
        self.access_token = tokens.get('access_token', self.access_token)
        if 'refresh_token' in tokens:
            self.refresh_token = tokens.get('refresh_token', self.refresh_token)

        # Update authorization header
        self.headers["Authorization"] = f"Bearer {self.access_token}"

        # Log warning about token persistence
        logger.warning(
            "Access token refreshed successfully. "
            "NOTE: Refreshed tokens are NOT persisted in LibreChat multi-user mode. "
            "User should re-authenticate when tokens expire."
        )

        # Do NOT write to .env file in multi-user mode
        # LibreChat manages tokens in its database
    
    def _make_request(self, method: str, endpoint: str, data=None) -> Dict:
        """
        Makes a request to the TickTick API using connection pooling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request data (for POST, PUT)
        
        Returns:
            API response as a dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Make the request using session (with connection pooling)
            if method == "GET":
                response = self.session.get(url, headers=self.headers)
            elif method == "POST":
                response = self.session.post(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = self.session.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check if the request was unauthorized (401)
            if response.status_code == 401:
                logger.info("Access token expired. Attempting to refresh...")
                
                # Try to refresh the access token
                if self._refresh_access_token():
                    # Retry the request with the new token
                    if method == "GET":
                        response = self.session.get(url, headers=self.headers)
                    elif method == "POST":
                        response = self.session.post(url, headers=self.headers, json=data)
                    elif method == "DELETE":
                        response = self.session.delete(url, headers=self.headers)
            
            # Raise an exception for 4xx/5xx status codes
            response.raise_for_status()
            
            # Return empty dict for 204 No Content
            if response.status_code == 204 or response.text == "":
                return {}
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            # HTTP errors (4xx, 5xx) - parse status code for specific handling
            status_code = e.response.status_code if e.response else None
            error_msg = str(e)
            
            logger.error(f"API HTTP error {status_code}: {error_msg}")
            
            # Categorize errors based on status code for tool-level handling
            if status_code == 401:
                return {
                    "error": "Authentication failed. Token expired or invalid.",
                    "status_code": 401,
                    "type": "auth"
                }
            elif status_code == 403:
                return {
                    "error": "Permission denied. You don't have access to this resource.",
                    "status_code": 403,
                    "type": "permission"
                }
            elif status_code == 404:
                return {
                    "error": "Resource not found. It may have been deleted.",
                    "status_code": 404,
                    "type": "not_found"
                }
            elif status_code and status_code >= 500:
                return {
                    "error": f"TickTick server error ({status_code}). Please try again later.",
                    "status_code": status_code,
                    "type": "server_error"
                }
            else:
                return {
                    "error": error_msg,
                    "status_code": status_code,
                    "type": "api"
                }
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Network connection failed: {e}")
            return {
                "error": f"Network connection failed: {str(e)}",
                "status_code": None,
                "type": "network"
            }
        
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timed out: {e}")
            return {
                "error": f"Request timed out: {str(e)}",
                "status_code": None,
                "type": "timeout"
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "error": str(e),
                "status_code": None,
                "type": "unknown"
            }
    
    # Project methods
    def get_projects(self) -> Union[List[Dict], Dict[str, Any]]:
        """Gets all projects for the user. Returns list of projects or error dict."""
        return self._make_request("GET", "/project")
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Gets a specific project by ID. Returns project dict or error dict."""
        return self._make_request("GET", f"/project/{project_id}")
    
    def get_project_with_data(self, project_id: str) -> Dict[str, Any]:
        """Gets project with tasks and columns. Returns project dict or error dict."""
        return self._make_request("GET", f"/project/{project_id}/data")
    
    def create_project(self, name: str, color: str = "#F18181", view_mode: str = "list", kind: str = "TASK") -> Dict[str, Any]:
        """
        Creates a new project with input validation.
        
        Args:
            name: Project name (required, max 200 chars)
            color: Project color in hex format
            view_mode: View mode (list, kanban, timeline)
            kind: Project kind (TASK, NOTE)
            
        Returns:
            Created project dict or error dict
            
        Raises:
            ValueError: If validation fails
        """
        # Validate input
        TaskValidator.validate_project_name(name)
        
        data = {
            "name": name,
            "color": color,
            "viewMode": view_mode,
            "kind": kind
        }
        return self._make_request("POST", "/project", data)
    
    def update_project(self, project_id: str, name: Optional[str] = None, color: Optional[str] = None, 
                       view_mode: Optional[str] = None, kind: Optional[str] = None) -> Dict[str, Any]:
        """
        Updates an existing project with input validation.
        
        Args:
            project_id: Project ID to update
            name: New project name (optional, max 200 chars if provided)
            color: New project color
            view_mode: New view mode
            kind: New project kind
            
        Returns:
            Updated project dict or error dict
            
        Raises:
            ValueError: If validation fails
        """
        data: Dict[str, Any] = {}
        if name:
            TaskValidator.validate_project_name(name)
            data["name"] = name
        if color:
            data["color"] = color
        if view_mode:
            data["viewMode"] = view_mode
        if kind:
            data["kind"] = kind
            
        return self._make_request("POST", f"/project/{project_id}", data)
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Deletes a project."""
        return self._make_request("DELETE", f"/project/{project_id}")
    
    # Task methods
    def get_task(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """Gets a specific task by project ID and task ID. Returns task dict or error dict."""
        return self._make_request("GET", f"/project/{project_id}/task/{task_id}")
    
    def create_task(self, title: str, project_id: str, content: Optional[str] = None, 
                   start_date: Optional[str] = None, due_date: Optional[str] = None, 
                   priority: int = 0, is_all_day: bool = False) -> Dict[str, Any]:
        """
        Creates a new task with input validation.
        
        Args:
            title: Task title (required, max 500 chars)
            project_id: Project ID to create task in
            content: Task content/description (optional, max 10000 chars)
            start_date: Start date in ISO format
            due_date: Due date in ISO format
            priority: Priority level (0=None, 1=Low, 3=Medium, 5=High)
            is_all_day: Whether task is all-day event
            
        Returns:
            Created task dict or error dict
            
        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        TaskValidator.validate_task_title(title)
        TaskValidator.validate_content(content)
        TaskValidator.validate_priority(priority)
        TaskValidator.validate_date(start_date, "start_date")
        TaskValidator.validate_date(due_date, "due_date")
        
        data: Dict[str, Any] = {
            "title": title,
            "projectId": project_id
        }
        
        if content:
            data["content"] = content
        if start_date:
            data["startDate"] = start_date
        if due_date:
            data["dueDate"] = due_date
        if priority is not None:
            data["priority"] = priority
        if is_all_day is not None:
            data["isAllDay"] = is_all_day
            
        return self._make_request("POST", "/task", data)
    
    def update_task(self, task_id: str, project_id: str, title: Optional[str] = None, 
                   content: Optional[str] = None, priority: Optional[int] = None, 
                   start_date: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Updates an existing task with input validation.
        
        Args:
            task_id: Task ID to update
            project_id: Project ID containing the task
            title: New task title (optional, max 500 chars if provided)
            content: New task content (optional, max 10000 chars if provided)
            priority: New priority level (0=None, 1=Low, 3=Medium, 5=High)
            start_date: New start date in ISO format
            due_date: New due date in ISO format
            
        Returns:
            Updated task dict or error dict
            
        Raises:
            ValueError: If validation fails
        """
        # Validate inputs if provided
        if title:
            TaskValidator.validate_task_title(title)
        if content:
            TaskValidator.validate_content(content)
        if priority is not None:
            TaskValidator.validate_priority(priority)
        if start_date:
            TaskValidator.validate_date(start_date, "start_date")
        if due_date:
            TaskValidator.validate_date(due_date, "due_date")
        
        data: Dict[str, Any] = {
            "id": task_id,
            "projectId": project_id
        }
        
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        if priority is not None:
            data["priority"] = priority
        if start_date:
            data["startDate"] = start_date
        if due_date:
            data["dueDate"] = due_date
            
        return self._make_request("POST", f"/task/{task_id}", data)
    
    def complete_task(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """Marks a task as complete. Returns success dict or error dict."""
        return self._make_request("POST", f"/project/{project_id}/task/{task_id}/complete")
    
    def delete_task(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """Deletes a task. Returns success dict or error dict."""
        return self._make_request("DELETE", f"/project/{project_id}/task/{task_id}")
    
    def create_subtask(self, subtask_title: str, parent_task_id: str, project_id: str, 
                      content: Optional[str] = None, priority: int = 0) -> Dict[str, Any]:
        """
        Creates a subtask for a parent task within the same project with input validation.
        
        Args:
            subtask_title: Title of the subtask (max 500 chars)
            parent_task_id: ID of the parent task
            project_id: ID of the project (must be same for both parent and subtask)
            content: Optional content/description for the subtask (max 10000 chars)
            priority: Priority level (0=None, 1=Low, 3=Medium, 5=High)
        
        Returns:
            API response as a dictionary containing the created subtask or error dict
            
        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        TaskValidator.validate_task_title(subtask_title)
        TaskValidator.validate_content(content)
        TaskValidator.validate_priority(priority)
        
        data: Dict[str, Any] = {
            "title": subtask_title,
            "projectId": project_id,
            "parentId": parent_task_id
        }
        
        if content:
            data["content"] = content
        if priority is not None:
            data["priority"] = priority
            
        return self._make_request("POST", "/task", data)