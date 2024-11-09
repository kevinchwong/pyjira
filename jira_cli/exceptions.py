class JiraCliError(Exception):
    """Base exception for Jira CLI errors"""
    pass

class ConfigurationError(JiraCliError):
    """Raised when there's a configuration error"""
    def __str__(self):
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
    """Raised when authentication fails"""
    pass

class JiraApiError(JiraCliError):
    """Raised when Jira API returns an error"""
    pass

class ValidationError(JiraCliError):
    """Raised when input validation fails"""
    pass 