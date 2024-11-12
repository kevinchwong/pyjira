# Jira CLI Tool

A command-line interface for interacting with Jira.

## Features

- List issues with multiple filter options
- View issue details
- Search issues using JQL
- View issues assigned to you
- Support for custom fields and filters

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jira-cli.git
cd jira-cli

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your Jira credentials:

```bash
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_DEFAULT_PROJECT=PROJ  # Optional
```

## Usage

```bash
# List your issues
jira my

# List issues with filters
jira list --project PROJ --status "In Progress" --type Task

# View issue details
jira view PROJ-123

# List with advanced filters
jira list \
  --project PROJ \
  --status "In Progress" \
  --type Task \
  --priority High \
  --labels "urgent,backend" \
  --created-after 2024-01-01 \
  --updated-after 2024-01-01 \
  --component "Backend" \
  --reporter "currentUser()" \
  --query "NOT resolution = Done"
```

## Available Commands

### List Command Options
- `--project`: Filter by project key
- `--status`: Filter by status
- `--type`: Filter by issue type
- `--priority`: Filter by priority
- `--assignee`: Filter by assignee
- `--reporter`: Filter by reporter
- `--component`: Filter by component
- `--labels`: Filter by labels (comma-separated)
- `--created-after`: Filter by creation date (YYYY-MM-DD)
- `--updated-after`: Filter by update date (YYYY-MM-DD)
- `--query`: Additional JQL query string

### View Command
```bash
jira view ISSUE-KEY
```

### My Issues Command
```bash
jira my [--status STATUS]
```

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run unit tests
pytest tests/test_cli.py -v

# Run E2E tests (requires .env setup)
pytest tests/test_e2e.py -v

# Run all tests
pytest -v
```

## License

MIT