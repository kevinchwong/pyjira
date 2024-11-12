from click.testing import CliRunner
from jira_cli.cli import cli
from jira_cli.exceptions import JiraCliError

def test_list_basic(mock_jira):
    """Test basic list command without filters"""
    runner = CliRunner()
    mock_jira.search_issues.return_value = []
    
    result = runner.invoke(cli, ['list'])
    print(f"Exit code: {result.exit_code}")
    print(f"Output: {result.output}")
    if hasattr(result, 'exception') and result.exception:
        print(f"Exception: {result.exception}")
        import traceback
        traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)
    
    print(f"Mock calls: {mock_jira.search_issues.call_args_list}")
    
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with('assignee = currentUser()')

def test_list_with_project(mock_jira):
    """Test list command with project filter"""
    runner = CliRunner()
    result = runner.invoke(cli, ['list', '--project', 'TEST'])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with('project = TEST')

def test_list_with_status(mock_jira):
    """Test list command with status filter"""
    runner = CliRunner()
    result = runner.invoke(cli, ['list', '--status', 'In Progress'])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with("status = 'In Progress'")

def test_my_command(mock_jira):
    """Test my command without filters"""
    runner = CliRunner()
    result = runner.invoke(cli, ['my'])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with('assignee = currentUser()')

def test_my_command_with_status(mock_jira):
    """Test my command with status filter"""
    runner = CliRunner()
    result = runner.invoke(cli, ['my', '--status', 'To Do'])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with("assignee = currentUser() AND status = 'To Do'")

def test_view_issue(mock_jira):
    """Test viewing a specific issue"""
    runner = CliRunner()
    mock_jira.get_issue.return_value = {
        'key': 'TEST-123',
        'fields': {
            'summary': 'Test issue',
            'status': {'name': 'In Progress'},
            'description': 'Test description'
        }
    }
    
    result = runner.invoke(cli, ['view', 'TEST-123'])
    assert result.exit_code == 0
    mock_jira.get_issue.assert_called_once_with('TEST-123')

def test_list_error_handling(mock_jira):
    """Test error handling in list command"""
    runner = CliRunner()
    mock_jira.search_issues.side_effect = JiraCliError('Failed to fetch issues')
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 1
    mock_jira.search_issues.assert_called_once()
    assert 'Failed to fetch issues' in result.output

def test_view_error_handling(mock_jira):
    """Test error handling when viewing non-existent issue"""
    runner = CliRunner()
    mock_jira.get_issue.side_effect = JiraCliError('Issue not found')
    result = runner.invoke(cli, ['view', 'FAKE-123'])
    assert result.exit_code == 1
    mock_jira.get_issue.assert_called_once_with('FAKE-123')
    assert 'Issue not found' in result.output

def test_list_with_multiple_filters(mock_jira):
    """Test list command with multiple filters"""
    runner = CliRunner()
    result = runner.invoke(cli, [
        'list',
        '--project', 'TEST',
        '--status', 'In Progress'
    ])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with("project = TEST AND status = 'In Progress'")