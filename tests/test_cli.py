from click.testing import CliRunner
from jira_cli.cli import cli

def test_my_command(mock_jira):
    """Test the 'my' command that shows issues assigned to current user"""
    runner = CliRunner()
    
    # Test without status filter
    result = runner.invoke(cli, ['my'])
    assert result.exit_code == 0
    mock_jira.search_issues.assert_called_with('assignee = currentUser()')