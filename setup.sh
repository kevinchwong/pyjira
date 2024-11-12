#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Jira CLI...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}Poetry not found. Installing Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Create virtual environment and install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
if ! poetry install; then
    echo -e "${RED}Failed to install dependencies. Retrying with --sync...${NC}"
    poetry install --sync
fi

# Verify key dependencies
echo -e "${GREEN}Verifying dependencies...${NC}"
poetry run python -c "import yaml; import jira; import click; import rich" || {
    echo -e "${RED}Failed to verify dependencies. Reinstalling...${NC}"
    poetry install --sync --no-cache
}

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    echo "# Jira instance URL" > .env
    echo "JIRA_SERVER=https://your-domain.atlassian.net" >> .env
    echo "# Your Atlassian account email" >> .env
    echo "JIRA_EMAIL=your-email@example.com" >> .env
    echo "# API token generated from Atlassian account" >> .env
    echo "JIRA_API_TOKEN=your-api-token" >> .env
    echo "# Optional: Default project key" >> .env
    echo "JIRA_DEFAULT_PROJECT=PROJ" >> .env
    echo -e "${YELLOW}Please edit .env file with your Jira credentials${NC}"
fi

# Run tests to verify installation
echo -e "${GREEN}Running unit tests...${NC}"
if ! poetry run pytest tests/test_cli.py -v; then
    echo -e "${YELLOW}Some tests failed, but installation can continue.${NC}"
    echo -e "${YELLOW}Please check the test output above for details.${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}Next steps:"
echo "1. Edit .env with your Jira credentials"
echo "2. Run 'poetry shell' to activate the virtual environment"
echo "3. Try 'jira --help' to see available commands"
echo -e "4. Run 'poetry run pytest tests/test_cli.py -v' to verify tests${NC}"