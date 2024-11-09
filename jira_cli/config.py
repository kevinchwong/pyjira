import os
import yaml
from pathlib import Path

def load_config(config_path=None):
    """Load configuration from YAML file"""
    if config_path is None:
        config_path = os.path.expanduser('~/.jira/config.yaml')
    else:
        # If it's a template, look in the templates directory
        if 'templates/' in config_path:
            config_path = os.path.expanduser(f'~/.jira/{config_path}')
    
    if not os.path.exists(config_path):
        return {}
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_template(template_name):
    """Load a template configuration"""
    template_path = os.path.expanduser(f'~/.jira/templates/{template_name}.yaml')
    return load_config(template_path)