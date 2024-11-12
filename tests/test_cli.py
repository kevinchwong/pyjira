from click.testing import CliRunner
from pyjira.cli import cli
from pyjira.exceptions import JiraCliError

def test_list_basic(mock_jira):
    """Test basic list command without filters"""
    runner = CliRunner()
    # Set up mock to return some issues
    mock_jira.search_issues.return_value = [
        {'key': 'TEST-1', 'fields': {'summary': 'Test 1', 'status': {'name': 'To Do'}}}
    ]
    
    result = runner.invoke(cli, ['list'])
    print(f"Exit code: {result.exit_code}")
    print(f"Output: {result.output}")
    
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with('project = DATA')

def test_list_with_project(mock_jira):
    """Test list command with project filter"""
    runner = CliRunner()
    mock_jira.search_issues.return_value = [
        {'key': 'TEST-1', 'fields': {'summary': 'Test 1', 'status': {'name': 'To Do'}}}
    ]
    
    result = runner.invoke(cli, ['list', '--project', 'TEST'])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with('project = TEST')

def test_list_with_status(mock_jira):
    """Test list command with status filter"""
    runner = CliRunner()
    mock_jira.search_issues.return_value = [
        {'key': 'TEST-1', 'fields': {'summary': 'Test 1', 'status': {'name': 'In Progress'}}}
    ]
    
    result = runner.invoke(cli, ['list', '--status', 'In Progress'])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with("project = DATA AND status = 'In Progress'")

def test_my_command(mock_jira):
    """Test my command without filters"""
    runner = CliRunner()
    mock_jira.search_issues.return_value = [
        {'key': 'TEST-1', 'fields': {'summary': 'Test 1', 'status': {'name': 'To Do'}}}
    ]
    
    result = runner.invoke(cli, ['my'])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with('project = DATA AND assignee = currentUser()')

def test_my_command_with_status(mock_jira):
    """Test my command with status filter"""
    runner = CliRunner()
    mock_jira.search_issues.return_value = [
        {'key': 'TEST-1', 'fields': {'summary': 'Test 1', 'status': {'name': 'To Do'}}}
    ]
    
    result = runner.invoke(cli, ['my', '--status', 'To Do'])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with("project = DATA AND assignee = currentUser() AND status = 'To Do'")

def test_list_with_multiple_filters(mock_jira):
    """Test list command with multiple filters"""
    runner = CliRunner()
    mock_jira.search_issues.return_value = [
        {'key': 'TEST-1', 'fields': {'summary': 'Test 1', 'status': {'name': 'In Progress'}}}
    ]
    
    result = runner.invoke(cli, [
        'list',
        '--project', 'TEST',
        '--status', 'In Progress'
    ])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_once_with("project = TEST AND status = 'In Progress'")

def test_list_no_results(mock_jira):
    """Test list command when no issues are found"""
    runner = CliRunner()
    mock_jira.search_issues.return_value = []
    
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 1
    assert 'No issues found' in result.output
    mock_jira.search_issues.assert_called_once_with('project = DATA')