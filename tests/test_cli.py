from click.testing import CliRunner
from pyjira.cli import cli
from unittest.mock import Mock

def test_list_basic(mock_jira):
    """Test basic list command without filters"""
    runner = CliRunner()
    # Create a proper mock issue
    mock_issue = Mock()
    mock_issue.key = 'TEST-1'
    mock_issue.fields.summary = 'Test 1'
    mock_issue.fields.status.name = 'To Do'
    
    mock_jira.search_issues.return_value = [mock_issue]
    
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'TEST-1' in result.output
    mock_jira.search_issues.assert_called_once_with('assignee = currentUser()')

def test_list_with_project(mock_jira):
    """Test list command with project filter"""
    runner = CliRunner()
    mock_issue = Mock()
    mock_issue.key = 'TEST-1'
    mock_issue.fields.summary = 'Test 1'
    mock_issue.fields.status.name = 'To Do'
    
    mock_jira.search_issues.return_value = [mock_issue]
    
    result = runner.invoke(cli, ['list', '--project', 'TEST'])
    assert result.exit_code == 0
    assert 'TEST-1' in result.output
    mock_jira.search_issues.assert_called_once_with('project = TEST')

def test_list_with_status(mock_jira):
    """Test list command with status filter"""
    runner = CliRunner()
    mock_issue = Mock()
    mock_issue.key = 'TEST-1'
    mock_issue.fields.summary = 'Test 1'
    mock_issue.fields.status.name = 'In Progress'
    
    mock_jira.search_issues.return_value = [mock_issue]
    
    result = runner.invoke(cli, ['list', '--status', 'In Progress'])
    assert result.exit_code == 0
    assert 'TEST-1' in result.output
    mock_jira.search_issues.assert_called_once_with("status = 'In Progress'")

def test_my_command(mock_jira):
    """Test my command without filters"""
    runner = CliRunner()
    mock_issue = Mock()
    mock_issue.key = 'TEST-1'
    mock_issue.fields.summary = 'Test 1'
    mock_issue.fields.status.name = 'To Do'
    
    mock_jira.search_issues.return_value = [mock_issue]
    
    result = runner.invoke(cli, ['my'])
    assert result.exit_code == 0
    assert 'TEST-1' in result.output
    mock_jira.search_issues.assert_called_once_with('assignee = currentUser()')

def test_my_command_with_status(mock_jira):
    """Test my command with status filter"""
    runner = CliRunner()
    mock_issue = Mock()
    mock_issue.key = 'TEST-1'
    mock_issue.fields.summary = 'Test 1'
    mock_issue.fields.status.name = 'To Do'
    
    mock_jira.search_issues.return_value = [mock_issue]
    
    result = runner.invoke(cli, ['my', '--status', 'To Do'])
    assert result.exit_code == 0
    assert 'TEST-1' in result.output
    mock_jira.search_issues.assert_called_once_with("assignee = currentUser() AND status = 'To Do'")

def test_list_with_multiple_filters(mock_jira):
    """Test list command with multiple filters"""
    runner = CliRunner()
    mock_issue = Mock()
    mock_issue.key = 'TEST-1'
    mock_issue.fields.summary = 'Test 1'
    mock_issue.fields.status.name = 'In Progress'
    
    mock_jira.search_issues.return_value = [mock_issue]
    
    result = runner.invoke(cli, [
        'list',
        '--project', 'TEST',
        '--status', 'In Progress'
    ])
    assert result.exit_code == 0
    assert 'TEST-1' in result.output
    mock_jira.search_issues.assert_called_once_with("project = TEST AND status = 'In Progress'")

def test_list_no_results(mock_jira):
    """Test list command when no issues are found"""
    runner = CliRunner()
    mock_jira.search_issues.return_value = []
    
    result = runner.invoke(cli, [
        'list',
        '--project', 'BADDATA',
    ])    
    assert result.exit_code == 1
    assert 'No issues found' in result.output
    mock_jira.search_issues.assert_called_once_with('project = BADDATA')

def test_list_with_error(mock_jira):
    """Test list command when Jira API raises an error"""
    runner = CliRunner()
    mock_jira.search_issues.side_effect = Exception("Jira API Error")
    
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 1
    assert 'Error' in result.output

def test_cli_help(mock_jira):
    """Test CLI help command"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Command line interface for Jira' in result.output