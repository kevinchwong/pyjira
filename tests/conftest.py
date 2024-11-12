import pytest
from unittest.mock import MagicMock
from jira_cli.client import JiraClient
from jira_cli.formatters import IssueFormatter
from rich.table import Table

@pytest.fixture
def mock_jira(monkeypatch):
    """Create a mock JIRA client"""
    # Create the mock
    mock = MagicMock()
    
    # Create a real Rich table for the formatter to return
    table = Table()
    table.add_column("Key")
    table.add_column("Summary")
    table.add_column("Status")
    table.add_column("Priority")
    table.add_row("TEST-1", "Test Issue", "In Progress", "High")
    
    # Mock the IssueFormatter class
    mock_formatter = MagicMock()
    mock_formatter.format_issue_list.return_value = table
    
    # Mock the IssueFormatter class to return our mock formatter instance
    def mock_formatter_class(*args, **kwargs):
        return mock_formatter
    
    # Patch both JiraClient and IssueFormatter
    monkeypatch.setattr(JiraClient, '__new__', lambda cls: mock)
    monkeypatch.setattr(IssueFormatter, '__new__', mock_formatter_class)
    
    # Mock all required methods
    mock.search_issues = MagicMock(return_value=[])
    mock.get_field_map = MagicMock(return_value={})
    
    return mock 