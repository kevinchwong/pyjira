# Jira CLI Tool

A command-line interface for interacting with Jira, focusing on efficient issue management and querying.

## Features

- List issues with comprehensive filtering options
- View detailed issue information
- Search using advanced JQL queries
- View assigned issues
- Support for custom fields and rich formatting

## Installation

```bash
# Clone the repository
git clone https://github.com/kevinchwong/pyjira.git
cd jira-cli

# Run setup script
chmod +x setup.sh
./setup.sh
```

## Configuration

After running setup.sh, edit `.env` file with your Jira credentials:

```bash
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token  # Generate from Atlassian account settings
JIRA_DEFAULT_PROJECT=PROJ      # Optional: Your default project
```

## Usage

```bash
# Activate virtual environment
poetry shell

# List your assigned issues
jira my

# List issues with filters
jira list \
  --project PROJ \
  --status "In Progress" \
  --type Task \
  --priority High

# View issue details
jira view PROJ-123

# Advanced filtering
jira list \
  --project PROJ \
  --status "In Progress" \
  --type Bug \
  --priority High \
  --labels "urgent,backend" \
  --created-after 2024-01-01 \
  --updated-after 2024-01-01 \
  --component "Backend" \
  --reporter "currentUser()" \
  --assignee "currentUser()" \
  --query "NOT resolution = Done"
```

## Available Commands

### List Command
Filter issues using multiple criteria:
- `--project`: Project key
- `--status`: Issue status
- `--type`: Issue type
- `--priority`: Priority level
- `--assignee`: Assignee (use "currentUser()")
- `--reporter`: Reporter
- `--component`: Component name
- `--labels`: Comma-separated labels
- `--created-after`: Creation date (YYYY-MM-DD)
- `--updated-after`: Last update date (YYYY-MM-DD)
- `--query`: Additional JQL

### View Command
```bash
jira view ISSUE-KEY
```

### My Issues
```bash
jira my [--status STATUS]
```

## Development

```bash
# Install dependencies
poetry install

# Run unit tests
poetry run pytest tests/test_cli.py -v

# Run E2E tests (requires .env)
poetry run pytest tests/test_e2e.py -v

# Run all tests with coverage
poetry run pytest -v
```

## Author

Kevin Wong (kevinchwong@gmail.com)

## License

MIT