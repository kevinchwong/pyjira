# Core imports and setup
import click
import os
from typing import Optional, List, Dict, Any, Tuple
from .client import JiraClient
from .config import load_config
from pathlib import Path
from .exceptions import JiraCliError
from rich.console import Console
from rich.table import Table
from .formatters import IssueFormatter
from rich.progress import Progress
from rich.prompt import Confirm
import json
from datetime import datetime
from click import Context

console = Console()

def get_alias_command(alias_name: str) -> Optional[str]:
    """Get the command for an alias from config"""
    config = load_config()
    aliases = config.get('aliases', {})
    return aliases.get(alias_name)

# Main CLI group
@click.group(invoke_without_command=True)
@click.version_option(version="1.0.0")
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def cli(ctx: Context, debug: bool) -> None:
    """Jira CLI - Command line interface for Jira"""
    if debug:
        os.environ['JIRA_CLI_DEBUG'] = 'true'
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

# Alias handling commands
@cli.command(hidden=True)
@click.argument('command_or_alias')
@click.argument('args', nargs=-1)
def run(command_or_alias: str, args: Tuple[str, ...]) -> None:
    """Run a command or alias"""
    alias_command = get_alias_command(command_or_alias)
    if alias_command:
        # Split the alias command into parts and handle quotes properly
        parts = []
        current_part = ''
        in_quotes = False
        
        for char in alias_command:
            if char == '"':
                in_quotes = not in_quotes
                current_part += char
            elif char == ' ' and not in_quotes:
                if current_part:
                    parts.append(current_part)
                current_part = ''
            else:
                current_part += char
        
        if current_part:
            parts.append(current_part)
        
        command_name = parts[0]
        command_args = parts[1:]  # Keep quotes intact
        
        # Add any additional args passed to the command
        command_args.extend(args)
        
        if command_name in cli.commands:
            ctx = click.get_current_context()
            # Create a new context for the command
            with ctx.scope(cleanup=False):
                # For the list command, ensure arguments are properly formatted
                if command_name == 'list':
                    # Convert the arguments to Click's expected format
                    formatted_args = []
                    for arg in command_args:
                        if arg.startswith('--'):
                            # Split option and value if combined
                            if '=' in arg:
                                opt, val = arg.split('=', 1)
                                formatted_args.extend([opt, val.strip('"')])
                            else:
                                formatted_args.append(arg)
                        else:
                            formatted_args.append(arg.strip('"'))
                    command_args = formatted_args
                
                return cli.commands[command_name].main(args=command_args, standalone_mode=False)
        else:
            raise click.UsageError(f"Unknown command: {command_name}")
    else:
        # If not an alias, treat as a regular command
        if command_or_alias in cli.commands:
            ctx = click.get_current_context()
            with ctx.scope(cleanup=False):
                return cli.commands[command_or_alias].main(args=args, standalone_mode=False)
        else:
            raise click.UsageError(f"Unknown command: {command_or_alias}")

def create_alias_command(alias_name: str) -> None:
    """Create a command function for an alias"""
    @cli.command(name=alias_name)
    @click.argument('args', nargs=-1)
    def alias_command(args: Tuple[str, ...]) -> None:
        """Alias command"""
        ctx = click.get_current_context()
        return ctx.invoke(run, command_or_alias=alias_name, args=args)
    return None

# Register all aliases as commands
config = load_config()
aliases = config.get('aliases', {})
for alias_name in aliases:
    create_alias_command(alias_name)

# Issue viewing and management commands
@cli.command()
@click.argument('issue_key')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'markdown']), default='table', help='Output format')
def view(issue_key: str, format: str) -> None:
    """View a specific issue"""
    try:
        client = JiraClient()
        issue = client.get_issue(issue_key)
        formatter = IssueFormatter()
        
        if format == 'table':
            console.print(formatter.format_issue(issue))
        elif format == 'json':
            # Convert issue to JSON
            issue_dict = {
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'assignee': getattr(issue.fields.assignee, 'displayName', 'Unassigned'),
                'created': issue.fields.created,
                'updated': issue.fields.updated,
                'description': issue.fields.description
            }
            console.print(json.dumps(issue_dict, indent=2))
        else:  # markdown
            console.print(formatter.format_issue_markdown(issue))
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)

# Bulk operations
@cli.command()
@click.argument('query')
@click.option('--status', help='New status')
@click.option('--assignee', help='New assignee')
@click.option('--add-labels', help='Labels to add (comma-separated)')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.option('--batch-size', default=50, help='Number of issues to process at once')
@click.option('--project', help='Filter by project key')
def bulk_update(query: str, status: Optional[str], assignee: Optional[str], add_labels: Optional[str], yes: bool, batch_size: int, project: Optional[str] = None) -> None:
    """Bulk update issues matching JQL query"""
    try:
        client = JiraClient()
        
        # Add project filter if specified or use default
        project_to_use = project or os.getenv('JIRA_DEFAULT_PROJECT')
        if project_to_use:
            query = f"project = {project_to_use} AND ({query})" if query else f"project = {project_to_use}"
        
        issues = client.search_issues(query)
        total = len(issues)
        
        if not yes:
            if not Confirm.ask(f"Are you sure you want to update {total} issues?"):
                click.echo("Operation cancelled")
                return
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Updating issues...", total=total)
            updated = 0
            batch = []
            
            for issue in issues:
                batch.append(issue)
                if len(batch) >= batch_size:
                    client.bulk_update_batch(batch, status, assignee, add_labels)
                    updated += len(batch)
                    progress.update(task, advance=len(batch))
                    batch = []
            
            # Process remaining issues
            if batch:
                client.bulk_update_batch(batch, status, assignee, add_labels)
                updated += len(batch)
                progress.update(task, advance=len(batch))
        
        console.print(f"[green]Successfully updated {updated} issues[/green]")
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)

# Issue relationship management
@cli.command()
@click.argument('issue_key')
@click.option('--watch/--unwatch', default=True, help='Add or remove watcher')
def watch(issue_key: str, watch: bool) -> None:
    """Add or remove yourself as a watcher"""
    try:
        client = JiraClient()
        if watch:
            client.add_watcher(issue_key)
            click.echo(f"Added watcher to {issue_key}")
        else:
            client.remove_watcher(issue_key)
            click.echo(f"Removed watcher from {issue_key}")
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)

# Board and sprint management commands
@cli.command()
@click.argument('board_id')
@click.option('--days', default=14, help='Number of days to analyze')
def velocity(board_id: str, days: int) -> None:
    """Show velocity metrics for a board"""
    try:
        client = JiraClient()
        metrics = client.get_velocity_metrics(board_id, days)
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Sprint")
        table.add_column("Completed Points")
        table.add_column("Completed Issues")
        table.add_column("Average Points/Issue")
        
        for sprint in metrics:
            table.add_row(
                sprint['name'],
                str(sprint['completed_points']),
                str(sprint['completed_issues']),
                f"{sprint['average_points']:.1f}"
            )
        
        console.print(table)
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)

# Sprint subcommands group
@cli.group(invoke_without_command=True)
@click.pass_context
def sprint(ctx: Context) -> None:
    """Sprint management commands"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@sprint.command(name='list')
@click.option('--board', required=True, help='Board ID')
@click.option('--state', help='Sprint state (active/future/closed)')
def list_sprints(board: str, state: Optional[str]) -> None:
    """List sprints for a board"""
    client = JiraClient()
    sprints = client.get_sprints(board, state)
    for sprint in sprints:
        click.echo(f"{sprint.id}: {sprint.name} ({sprint.state})")

@sprint.command(name='add')
@click.argument('sprint_id')
@click.argument('issue_keys', nargs=-1)
def add_to_sprint(sprint_id: str, issue_keys: Tuple[str, ...]) -> None:
    """Add issues to a sprint"""
    client = JiraClient()
    client.add_to_sprint(sprint_id, issue_keys)
    click.echo(f"Added {len(issue_keys)} issues to sprint {sprint_id}")

@sprint.command(name='create')
@click.option('--board', required=True, help='Board ID')
@click.option('--name', required=True, help='Sprint name')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
def create_sprint(board: str, name: str, start_date: Optional[str]) -> None:
    """Create a new sprint"""
    client = JiraClient()
    sprint = client.create_sprint(board, name, start_date)
    click.echo(f"Created sprint: {sprint.id}")

# Field inspection commands
@cli.command()
@click.option('--issue', help='Issue key to get field values from')
@click.option('--custom-only', is_flag=True, help='Show only custom fields')
@click.option('--with-values', is_flag=True, help='Show field values (requires --issue)')
def fields(issue: Optional[str], custom_only: bool, with_values: bool) -> None:
    """List all available fields and their IDs"""
    try:
        client = JiraClient()
        field_map = client.get_field_map(issue if with_values else None)
        
        # Create table
        table = Table(show_header=True, header_style="bold")
        table.add_column("Name")
        table.add_column("ID")
        table.add_column("Type")
        if with_values:
            table.add_column("Value")
        
        # Sort fields by name
        sorted_fields = sorted(field_map.items())
        
        for name, info in sorted_fields:
            # Skip non-custom fields if custom-only flag is set
            if custom_only and not info['custom']:
                continue
                
            row = [
                name,
                info['id'],
                info['type']
            ]
            if with_values:
                row.append(info.get('value', ''))
            
            table.add_row(*row)
        
        console.print(table)
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)

# Issue update and modification commands
@cli.command()
@click.argument('issue_key')
@click.option('--status', help='New status')
@click.option('--assignee', help='Assignee username')
@click.option('--priority', help='Priority level')
@click.option('--labels', help='Comma-separated labels')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
def update(issue_key: str, status: Optional[str], assignee: Optional[str], 
          priority: Optional[str], labels: Optional[str], yes: bool) -> None:
    """Update an issue"""
    try:
        if not yes:
            if not Confirm.ask(f"Are you sure you want to update {issue_key}?"):
                click.echo("Operation cancelled")
                return
                
        client = JiraClient()
        fields = {}
        
        if status:
            fields['status'] = status
        if assignee:
            fields['assignee'] = assignee
        if priority:
            fields['priority'] = priority
        if labels:
            fields['labels'] = labels.split(',')
        
        client.update_issue(issue_key, fields)
        click.echo(f"Updated issue: {issue_key}")
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)

@cli.command()
@click.argument('issue_key')
@click.argument('comment_text')
def comment(issue_key: str, comment_text: str) -> None:
    """Add a comment to an issue"""
    client = JiraClient()
    client.add_comment(issue_key, comment_text)
    click.echo(f"Added comment to {issue_key}")

# Export and attachment handling
@cli.command()
@click.argument('query')
@click.option('--output', help='Output CSV file path')
def export(query: str, output: Optional[str]) -> None:
    """Export issues to CSV"""
    client = JiraClient()
    client.export_issues(query, output)
    click.echo(f"Exported issues to {output}")

@cli.command()
@click.argument('issue_key')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def attach(issue_key: str, files: Tuple[str, ...]) -> None:
    """Attach files to an issue"""
    client = JiraClient()
    for file in files:
        client.add_attachment(issue_key, file)
        click.echo(f"Attached {file} to {issue_key}")

# Time tracking and work logging
@cli.command()
@click.argument('issue_key')
@click.option('--time', required=True, help='Time spent (e.g., "3h 30m")')
@click.option('--comment', help='Work log comment')
def log(issue_key: str, time: str, comment: Optional[str] = None) -> None:
    """Log work on an issue"""
    try:
        # Validate time format
        if not any(unit in time for unit in ['w', 'd', 'h', 'm']):
            raise click.UsageError('Time must include units (w=weeks, d=days, h=hours, m=minutes)')
            
        client = JiraClient()
        client.log_work(issue_key, time, comment)
        click.echo(f"Logged {time} on {issue_key}")
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)

# Issue listing and searching
@cli.command()
@click.option('--query', default='', help='JQL query string')
@click.option('--status', default=None, help='Filter by status')
@click.option('--assignee', default=None, help='Filter by assignee (use "currentUser()" for yourself)')
@click.option('--project', default=None, help='Filter by project key')
def list(query: str = '', status: Optional[str] = None, assignee: Optional[str] = None, project: Optional[str] = None) -> None:
    """List issues using JQL. If no JQL provided, uses filters or shows all assigned issues."""
    try:
        client = JiraClient()
        
        # Build JQL from options
        conditions = []
        
        # Use project from command line or default from environment
        project_to_use = project or os.getenv('JIRA_DEFAULT_PROJECT')
        if project_to_use:
            conditions.append(f"project = {project_to_use}")
            
        if assignee:
            conditions.append(f"assignee = {assignee}")
        if status:
            conditions.append(f"status = '{status}'")
        
        # If query is provided, use it as a condition
        if query:
            conditions.append(f"({query})")
        # Default to showing user's issues if no filters provided
        elif not conditions:
            conditions.append("assignee = currentUser()")
        
        jql = " AND ".join(conditions)
        
        issues = client.search_issues(jql)
        if not issues:
            console.print("[yellow]No issues found matching the criteria[/yellow]")
            return
        
        formatter = IssueFormatter()
        table = formatter.format_issue_list(issues)
        console.print(table)
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {str(e)}[/red]")
        if os.getenv('JIRA_CLI_DEBUG'):
            raise
        exit(1)

# Issue creation and workflow commands
@cli.command()
@click.option('--project', help='Project key')
@click.option('--summary', required=True, help='Issue summary')
@click.option('--description', help='Issue description')
@click.option('--priority', help='Issue priority')
@click.option('--labels', help='Comma-separated labels')
@click.option('--template', help='Template name to use')
@click.option('--custom-field', multiple=True, help='Custom field in format "field=value"')
def create(project: Optional[str], summary: str, description: Optional[str], priority: Optional[str], 
          labels: Optional[str], template: Optional[str], custom_field: Tuple[str, ...]) -> None:
    """Create a new issue"""
    try:
        client = JiraClient()
        
        # Use project from command line or default from environment
        if not project:
            project = os.getenv('JIRA_DEFAULT_PROJECT')
            if not project:
                raise click.UsageError("Project is required. Specify with --project or set JIRA_DEFAULT_PROJECT")
        
        fields = {
            'project': project,
            'summary': summary,
            'description': description
        }
        
        # Use default issue type if not specified in template
        if 'issuetype' not in fields and os.getenv('JIRA_DEFAULT_ISSUE_TYPE'):
            fields['issuetype'] = {'name': os.getenv('JIRA_DEFAULT_ISSUE_TYPE')}
        
        if priority:
            fields['priority'] = {'name': priority}
        if labels:
            fields['labels'] = labels.split(',')
        
        if template:
            template_fields = load_config(f'templates/{template}.yaml')
            fields.update(template_fields)
        
        for field in custom_field:
            key, value = field.split('=')
            fields[key] = value
        
        issue = client.create_issue(fields)
        click.echo(f"Created issue: {issue.key}")
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)

@cli.command()
@click.argument('issue_key')
def transitions(issue_key: str) -> None:
    """List available transitions for an issue"""
    try:
        client = JiraClient()
        transitions = client.get_transitions(issue_key)
        
        # Create table for transitions
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("To Status", style="yellow")
        
        # Sort transitions by name for better readability
        sorted_transitions = sorted(transitions, key=lambda x: x['name'])
        
        for t in sorted_transitions:
            table.add_row(
                str(t['id']),
                t['name'],
                t['to']['name']
            )
        
        console.print(table)
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)

@cli.command()
@click.argument('issue_key')
@click.argument('transition_name')
@click.option('--resolution', help='Resolution when transitioning to Done')
def transition(issue_key: str, transition_name: str, resolution: Optional[str]) -> None:
    """Transition an issue to a new status"""
    client = JiraClient()
    client.transition_issue(issue_key, transition_name, resolution)
    click.echo(f"Transitioned {issue_key} to {transition_name}")

# Issue linking and relationships
@cli.command()
@click.argument('issue_key')
@click.option('--link-type', required=True, help='Type of link (e.g., "blocks", "relates to")')
@click.argument('target_issue')
def link(issue_key: str, link_type: str, target_issue: str) -> None:
    """Link two issues together"""
    try:
        # Validate both issues exist before linking
        client = JiraClient()
        # Check source issue
        client.get_issue(issue_key)
        # Check target issue
        client.get_issue(target_issue)
        # Create link
        client.create_link(issue_key, target_issue, link_type)
        click.echo(f"Created {link_type} link between {issue_key} and {target_issue}")
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)

# Add this with the other CLI commands
@cli.command()
@click.option('--status', help='Filter by status')
def my(status: Optional[str] = None) -> None:
    """Show issues assigned to you"""
    try:
        # Reuse list command logic with currentUser() assignee
        ctx = click.get_current_context()
        return ctx.invoke(list, assignee='currentUser()', status=status)
    except JiraCliError as e:
        console.print(f"[red]{str(e)}[/red]")
        exit(1)