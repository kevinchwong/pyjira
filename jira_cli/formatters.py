"""
Formatters module for Jira CLI.

This module provides formatting utilities for displaying Jira issues and related data
in various formats including rich text tables, panels, and markdown. It uses the Rich
library to create beautiful terminal output.

The module includes:
- IssueFormatter: Main class for formatting Jira issues and related data
- Support for table, panel, and markdown output formats
- Color-coded and styled terminal output
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from datetime import datetime
from typing import Any, List, Dict
from jira import Issue
from jira.resources import Resource

console = Console()

class IssueFormatter:
    """
    Formatter class for Jira issues and related data.
    
    This class provides static methods to format Jira issues and related data
    in various formats suitable for terminal display. It uses Rich library
    components for beautiful and readable output.
    """

    @staticmethod
    def format_issue(issue: Issue) -> Panel:
        """
        Format a single issue as a Rich panel with detailed information.

        Args:
            issue (Issue): The Jira issue to format

        Returns:
            Panel: A Rich panel containing formatted issue details

        Example:
            >>> formatter = IssueFormatter()
            >>> panel = formatter.format_issue(issue)
            >>> console.print(panel)
        """
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
    def format_issue_list(issues: List[Issue]) -> Table:
        """
        Format a list of issues as a Rich table.

        Args:
            issues (List[Issue]): List of Jira issues to format

        Returns:
            Table: A Rich table containing the formatted issue list

        Example:
            >>> formatter = IssueFormatter()
            >>> table = formatter.format_issue_list(issues)
            >>> console.print(table)
        """
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
    def format_transitions(transitions: List[Dict[str, Any]]) -> Table:
        """
        Format issue transitions as a Rich table.

        Args:
            transitions (List[Dict[str, Any]]): List of transition dictionaries

        Returns:
            Table: A Rich table containing the formatted transitions

        Example:
            >>> formatter = IssueFormatter()
            >>> table = formatter.format_transitions(transitions)
            >>> console.print(table)
        """
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("To Status", style="yellow")
        
        for t in transitions:
            table.add_row(
                str(t['id']),
                t['name'],
                t['to']['name']
            )
        
        return table

    @staticmethod
    def format_sprints(sprints: List[Resource]) -> Table:
        """
        Format sprint information as a Rich table.

        Args:
            sprints (List[Resource]): List of Jira sprint resources

        Returns:
            Table: A Rich table containing the formatted sprint information

        Example:
            >>> formatter = IssueFormatter()
            >>> table = formatter.format_sprints(sprints)
            >>> console.print(table)
        """
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

    @staticmethod
    def format_issue_markdown(issue: Issue) -> str:
        """
        Format an issue as a markdown string.

        Args:
            issue (Issue): The Jira issue to format

        Returns:
            str: Markdown formatted string containing issue details

        Example:
            >>> formatter = IssueFormatter()
            >>> markdown = formatter.format_issue_markdown(issue)
            >>> print(markdown)
        """
        return f"""# {issue.key}: {issue.fields.summary}

**Status:** {issue.fields.status.name}  
**Type:** {issue.fields.issuetype.name}  
**Priority:** {issue.fields.priority.name}  
**Assignee:** {getattr(issue.fields.assignee, 'displayName', 'Unassigned')}  
**Reporter:** {issue.fields.reporter.displayName}  
**Created:** {datetime.strptime(issue.fields.created[:19], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')}

## Description
{issue.fields.description or 'No description provided'}
"""