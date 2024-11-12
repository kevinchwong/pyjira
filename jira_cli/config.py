"""
Configuration module for Jira CLI.

This module handles loading and managing configuration from various sources:
- YAML configuration files
- Issue templates
- Environment variables

The module provides functions to:
- Load main configuration from ~/.jira/config.yaml
- Load issue templates from ~/.jira/templates/
- Handle default configurations
- Support custom template paths
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import ConfigurationError

def get_config_path() -> Path:
    """Get the path to the config file"""
    # Check for config in user's home directory
    home_config = Path.home() / '.jira' / 'config.yaml'
    if home_config.exists():
        return home_config
    
    # Check for config in current directory
    local_config = Path.cwd() / 'config.yaml'
    if local_config.exists():
        return local_config
    
    # Return default home config path
    return home_config

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        # If specific path provided, use it
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = get_config_path()
        
        # Create default config if it doesn't exist
        if not config_file.exists():
            config_file.parent.mkdir(parents=True, exist_ok=True)
            default_config = {
                'aliases': {
                    'my': 'list --assignee="currentUser()"',
                    'todo': 'list --status="To Do"',
                    'inprog': 'list --status="In Progress"',
                    'done': 'list --status="Done"',
                    'blocked': 'list --status="Blocked"',
                    'review': 'list --status="In Review"',
                    'recent': 'list "updated >= -7d"'
                }
            }
            with open(config_file, 'w') as f:
                yaml.safe_dump(default_config, f)
            return default_config
        
        # Load existing config
        with open(config_file, 'r') as f:
            return yaml.safe_load(f) or {}
            
    except Exception as e:
        raise ConfigurationError(f"Failed to load config: {str(e)}")

def get_template(template_name: str) -> Dict[str, Any]:
    """
    Load a specific issue template configuration.

    This function loads a template file from the templates directory
    and returns its configuration.

    Args:
        template_name (str): Name of the template to load (without .yaml extension)

    Returns:
        Dict[str, Any]: Template configuration containing:
            - Issue type settings
            - Field defaults
            - Description templates
            - Custom field values

    Raises:
        yaml.YAMLError: If the template file is invalid
        OSError: If template file is not accessible

    Example:
        >>> bug_template = get_template('bug')
        >>> feature_template = get_template('feature')
    """
    template_path = os.path.expanduser(f'~/.jira/templates/{template_name}.yaml')
    return load_config(template_path)