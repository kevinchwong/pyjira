import logging
import os
from pathlib import Path

def setup_logger():
    """Configure logging for the application"""
    log_dir = Path.home() / '.jira' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'jira-cli.log'
    
    logging.basicConfig(
        level=logging.DEBUG if os.getenv('JIRA_CLI_DEBUG') else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler() if os.getenv('JIRA_CLI_DEBUG') else logging.NullHandler()
        ]
    )
    
    return logging.getLogger('jira-cli')

logger = setup_logger() 