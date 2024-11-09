from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from datetime import datetime

console = Console()

class IssueFormatter:
    @staticmethod
    def format_issue(issue):
        """Format a single issue for display"""
        panel = Panel(
            f"""[bold blue]{issue.key}[/bold blue]: {issue.fields.summary}
[bold]Status:[/bold] {issue.fields.status.name}
[bold]Type:[/bold] {issue.fields.issuetype.name}
[bold]Priority:[/bold] {issue.fields.priority.name}
[bold]Assignee:[/bold] {getattr(issue.fields.assignee, 'displayName', 'Unassigned')}
[bold]Reporter:[/bold] {issue.fields.reporter.displayName}
[bold]Created:[/bold] {datetime.strptime(issue.fields.created[:19], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')}

[bold]Description:[/bold]
{issue.fields.description or 'No description provided'}
""",
            title=f"Issue Details",
            expand=False
        )
        return panel

    @staticmethod
    def format_issue_list(issues):
        """Format a list of issues as a table"""
        table = Table(show_header=True, header_style="bold")
        table.add_column("Key")
        table.add_column("Summary")
        table.add_column("Status")
        table.add_column("Priority")
        table.add_column("Assignee")
        
        for issue in issues:
            table.add_row(
                issue.key,
                issue.fields.summary,
                issue.fields.status.name,
                issue.fields.priority.name,
                getattr(issue.fields.assignee, 'displayName', 'Unassigned')
            )
        
        return table

    @staticmethod
    def format_transitions(transitions):
        """Format available transitions as a table"""
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("To Status")
        
        for t in transitions:
            table.add_row(
                str(t['id']),
                t['name'],
                t['to']['name']
            )
        
        return table

    @staticmethod
    def format_sprints(sprints):
        """Format sprints as a table"""
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("State")
        table.add_column("Start Date")
        table.add_column("End Date")
        
        for sprint in sprints:
            table.add_row(
                str(sprint.id),
                sprint.name,
                sprint.state,
                sprint.startDate[:10] if hasattr(sprint, 'startDate') else 'N/A',
                sprint.endDate[:10] if hasattr(sprint, 'endDate') else 'N/A'
            )
        
        return table 