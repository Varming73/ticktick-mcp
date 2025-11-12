# TickTick MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for TickTick that enables interacting with your TickTick task management system directly through Claude and other MCP clients.

> **Note**: This is a fork of [jacepark12/ticktick-mcp](https://github.com/jacepark12/ticktick-mcp) with enhancements for multi-user support (LibreChat), npx installation, input validation, connection pooling, and comprehensive error handling.
> 
> Original work by [Jaesung Park](https://github.com/jacepark12).

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

- Python 3.10 or higher (automatically checked during npx installation)
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer (only needed for manual installation)
- TickTick account with API access
- TickTick API credentials (Client ID, Client Secret, Access Token)

## Installation

### Option 1: Quick Install with npx (Recommended)

Install and set up in one command - works with **all platforms**:

```bash
npx @varming/ticktick-mcp
```

This will:
- ✅ Automatically check for Python 3.10+
- ✅ Install all Python dependencies
- ✅ Make the server ready for Claude Desktop, Claude Code, and LibreChat

**Or install globally:**
```bash
npm install -g @varming/ticktick-mcp
```

### Option 2: Manual Installation with uv

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Varming73/ticktick-mcp.git
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

## Authentication

**Authenticate with TickTick** (required for all installation methods):

```bash
# If installed with npx globally:
ticktick-mcp auth

# If installed with uv:
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

3. Add the TickTick MCP server configuration:

   **Option A: If you installed with npx:**
   ```json
   {
      "mcpServers": {
         "ticktick": {
            "command": "npx",
            "args": ["@varming/ticktick-mcp"]
         }
      }
   }
   ```

   **Option B: If you installed manually with uv:**
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

**Authenticate with TickTick first**:
```bash
# If installed with npx globally:
ticktick-mcp auth

# If installed with uv:
cd /path/to/ticktick-mcp
uv run -m ticktick_mcp.cli auth
```
This creates a `.env` file with your tokens.

### Setup

Add the TickTick MCP server to Claude Code:

**Option A: If you installed with npx (simplest):**
```bash
claude mcp add --transport stdio ticktick --scope user \
  -- npx @varming/ticktick-mcp
```

**Option B: If you installed manually with uv:**
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

### ⚠️ Known Limitation: Token Refresh Persistence

**IMPORTANT**: There is currently a known limitation with token refresh in LibreChat multi-user mode:

- ✅ **Initial authentication works perfectly** - Users can authenticate via OAuth and start using TickTick
- ⚠️ **Token refresh limitation** - When access tokens expire and are refreshed, the new tokens are NOT persisted back to LibreChat's storage
- 🔄 **Impact** - Users may need to re-authenticate more frequently than expected (when refresh tokens expire or LibreChat restarts)

**Status**: This is a known architectural issue. The MCP server successfully refreshes tokens, but in LibreChat's multi-user environment, these refreshed tokens cannot be persisted back to the user's storage.

**Workarounds**:
1. Use the **customUserVars configuration** (see Approach B below) for manual token management
2. Users can re-authenticate when prompted - the process is quick via OAuth
3. For production deployments, consider implementing LibreChat database integration (planned enhancement)

### Key Features for LibreChat

- **Per-User Authentication**: Each user authenticates with their own TickTick account via OAuth2
- **Process Isolation**: LibreChat spawns separate MCP processes per user with isolated tokens
- **Multi-User Data Isolation**: Each user's TickTick data is completely isolated
- **Docker Compatible**: Designed to run in containerized environments (Docker, Unraid, etc.)

### Installation Options

#### Option 1: Using npx (Recommended)

Install directly from npm:
```bash
npx @varming/ticktick-mcp
```

Or install globally:
```bash
npm install -g @varming/ticktick-mcp
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

### LibreChat Configuration

Choose one of the two approaches below based on your needs:

#### Approach A: OAuth Flow (Recommended - With Known Limitation)

This approach uses LibreChat's OAuth integration. Users authenticate via TickTick's OAuth flow, but be aware of the token refresh limitation mentioned above.

**Step 1: Register OAuth Application**

Register at [TickTick Developer Center](https://developer.ticktick.com/manage):
- Set redirect URI to: `http://your-librechat-domain:3080/oauth/callback`
- Note your Client ID and Client Secret
- For local testing: `http://localhost:3080/oauth/callback`

**Step 2: Configure Environment Variables**

Add to your LibreChat `.env` file:
```env
TICKTICK_CLIENT_ID=your_client_id_here
TICKTICK_CLIENT_SECRET=your_client_secret_here
```

**Step 3: Add to librechat.yaml**

Using npx (simpler):
```yaml
version: 1.0.0

mcpServers:
  ticktick:
    type: stdio
    command: npx
    args:
      - "@varming/ticktick-mcp"

    env:
      TICKTICK_CLIENT_ID: ${TICKTICK_CLIENT_ID}
      TICKTICK_CLIENT_SECRET: ${TICKTICK_CLIENT_SECRET}
      LIBRECHAT_USER_ID: "{{LIBRECHAT_USER_ID}}"

    timeout: 30000
    initTimeout: 10000

    # Optional: Custom icon for the tool
    # iconPath: /path/to/ticktick-icon.svg

    # Optional: Include in chat menu dropdown
    chatMenu: true
```

Or using manual uv installation:
```yaml
version: 1.0.0

mcpServers:
  ticktick:
    type: stdio
    command: uv
    args:
      - "run"
      - "--directory"
      - "/app/ticktick-mcp"  # Update to your installation path
      - "-m"
      - "ticktick_mcp.cli"
      - "run"

    env:
      TICKTICK_CLIENT_ID: ${TICKTICK_CLIENT_ID}
      TICKTICK_CLIENT_SECRET: ${TICKTICK_CLIENT_SECRET}
      LIBRECHAT_USER_ID: "{{LIBRECHAT_USER_ID}}"

    timeout: 30000
    initTimeout: 10000
```

**Step 4: User Authentication**

Users authenticate once via LibreChat's OAuth flow:
1. First time using TickTick, user will be prompted to authenticate
2. Click "Authenticate" button in LibreChat UI
3. Redirect to TickTick for authorization
4. Return to LibreChat - ready to use!

**Note**: Due to the token refresh limitation, users may need to re-authenticate periodically.

---

#### Approach B: Manual Token Entry (customUserVars)

This approach uses LibreChat's `customUserVars` feature, allowing users to manually enter and update their tokens. This provides more control over token management.

**Step 1: Register OAuth Application** (same as Approach A)

**Step 2: Add to librechat.yaml**

Using npx:
```yaml
version: 1.0.0

mcpServers:
  ticktick:
    type: stdio
    command: npx
    args:
      - "@varming/ticktick-mcp"

    env:
      TICKTICK_CLIENT_ID: ${TICKTICK_CLIENT_ID}
      TICKTICK_CLIENT_SECRET: ${TICKTICK_CLIENT_SECRET}
      TICKTICK_ACCESS_TOKEN: "{{TICKTICK_ACCESS_TOKEN}}"
      TICKTICK_REFRESH_TOKEN: "{{TICKTICK_REFRESH_TOKEN}}"
      LIBRECHAT_USER_ID: "{{LIBRECHAT_USER_ID}}"

    customUserVars:
      TICKTICK_ACCESS_TOKEN:
        title: "TickTick Access Token"
        description: "Your personal TickTick access token. Authenticate at <a href='https://developer.ticktick.com/manage' target='_blank'>TickTick Developer Portal</a> to obtain tokens."
      TICKTICK_REFRESH_TOKEN:
        title: "TickTick Refresh Token"
        description: "Your TickTick refresh token (obtained during OAuth authentication)."

    startup: false  # Don't connect until user provides tokens
    timeout: 30000
    initTimeout: 10000
```

**Step 3: User Token Setup**

Users manage their own tokens:

1. **Obtain Tokens**:
   - Visit [TickTick Developer Portal](https://developer.ticktick.com/manage)
   - Create an OAuth application (or use existing)
   - Authenticate and obtain access + refresh tokens

2. **Enter in LibreChat**:
   - **From Chat**: When selecting TickTick tools, click the settings icon next to "ticktick" in the tool dropdown
   - **From Settings Panel**: Navigate to Settings → MCP Settings → ticktick
   - Enter both tokens in the configuration dialog

3. **Update Tokens**: Users can update tokens anytime through the same UI

**Benefits of This Approach**:
- ✅ Users have full control over token management
- ✅ Tokens are stored securely by LibreChat per-user
- ✅ No token refresh persistence issues
- ✅ Users can manually update tokens when they expire

---

### Docker Setup (If Using Containers)

For Docker deployments, ensure proper volume mounting:

```yaml
# docker-compose.yml or Unraid template
volumes:
  - /path/on/host/ticktick-mcp:/app/ticktick-mcp

environment:
  - TICKTICK_CLIENT_ID=your_client_id
  - TICKTICK_CLIENT_SECRET=your_client_secret
```

For npx installations, ensure Node.js and Python are available in the container.

### Using TickTick in LibreChat

Once configured and authenticated, users can interact naturally:

- "Show me all my TickTick projects"
- "Create a task called 'Review PR' in my Work project with high priority"
- "What tasks are due today?"
- "Show me my high priority tasks"
- "Mark task 'Buy groceries' as complete"
- "What's on my engaged list?" (GTD methodology)

### Multi-User Considerations

- **Complete Data Isolation**: Each user only accesses their own TickTick account
- **Per-User Processes**: LibreChat spawns isolated MCP process per user
- **Token Expiration**: Be aware of the token refresh limitation (see warning above)
- **Re-authentication**: Users may need to re-authenticate periodically
- **Concurrent Users**: Tested with multiple simultaneous users

### Troubleshooting

#### "TICKTICK_ACCESS_TOKEN not found in environment"

**Approach A (OAuth)**:
- User hasn't authenticated yet - click "Authenticate" in LibreChat UI
- Verify OAuth redirect URI matches LibreChat deployment URL
- Check that TICKTICK_CLIENT_ID and TICKTICK_CLIENT_SECRET are set

**Approach B (customUserVars)**:
- User needs to enter tokens in MCP Settings
- Access via Settings → MCP Settings → ticktick
- Or via tool selection dropdown (settings icon)

#### "Token Refresh Failed" or Frequent Re-authentication Required

This is the expected behavior due to the token persistence limitation:
- **Short-term**: Users re-authenticate when prompted (quick OAuth flow)
- **Workaround**: Switch to Approach B (customUserVars) for manual token control
- **Long-term**: Database integration planned for future release

#### "TickTick API connection failed"

- Verify environment variables are set correctly
- Check OAuth application configuration in TickTick Developer Portal
- Ensure redirect URI matches exactly (including port)
- Review LibreChat logs for detailed error messages

#### Docker/Container Issues

- Verify volume mounts for manual installations
- Ensure Python 3.10+ available in container
- Check that npx/Node.js available if using npx approach
- Review container logs: `docker logs <container_name>`

### Dida365 Support (Chinese TickTick)

For Dida365 users, add these environment variables:

```yaml
env:
  TICKTICK_CLIENT_ID: ${TICKTICK_CLIENT_ID}
  TICKTICK_CLIENT_SECRET: ${TICKTICK_CLIENT_SECRET}
  TICKTICK_BASE_URL: "https://api.dida365.com/open/v1"
  TICKTICK_AUTH_URL: "https://dida365.com/oauth/authorize"
  TICKTICK_TOKEN_URL: "https://dida365.com/oauth/token"
  LIBRECHAT_USER_ID: "{{LIBRECHAT_USER_ID}}"
```

Update OAuth URLs in your OAuth application registration to use `dida365.com` instead of `ticktick.com`.

### Production Readiness

**Current Status**: ✅ **Approved for Production with Conditions**

Based on comprehensive code review (B+ grade, 89.5/100):

- ✅ **Architecture**: Excellent (98/100)
- ✅ **Security**: Strong OAuth2 implementation (92/100)
- ✅ **Error Handling**: Comprehensive (92/100)
- ✅ **Code Quality**: Professional (88/100)
- ⚠️ **Known Limitation**: Token refresh persistence issue

**Deployment Recommendation**:
- **Claude Desktop**: ✅ Production ready (no limitations)
- **Claude Code**: ✅ Production ready (no limitations)
- **LibreChat**: ✅ Approved with conditions (token refresh limitation documented)

**Mitigation Strategy**:
- Document limitation clearly for users (✅ Done)
- Provide customUserVars alternative (✅ Done)
- Plan database integration for future release (📋 Roadmap)

For detailed review findings, see:
- `COMPREHENSIVE_CODE_REVIEW.md` - Full technical assessment
- `QA_MASTER_REVIEW.md` - Quality assurance audit
- `REVIEW_SUMMARY.md` - Executive summary

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

## Attribution

This project is a fork of [jacepark12/ticktick-mcp](https://github.com/jacepark12/ticktick-mcp) created by [Jaesung Park](https://github.com/jacepark12).

### Enhancements in This Fork

- 🔐 **Multi-User Support**: Full LibreChat integration with per-user OAuth tokens
- 📦 **npx Installation**: Universal installation via npm for all platforms
- ✅ **Input Validation**: Comprehensive validation with TaskValidator class
- 🔄 **Connection Pooling**: HTTP connection pooling with automatic retry
- 🛡️ **Error Handling**: Master-level error handling with HTTP status code parsing
- 🔧 **Missing Tools**: Added `update_project` tool for project management
- 📚 **Documentation**: Enhanced docs for Claude Desktop, Claude Code, and LibreChat

### Original Contributors

Special thanks to the original contributors:
- [Jaesung Park](https://github.com/jacepark12) - Original author
- [yangkghjh](https://github.com/yangkghjh)
- [Monacraft](https://github.com/Monacraft)
- [wsargent](https://github.com/wsargent)
- [lisah2u](https://github.com/lisah2u)
- [richgrov](https://github.com/richgrov)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Original work Copyright (c) 2024 Jaesung Park  
Fork enhancements Copyright (c) 2025 Lars Varming

## License

This project is licensed under the MIT License - see the LICENSE file for details.
