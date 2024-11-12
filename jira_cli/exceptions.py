"""
Exception classes for the Jira CLI application.

This module defines custom exceptions used throughout the application to provide
clear error messages and handling for different types of errors that may occur
during CLI operation.

The exception hierarchy is:
- JiraCliError (base exception)
  |- ConfigurationError (configuration/environment issues)
  |- AuthenticationError (Jira authentication failures)
  |- JiraApiError (Jira API interaction errors)
  |- ValidationError (input validation failures)
"""

from typing import Any

class JiraCliError(Exception):
    """
    Base exception class for all Jira CLI errors.
    
    This class serves as the parent class for all custom exceptions in the application.
    It provides a common base for catching and handling all Jira CLI-specific errors.

    Args:
        message (str): The error message to display

    Example:
        >>> raise JiraCliError("An error occurred")
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)

class ConfigurationError(JiraCliError):
    """
    Raised when there's a configuration error in the application.
    
    This exception is raised when:
    - Required environment variables are missing
    - Configuration files are not found
    - Configuration values are invalid

    The error message includes common fixes and setup instructions.

    Example:
        >>> raise ConfigurationError("Missing JIRA_SERVER variable")
    """
    def __str__(self) -> str:
        return f"""
Configuration Error: {self.args[0]}

Common fixes:
1. Copy .env.example to .env:
   cp .env.example .env

2. Edit .env with your credentials:
   - JIRA_SERVER: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
   - JIRA_EMAIL: Your Atlassian account email
   - JIRA_API_TOKEN: API token from https://id.atlassian.com/manage/api-tokens

3. Make sure the .env file is in your current directory
"""

class AuthenticationError(JiraCliError):
    """
    Raised when authentication with Jira fails.
    
    This exception is raised when:
    - API token is invalid
    - Credentials are incorrect
    - Server URL is incorrect
    - Authentication request fails

    Example:
        >>> raise AuthenticationError("Invalid API token")
    """
    pass

class JiraApiError(JiraCliError):
    """
    Raised when a Jira API request fails.
    
    This exception is raised when:
    - API requests return errors
    - Network issues occur
    - Invalid data is sent to API
    - Rate limits are exceeded

    Example:
        >>> raise JiraApiError("Failed to create issue: Invalid project key")
    """
    pass

class ValidationError(JiraCliError):
    """
    Raised when input validation fails.
    
    This exception is raised when:
    - Required fields are missing
    - Field values are invalid
    - Data format is incorrect
    - Business rules are violated

    Example:
        >>> raise ValidationError("Invalid transition name")
    """
    pass 