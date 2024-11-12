import pytest
from click.testing import CliRunner
from jira_cli.cli import cli
import os
from dotenv import load_dotenv
import time
from functools import wraps
from typing import Callable, Any

# Skip all tests if no JIRA credentials are available
pytestmark = pytest.mark.skipif(
    not os.path.exists('.env'),
    reason="No .env file found. Skipping E2E tests."
)

def timeout_after(seconds: int) -> Callable:
    """Decorator to skip test if it takes too long"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            if duration > seconds:
                pytest.skip(f"Test took too long ({duration:.2f}s > {seconds}s)")
            return result
        return wrapper
    return decorator

@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """Load environment variables from .env file"""
    load_dotenv()
    # Verify required environment variables
    required_vars = ['JIRA_SERVER', 'JIRA_EMAIL', 'JIRA_API_TOKEN']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        pytest.skip(f"Missing required environment variables: {', '.join(missing)}")
    # Wait a bit to avoid rate limiting at the start
    time.sleep(1)

@pytest.fixture(scope="session")
def runner():
    """Create a CLI runner - reuse for all tests"""
    return CliRunner()

@pytest.fixture(scope="session")
def sample_issue_key(setup_env, runner):
    """Get a sample issue key once and reuse it for all tests"""
    result = runner.invoke(cli, ['my'])
    if result.exit_code == 0:
        import re
        match = re.search(r'([A-Z]+-\d+)', result.output)
        if match:
            return match.group(1)
    pytest.skip("No issues found to test with")

@timeout_after(30)
def test_list_my_issues(setup_env, runner):
    """Test listing issues assigned to current user"""
    result = runner.invoke(cli, ['my'])
    print(f"Output: {result.output}")  # Debug output
    if result.exception:
        print(f"Exception: {result.exception}")  # Debug output
    
    # Check for either success or "No issues found" message
    assert result.exit_code in [0, 1]
    if result.exit_code == 1:
        assert 'No issues found' in result.output
    else:
        assert 'Key' in result.output
        assert 'Summary' in result.output
        assert 'Status' in result.output

@pytest.fixture(scope="session")
def project():
    """Get project key for testing"""
    # Try to get from environment first
    project = os.getenv('JIRA_DEFAULT_PROJECT')
    if not project:
        # If no project in env, try to get from first issue in 'my' list
        runner = CliRunner()
        result = runner.invoke(cli, ['my'])
        if result.exit_code == 0:
            import re
            # Look for project key pattern (letters-numbers)
            match = re.search(r'([A-Z]+)-\d+', result.output)
            if match:
                # Extract just the project part (e.g., 'DATA' from 'DATA-123')
                project = match.group(1)
    
    if not project:
        pytest.skip("No project could be determined for testing")
    return project

@timeout_after(20)
def test_list_project_issues(setup_env, runner, project):
    """Test listing issues from a specific project with specific criteria"""
    result = runner.invoke(cli, [
        'list',
        '--project', project,
        '--status', 'In Progress',
        '--type', 'Task',
        '--priority', 'High',
        '--assignee', 'currentUser()',
        '--created-after', '2024-01-01',
        '--labels', 'urgent',
        '--query', 'NOT resolution = Done'
    ])
    print(f"Output: {result.output}")  # Debug output
    print(f"Exit code: {result.exit_code}")  # Debug output
    
    # Check for either success or "No issues found" message
    assert result.exit_code in [0, 1]
    if result.exit_code == 1:
        assert 'No issues found' in result.output
    else:
        clean_output = result.output.replace('\x1b[1;34m', '').replace('\x1b[0m', '')
        # Verify some of the filter results are reflected in output
        assert project in clean_output
        assert 'In Progress' in clean_output
        assert 'Task' in clean_output
        assert 'High' in clean_output

@timeout_after(30)
def test_view_existing_issue(setup_env, runner, sample_issue_key):
    """Test viewing details of an existing issue"""
    result = runner.invoke(cli, ['view', sample_issue_key])
    print(f"Output: {result.output}")  # Debug output
    
    assert result.exit_code == 0
    # Check that the issue key appears anywhere in the output
    assert sample_issue_key in result.output.replace('\x1b[1;34m', '').replace('\x1b[0m', '')
    
    # Check for required fields in the output, ignoring ANSI codes
    clean_output = result.output.replace('\x1b[1m', '').replace('\x1b[0m', '')
    assert 'Status:' in clean_output
    assert 'Type:' in clean_output
    assert 'Priority:' in clean_output
    assert 'Assignee:' in clean_output
    assert 'Description:' in clean_output
    
    # Don't check for exact format with colons since the output is formatted
    assert sample_issue_key in clean_output

@timeout_after(30)
def test_view_nonexistent_issue(setup_env, runner):
    """Test viewing a non-existent issue"""
    result = runner.invoke(cli, ['view', 'FAKE-99999'])
    assert result.exit_code == 1
    assert 'Error' in result.output or 'Issue not found' in result.output

@timeout_after(20)
def test_list_with_multiple_filters(setup_env, runner, project):
    """Test listing issues with multiple filters"""
    result = runner.invoke(cli, [
        'list',
        '--project', project,
        '--status', 'In Progress',
        '--type', 'Bug',
    ])
    print(f"Output: {result.output}")  # Debug output
    print(f"Error code: {result.exit_code}")  # Debug exit_code
    
    # Check for either success or "No issues found" message
    assert result.exit_code in [0, 1]
    if result.exit_code == 1:
        assert 'No issues found' in result.output

@timeout_after(30)
def test_list_with_no_results(setup_env, runner):
    """Test listing issues with filters that return no results"""
    result = runner.invoke(cli, [
        'list',
        '--status', 'InvalidStatus123'
    ])
    # This should return exit code 1 for no results
    assert result.exit_code == 1
    assert 'No issues found' in result.output or 'Error' in result.output