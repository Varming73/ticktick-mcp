# TickTick MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for TickTick that enables interacting with your TickTick task management system directly through Claude and other MCP clients.

## Features

- 📋 View all your TickTick projects and tasks
- ✏️ Create new projects and tasks through natural language
- 🔄 Update existing task details (title, content, dates, priority)
- ✅ Mark tasks as complete
- 🗑️ Delete tasks and projects
- 🔄 Full integration with TickTick's open API
- 🔌 Seamless integration with Claude and other MCP clients

## Quick Start - Choose Your Platform

This MCP server works with multiple platforms. Choose the setup guide for your use case:

- **[Claude Desktop](#usage-with-claude-for-desktop)** - Personal use on macOS/Windows
- **[Claude Code](#usage-with-claude-code)** - AI-powered IDE with MCP support
- **[LibreChat](#usage-with-librechat-multi-user)** - Multi-user chat platform (Unraid/Docker)

All platforms require the same initial setup steps below.

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- TickTick account with API access
- TickTick API credentials (Client ID, Client Secret, Access Token)

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/jacepark12/ticktick-mcp.git
   cd ticktick-mcp
   ```

2. **Install with uv**:
   ```bash
   # Install uv if you don't have it already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create a virtual environment
   uv venv

   # Activate the virtual environment
   # On macOS/Linux:
   source .venv/bin/activate
   # On Windows:
   .venv\Scripts\activate

   # Install the package
   uv pip install -e .
   ```

3. **Authenticate with TickTick**:
   ```bash
   # Run the authentication flow
   uv run -m ticktick_mcp.cli auth
   ```

   This will:
   - Ask for your TickTick Client ID and Client Secret
   - Open a browser window for you to log in to TickTick
   - Automatically save your access tokens to a `.env` file

4. **Test your configuration**:
   ```bash
   uv run test_server.py
   ```
   This will verify that your TickTick credentials are working correctly.

## Authentication with TickTick

This server uses OAuth2 to authenticate with TickTick. The setup process is straightforward:

1. Register your application at the [TickTick Developer Center](https://developer.ticktick.com/manage)
   - Set the redirect URI to `http://localhost:8000/callback`
   - Note your Client ID and Client Secret

2. Run the authentication command:
   ```bash
   uv run -m ticktick_mcp.cli auth
   ```

3. Follow the prompts to enter your Client ID and Client Secret

4. A browser window will open for you to authorize the application with your TickTick account

5. After authorizing, you'll be redirected back to the application, and your access tokens will be automatically saved to the `.env` file

The server handles token refresh automatically, so you won't need to reauthenticate unless you revoke access or delete your `.env` file.

## Authentication with Dida365

[滴答清单 - Dida365](https://dida365.com/home) is China version of TickTick, and the authentication process is similar to TickTick. Follow these steps to set up Dida365 authentication:

1. Register your application at the [Dida365 Developer Center](https://developer.dida365.com/manage)
   - Set the redirect URI to `http://localhost:8000/callback`
   - Note your Client ID and Client Secret

2. Add environment variables to your `.env` file:
   ```env
   TICKTICK_BASE_URL='https://api.dida365.com/open/v1'
   TICKTICK_AUTH_URL='https://dida365.com/oauth/authorize'
   TICKTICK_TOKEN_URL='https://dida365.com/oauth/token'
   ```

3. Follow the same authentication steps as for TickTick

## Usage with Claude for Desktop

1. Install [Claude for Desktop](https://claude.ai/download)
2. Edit your Claude for Desktop configuration file:

   **macOS**:
   ```bash
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

   **Windows**:
   ```bash
   notepad %APPDATA%\Claude\claude_desktop_config.json
   ```

3. Add the TickTick MCP server configuration, using absolute paths:
   ```json
   {
      "mcpServers": {
         "ticktick": {
            "command": "<absolute path to uv>",
            "args": ["run", "--directory", "<absolute path to ticktick-mcp directory>", "-m", "ticktick_mcp.cli", "run"]
         }
      }
   }
   ```

4. Restart Claude for Desktop

Once connected, you'll see the TickTick MCP server tools available in Claude, indicated by the 🔨 (tools) icon.

## Usage with Claude Code

[Claude Code](https://claude.ai/code) is Anthropic's AI-powered IDE with built-in MCP support.

### Prerequisites

1. **Authenticate with TickTick first**:
   ```bash
   cd /path/to/ticktick-mcp
   uv run -m ticktick_mcp.cli auth
   ```
   This creates a `.env` file with your tokens.

2. **Find your paths**:
   ```bash
   # Find uv path
   which uv

   # Get ticktick-mcp directory path
   cd /path/to/ticktick-mcp && pwd
   ```

### Setup

Add the TickTick MCP server to Claude Code:

```bash
# Basic setup (user scope - available across all projects)
claude mcp add --transport stdio ticktick --scope user \
  -- /path/to/uv run --directory /path/to/ticktick-mcp -m ticktick_mcp.cli run

# Example with actual paths (macOS):
claude mcp add --transport stdio ticktick --scope user \
  -- /Users/yourname/.local/bin/uv run --directory /Users/yourname/projects/ticktick-mcp -m ticktick_mcp.cli run
```

**Scope Options:**
- `--scope user` (recommended): Available across all your projects
- `--scope local`: Only available in current project
- `--scope project`: Shared with team via `.mcp.json` (requires authentication setup for each team member)

### Managing Your Server

```bash
# List all configured servers
claude mcp list

# Get details for ticktick server
claude mcp get ticktick

# Remove the server
claude mcp remove ticktick

# Check server status in Claude Code
/mcp
```

### Using TickTick in Claude Code

Once configured, you can use natural language in Claude Code:
- "Show me all my TickTick projects"
- "Create a task to review the PR in my Work project"
- "What tasks are due today?"

The 🔨 icon indicates MCP tools are available.

## Usage with LibreChat (Multi-User)

LibreChat is a multi-user chat platform that supports MCP servers with OAuth2 authentication. This TickTick MCP server has been designed to work seamlessly with LibreChat's multi-user environment.

### Key Features for LibreChat

- **Per-User Authentication**: Each user authenticates with their own TickTick account via OAuth2
- **Process Isolation**: LibreChat spawns separate MCP processes per user with isolated tokens
- **Automatic Token Management**: LibreChat handles token storage and injection into process environment
- **Docker Compatible**: Designed to run in containerized environments (Docker, Unraid, etc.)

### Installation Options

#### Option 1: Using npx (Recommended)

Install directly from npm:
```bash
npx @varming73/ticktick-mcp
```

Or install globally:
```bash
npm install -g @varming73/ticktick-mcp
```

The npx installation will:
- ✅ Automatically check for Python 3.10+
- ✅ Install all Python dependencies
- ✅ Set up the MCP server executable
- ✅ Work seamlessly with LibreChat's configuration

#### Option 2: Manual Installation

Clone and install from source:
```bash
git clone https://github.com/Varming73/ticktick-mcp.git
cd ticktick-mcp
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Server Setup (For LibreChat Administrators)

1. **Register OAuth Application** at [TickTick Developer Center](https://developer.ticktick.com/manage):
   - Set redirect URI to: `http://your-librechat-domain:3080/oauth/callback`
   - Note your Client ID and Client Secret
   - For local testing: `http://localhost:3080/oauth/callback`

2. **Configure LibreChat Environment**:

   Add to your LibreChat `.env` file or Docker environment:
   ```env
   TICKTICK_CLIENT_ID=your_client_id_here
   TICKTICK_CLIENT_SECRET=your_client_secret_here
   ```

3. **Add MCP Server to LibreChat Configuration**:

   **If you installed via npx:**
   ```yaml
   version: 1.0.0

   mcpServers:
     ticktick:
       type: stdio
       command: npx
       args:
         - "@varming73/ticktick-mcp"

       env:
         TICKTICK_CLIENT_ID: ${TICKTICK_CLIENT_ID}
         TICKTICK_CLIENT_SECRET: ${TICKTICK_CLIENT_SECRET}
         # User tokens will be injected automatically by LibreChat
   ```

   **If you installed manually with uv:**
   ```yaml
   version: 1.0.0

   mcpServers:
     ticktick:
       type: stdio
       command: uv
       args:
         - "run"
         - "--directory"
         - "/app/ticktick-mcp"  # Update path for your setup
         - "-m"
         - "ticktick_mcp.cli"
         - "run"

       env:
         TICKTICK_CLIENT_ID: ${TICKTICK_CLIENT_ID}
         TICKTICK_CLIENT_SECRET: ${TICKTICK_CLIENT_SECRET}

       oauth:
         authorization_url: https://ticktick.com/oauth/authorize
         token_url: https://ticktick.com/oauth/token
         client_id: ${TICKTICK_CLIENT_ID}
         client_secret: ${TICKTICK_CLIENT_SECRET}
         scope: "tasks:read tasks:write"
         redirect_uri: http://localhost:3080/oauth/callback

       startup: false
       timeout: 30000
       initTimeout: 10000
   ```

5. **Docker Setup** (if using Docker):

   Ensure the ticktick-mcp directory is mounted and accessible:
   ```yaml
   volumes:
     - /path/to/ticktick-mcp:/app/ticktick-mcp
   ```

6. **Restart LibreChat** to load the new MCP server configuration.

### User Setup (For LibreChat End Users)

1. **Authentication**:
   - When first using TickTick commands in LibreChat, you'll be prompted to authenticate
   - Click the "Authenticate" button in the LibreChat UI
   - You'll be redirected to TickTick to authorize access
   - After authorization, return to LibreChat - you're ready to use TickTick!

2. **Using TickTick in Chat**:

   Once authenticated, you can use natural language commands:
   - "Show me all my TickTick projects"
   - "Create a task called 'Review PR' in my Work project with high priority"
   - "What tasks are due today?"
   - "Show me my high priority tasks"
   - "Mark task X as complete"

### Multi-User Considerations

- **Isolated Data**: Each user's TickTick data is completely isolated - users can only access their own tasks and projects
- **Token Lifetime**: Access tokens have a limited lifetime. Users may need to re-authenticate periodically
- **Token Refresh**: The server automatically attempts to refresh tokens, but refresh tokens also expire
- **Process Per User**: LibreChat spawns a new MCP process for each user session with their specific tokens

### Troubleshooting

**"TICKTICK_ACCESS_TOKEN not found in environment"**
- User needs to authenticate via LibreChat UI
- Click the authenticate button when prompted
- Verify OAuth2 redirect URI matches your LibreChat deployment

**"TickTick API connection failed"**
- Verify TICKTICK_CLIENT_ID and TICKTICK_CLIENT_SECRET are set in LibreChat's server environment
- Check that the OAuth application is properly configured in TickTick Developer Center
- Ensure redirect URI in TickTick app matches LibreChat's callback URL

**Token Refresh Issues**
- Refresh tokens expire after a period of inactivity
- Users will need to re-authenticate when refresh tokens expire
- This is a TickTick API limitation, not a bug in the MCP server

**Docker/Container Issues**
- Ensure the ticktick-mcp directory path in the config matches the container's mount path
- Verify `uv` is available in the container's PATH
- Check container logs for Python/dependency errors

### Alternative: Manual Token Entry (customUserVars)

If LibreChat's OAuth2 integration has issues, you can use manual token entry instead. See `librechat_config.yaml` for the alternative configuration using `customUserVars`. Users will need to:

1. Get their tokens from [TickTick Developer Portal](https://developer.ticktick.com/manage)
2. Enter tokens in LibreChat's MCP settings
3. Tokens will be stored per-user by LibreChat

### Dida365 Support (Chinese TickTick)

For Dida365 users, update the OAuth URLs in your LibreChat configuration:
```yaml
oauth:
  authorization_url: https://dida365.com/oauth/authorize
  token_url: https://dida365.com/oauth/token
  # ... rest of config

env:
  TICKTICK_BASE_URL: "https://api.dida365.com/open/v1"
  TICKTICK_AUTH_URL: "https://dida365.com/oauth/authorize"
  TICKTICK_TOKEN_URL: "https://dida365.com/oauth/token"
```

## Available MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_projects` | List all your TickTick projects | None |
| `get_project` | Get details about a specific project | `project_id` |
| `get_project_tasks` | List all tasks in a project | `project_id` |
| `get_task` | Get details about a specific task | `project_id`, `task_id` |
| `create_task` | Create a new task | `title`, `project_id`, `content` (optional), `start_date` (optional), `due_date` (optional), `priority` (optional) |
| `update_task` | Update an existing task | `task_id`, `project_id`, `title` (optional), `content` (optional), `start_date` (optional), `due_date` (optional), `priority` (optional) |
| `complete_task` | Mark a task as complete | `project_id`, `task_id` |
| `delete_task` | Delete a task | `project_id`, `task_id` |
| `create_project` | Create a new project | `name`, `color` (optional), `view_mode` (optional) |
| `update_project` | Update an existing project | `project_id`, `name` (optional), `color` (optional), `view_mode` (optional) |
| `delete_project` | Delete a project | `project_id` |

## Task-specific MCP Tools

### Task Retrieval & Search
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_all_tasks` | Get all tasks from all projects | None |
| `get_tasks_by_priority` | Get tasks filtered by priority level | `priority_id` (0: None, 1: Low, 3: Medium, 5: High) |
| `search_tasks` | Search tasks by title, content, or subtasks | `search_term` |

### Date-Based Task Retrieval
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_tasks_due_today` | Get all tasks due today | None |
| `get_tasks_due_tomorrow` | Get all tasks due tomorrow | None |
| `get_tasks_due_in_days` | Get tasks due in exactly X days | `days` (0 = today, 1 = tomorrow, etc.) |
| `get_tasks_due_this_week` | Get tasks due within the next 7 days | None |
| `get_overdue_tasks` | Get all overdue tasks | None |

### Getting Things Done (GTD) Framework
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_engaged_tasks` | Get "engaged" tasks (high priority or overdue) | None |
| `get_next_tasks` | Get "next" tasks (medium priority or due tomorrow) | None |
| `batch_create_tasks` | Create multiple tasks at once | `tasks` (list of task dictionaries) |

## Example Prompts for Claude

Here are some example prompts to use with Claude after connecting the TickTick MCP server:

### General

- "Show me all my TickTick projects"
- "Create a new task called 'Finish MCP server documentation' in my work project with high priority"
- "List all tasks in my personal project"
- "Mark the task 'Buy groceries' as complete"
- "Create a new project called 'Vacation Planning' with a blue color"
- "Update my 'Work' project to use kanban view and change the color to green"
- "When is my next deadline in TickTick?"

### Task Filtering Queries

- "What tasks do I have due today?"
- "Show me everything that's overdue"
- "Show me all tasks due this week"
- "Search for tasks about 'project alpha'"
- "Show me all tasks with 'client' in the title or description"
- "Show me all my high priority tasks"

### GTD Workflow

Following David Allen's "Getting Things Done" framework, manage an Engaged and Next actions.

- Engaged will retrieve tasks of high priority, due today or overdue.
- Next will retrieve medium priority or due tomorrow.
- Break down complex actions into smaller actions with batch_creation

For example:

- "Time block the rest of my day from 2-8pm with items from my engaged list"
- "Walk me through my next actions and help my identify what I should focus on tomorrow?" 
- "Break down this project into 5 smaller actionable tasks"

## Development

### Project Structure

```
ticktick-mcp/
├── .env.template          # Template for environment variables
├── README.md              # Project documentation
├── requirements.txt       # Project dependencies
├── setup.py               # Package setup file
├── test_server.py         # Test script for server configuration
└── ticktick_mcp/          # Main package
    ├── __init__.py        # Package initialization
    ├── authenticate.py    # OAuth authentication utility
    ├── cli.py             # Command-line interface
    └── src/               # Source code
        ├── __init__.py    # Module initialization
        ├── auth.py        # OAuth authentication implementation
        ├── server.py      # MCP server implementation
        └── ticktick_client.py  # TickTick API client
```

### Authentication Flow

The project implements a complete OAuth 2.0 flow for TickTick:

1. **Initial Setup**: User provides their TickTick API Client ID and Secret
2. **Browser Authorization**: User is redirected to TickTick to grant access
3. **Token Reception**: A local server receives the OAuth callback with the authorization code
4. **Token Exchange**: The code is exchanged for access and refresh tokens
5. **Token Storage**: Tokens are securely stored in the local `.env` file
6. **Token Refresh**: The client automatically refreshes the access token when it expires

This simplifies the user experience by handling the entire OAuth flow programmatically.

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
