#!/bin/bash

# Create necessary directories
mkdir -p ~/.jira/templates ~/.jira/logs

# Copy example files if they don't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it with your credentials."
fi

# Create default config if it doesn't exist
if [ ! -f ~/.jira/config.yaml ]; then
    cat > ~/.jira/config.yaml << EOL
# Jira CLI Configuration
aliases:
  todo: "list 'assignee = currentUser() AND status = \"To Do\"'"
  my-bugs: "list 'assignee = currentUser() AND issuetype = Bug'"
  in-progress: "list 'assignee = currentUser() AND status = \"In Progress\"'"

templates_dir: ~/.jira/templates
log_file: ~/.jira/logs/jira-cli.log
EOL
    echo "Created default configuration file."
fi

# Create example template
if [ ! -f ~/.jira/templates/bug.yaml ]; then
    cat > ~/.jira/templates/bug.yaml << EOL
fields:
  issuetype: Bug
  priority: High
  labels: [bug]
  components: [backend]
EOL
    echo "Created example bug template."
fi

# Install dependencies
poetry install

# Set up Python environment
poetry env use python3.12

echo "Setup complete! Please edit .env with your Jira credentials."