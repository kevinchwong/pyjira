"""
Logger module for Jira CLI.

This module provides logging configuration and setup for the Jira CLI application.
It creates a logger that writes to both a file and optionally to the console in debug mode.

The logger is configured to:
- Write logs to ~/.jira/logs/jira-cli.log
- Use DEBUG level when JIRA_CLI_DEBUG environment variable is set
- Use INFO level by default
- Include timestamp, logger name, and log level in messages
"""

import logging
import os
from pathlib import Path
from typing import Optional

def setup_logger() -> logging.Logger:
    """
    Configure and set up the application logger.

    This function:
    1. Creates the log directory if it doesn't exist
    2. Sets up file logging
    3. Optionally enables console logging in debug mode
    4. Configures log format with timestamps and levels

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = setup_logger()
        >>> logger.info("Application started")
        >>> logger.debug("Debug information")
    """
    log_dir: Path = Path.home() / '.jira' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file: Path = log_dir / 'jira-cli.log'
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if os.getenv('JIRA_CLI_DEBUG') else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler() if os.getenv('JIRA_CLI_DEBUG') else logging.NullHandler()
        ]
    )
    
    return logging.getLogger('jira-cli')

# Initialize logger
logger: logging.Logger = setup_logger() 