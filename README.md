# Jira CLI Tool

A command-line interface for interacting with Jira.

## Features

- Create, view, and update issues
- Search issues using JQL
- Bulk operations
- Sprint management
- Work logging
- File attachments
- Custom templates
- Rich text output
- Detailed logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jira-cli.git
cd jira-cli
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. Edit your `.env` file with your Jira credentials.

## Usage

See the [tutorial](tutorial.md) for detailed usage instructions.

## Development

### Prerequisites

- Python 3.12+
- Poetry

### Setting up development environment

1. Install dependencies:
```bash
poetry install
```

2. Activate virtual environment:
```bash
poetry shell
```

3. Run tests:
```bash
poetry run pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details. 