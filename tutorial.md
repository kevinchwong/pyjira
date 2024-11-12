# Jira CLI Tutorial

This tutorial will guide you on how to use the Jira CLI tool to manage your Jira issues.

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Basic Commands](#basic-commands)
3. [Advanced Usage](#advanced-usage)
4. [Custom Configurations](#custom-configurations)
5. [Troubleshooting](#troubleshooting)

## Initial Setup

### 1. Get Jira API Token
1. Visit https://id.atlassian.com/manage/api-tokens
2. Click "Create API token"
3. Give your token a descriptive name (e.g., "jira-cli")
4. Copy and safely store the generated token

### 2. Configure Environment Variables
1. Copy the environment template:
```bash
# Create environment file from template
cp .env.example .env
```

2. Edit the `.env` file with your information:
```bash
# Jira instance URL
JIRA_SERVER=https://your-domain.atlassian.net
# Your Atlassian account email
JIRA_EMAIL=your-email@example.com
# API token generated in step 1
JIRA_API_TOKEN=your-api-token
# Optional: Default project key
JIRA_DEFAULT_PROJECT=DATA
# Optional: Default issue type
JIRA_DEFAULT_ISSUE_TYPE=Task
```

### 3. Installation and Setup
1. Install dependencies:
```bash
# Install project dependencies using Poetry
poetry install
```

2. Configure Python environment:
```bash
# Set Python version
poetry env use python3.8
# Activate the virtual environment
poetry shell
```

3. Verify installation:
```bash
# Check if CLI is properly installed
jira --version
```

## Basic Commands

### 1. View Issues
```bash
# View a specific issue
jira view DATA-2904

# View in different formats
jira view DATA-2904 --format json
jira view DATA-2904 --format markdown

# List your assigned issues
jira list

# List with filters
jira list --project DATA --status "In Progress"
jira list --assignee currentUser() --status "To Do"

# List using JQL
jira list "project = DATA AND priority = High"
```

### 2. Create Issues
```bash
# Basic creation
jira create --project DATA --summary "New feature request" --description "Details here"

# With custom fields
jira create --project DATA \
    --summary "Bug fix" \
    --custom-field "customfield_10000=5" \
    --custom-field "customfield_10001=High"

# Using templates
jira create --template bug --project DATA --summary "Login error"
jira create --template feature --project DATA --summary "User profile"
```

### 3. Update Issues
```bash
# Update status
jira update DATA-2904 --status "In Progress"

# Update multiple fields
jira update DATA-2904 \
    --assignee "john.doe" \
    --priority "High" \
    --labels "urgent,critical"

# Add comment
jira comment DATA-2904 "Work in progress"

# Add attachments
jira attach DATA-2904 ./screenshot.png ./logs.txt

# Log work
jira log DATA-2904 --time "3h 30m" --comment "Code review"
```

### 4. Transitions
```bash
# List available transitions
jira transitions DATA-2904

# Transition issue
jira transition DATA-2904 "In Progress"
jira transition DATA-2904 "Done" --resolution "Fixed"
```

### 5. Field Information
```bash
# List all fields
jira fields

# List custom fields only
jira fields --issue DATA-2904 --custom-only

# Show field values for an issue
jira fields --issue DATA-2904 --with-values
```

## Advanced Usage

### 1. Bulk Operations
```bash
# Update multiple issues
jira bulk-update "project = DATA AND status = 'To Do'" --status "In Progress"

# With confirmation and batch size
jira bulk-update "project = DATA" \
    --status "Done" \
    --batch-size 10 \
    --yes
```

### 2. Issue Links
```bash
# Create issue link
jira link DATA-2904 --link-type "blocks" DATA-456
```

### 3. Watchers
```bash
# Add yourself as watcher
jira watch DATA-2904

# Remove yourself
jira watch DATA-2904 --unwatch
```

### 4. Sprint Management
```bash
# List sprints
jira sprint list --board BOARD-1

# Create sprint
jira sprint create --board BOARD-1 --name "Sprint 1" --start-date "2024-01-01"

# Add issues to sprint
jira sprint add SPRINT-1 DATA-2904 DATA-456
```

### 5. Velocity Metrics
```bash
# View board velocity
jira velocity BOARD-1 --days 30
```

## Custom Configurations

### 1. Aliases
Add to `~/.jira/config.yaml`:
```yaml
aliases:
  my: "list 'assignee = currentUser()'"
  todo: "list 'status = \"To Do\" AND assignee = currentUser()'"
  bugs: "list 'issuetype = Bug AND assignee = currentUser()'"
```

Use aliases:
```bash
jira my
jira todo
jira bugs
```

### 2. Templates
Create custom templates in `~/.jira/templates/`:
```yaml
# ~/.jira/templates/custom.yaml
fields:
  issuetype:
    name: Task
  priority:
    name: High
  labels: [custom]
  customfield_10000: "5"
```

## Troubleshooting

### 1. Authentication Issues
- Check `.env` file configuration
- Verify API token is valid
- Ensure JIRA_SERVER includes 'https://'

### 2. Command Errors
- Use `--debug` flag for verbose output
- Check logs in `~/.jira/logs/jira-cli.log`
- Verify JQL syntax for list commands

### 3. Template Issues
- Ensure template files are valid YAML
- Check field IDs using `jira fields`
- Verify issue type exists in your Jira instance