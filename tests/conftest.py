import pytest
from unittest.mock import MagicMock
from pyjira.client import JiraClient
from pyjira.formatters import IssueFormatter
from rich.table import Table

@pytest.fixture
def mock_jira(monkeypatch):
    """Create a mock JIRA client"""
    # Create a mock client instance
    mock_client = MagicMock(spec=JiraClient)
    
    # Set up default return values
    mock_client.search_issues.return_value = []
    mock_client.get_field_map.return_value = {}
    mock_client.get_issue.return_value = {
        'key': 'TEST-123',
        'fields': {
            'summary': 'Test Issue',
            'status': {'name': 'In Progress'}
        }
    }
    
    # Create a real Rich table for the formatter to return
    table = Table()
    table.add_column("Key")
    table.add_column("Summary")
    table.add_column("Status")
    table.add_column("Priority")
    table.add_row("TEST-1", "Test Issue", "In Progress", "High")
    
    # Mock the formatter
    mock_formatter = MagicMock(spec=IssueFormatter)
    mock_formatter.format_issue_list.return_value = table
    mock_formatter.format_issue.return_value = table
    
    # Create factory functions that return our mock instances
    def mock_client_factory(*args, **kwargs):
        return mock_client
        
    def mock_formatter_factory(*args, **kwargs):
        return mock_formatter
    
    # Patch at module level where the classes are imported
    monkeypatch.setattr('pyjira.client.JiraClient.__new__', mock_client_factory)
    monkeypatch.setattr('pyjira.formatters.IssueFormatter.__new__', mock_formatter_factory)
    
    return mock_client