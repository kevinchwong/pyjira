"""
Jira Client module for Jira CLI.

This module provides the main interface to the Jira API, handling all interactions
with the Jira server including:
- Authentication and configuration
- Issue operations (create, update, search)
- Attachments and comments
- Sprint management
- Field mapping
- Bulk operations

The module uses python-jira library for API interactions and provides error handling
and convenience methods for common operations.
"""

import os
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, BinaryIO
from jira import JIRA, Issue
from dotenv import load_dotenv
from .config import load_config
from .exceptions import ConfigurationError, JiraApiError, AuthenticationError, ValidationError
from jira.resources import Resource

class JiraClient:
    """
    Main client class for interacting with Jira.
    
    This class handles all Jira API operations and provides a high-level interface
    for the CLI commands. It manages authentication, configuration, and provides
    error handling for all API interactions.

    Attributes:
        config (Dict[str, str]): Configuration loaded from environment
        client (JIRA): Authenticated Jira client instance

    Raises:
        AuthenticationError: When Jira authentication fails
        ConfigurationError: When required configuration is missing
    """

    def __init__(self) -> None:
        """
        Initialize the Jira client.

        Loads configuration from environment and establishes connection to Jira.
        
        Raises:
            AuthenticationError: If authentication fails
            ConfigurationError: If required environment variables are missing
        """
        load_dotenv()
        self.config: Dict[str, str] = self._load_environment()
        try:
            self.client: JIRA = JIRA(
                server=self.config['JIRA_SERVER'],
                basic_auth=(self.config['JIRA_EMAIL'], self.config['JIRA_API_TOKEN'])
            )
        except Exception as e:
            raise AuthenticationError(f"Failed to authenticate with Jira: {str(e)}")

    def _load_environment(self) -> Dict[str, str]:
        """
        Load configuration from environment variables.

        Returns:
            Dict[str, str]: Dictionary containing configuration values

        Raises:
            ConfigurationError: If required variables are missing

        Example:
            >>> client = JiraClient()
            >>> config = client._load_environment()
            >>> print(config['JIRA_SERVER'])
        """
        required_vars: List[str] = [
            'JIRA_SERVER', 
            'JIRA_EMAIL', 
            'JIRA_API_TOKEN'
        ]
        optional_vars: List[str] = [
            'JIRA_DEFAULT_PROJECT',
            'JIRA_DEFAULT_ISSUE_TYPE'
        ]
        config: Dict[str, str] = {}
        
        # Load required variables
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                raise ConfigurationError(f"Missing required environment variable: {var}")
            config[var] = value
            
        # Load optional variables
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                config[var] = value
            
        return config

    def get_issue(self, issue_key: str) -> Issue:
        """
        Retrieve a specific issue from Jira.

        Args:
            issue_key (str): The issue key (e.g., 'PROJ-123')

        Returns:
            Issue: The Jira issue object

        Raises:
            JiraApiError: If the API request fails

        Example:
            >>> issue = client.get_issue('PROJ-123')
            >>> print(issue.fields.summary)
        """
        try:
            return self.client.issue(issue_key)
        except Exception as e:
            raise JiraApiError(f"Failed to get issue {issue_key}: {str(e)}")

    def search_issues(self, jql: str, max_results: int = 50) -> List[Issue]:
        """
        Search for issues using JQL (Jira Query Language).

        Args:
            jql (str): JQL query string to search issues
            max_results (int): Maximum number of results to return

        Returns:
            List[Issue]: List of matching Jira issues

        Raises:
            JiraApiError: If the search request fails

        Example:
            >>> issues = client.search_issues('project = DATA AND status = "In Progress"', max_results=50)
            >>> for issue in issues:
            ...     print(f"{issue.key}: {issue.fields.summary}")
        """
        try:
            start_at = 0
            all_issues = []
            
            while True:
                results = self.client.search_issues(
                    jql, 
                    startAt=start_at, 
                    maxResults=max_results
                )
                if not results:
                    break
                
                all_issues.extend(results)
                if len(results) < max_results:
                    break
                
                start_at += max_results
                
            return all_issues
        except Exception as e:
            raise JiraApiError(f"JQL search failed: {str(e)}")

    def create_issue(self, fields: Dict[str, Any]) -> Issue:
        """
        Create a new Jira issue.

        Args:
            fields (Dict[str, Any]): Dictionary containing issue fields including:
                - project: Project key or dict
                - summary: Issue summary
                - description: Issue description
                - issuetype: Issue type name or dict
                - priority: Priority name or dict
                - labels: List of labels
                - components: List of component names or dicts
                - customfield_*: Custom field values

        Returns:
            Issue: The created Jira issue

        Raises:
            JiraApiError: If issue creation fails
            ValidationError: If required fields are missing

        Example:
            >>> fields = {
            ...     'project': 'DATA',
            ...     'summary': 'New feature request',
            ...     'description': 'Feature details',
            ...     'issuetype': {'name': 'Story'}
            ... }
            >>> issue = client.create_issue(fields)
        """
        try:
            # Set default project if not specified
            if 'project' not in fields and 'JIRA_DEFAULT_PROJECT' in self.config:
                fields['project'] = self.config['JIRA_DEFAULT_PROJECT']
            
            # Set default issue type if not specified
            if 'issuetype' not in fields and 'JIRA_DEFAULT_ISSUE_TYPE' in self.config:
                fields['issuetype'] = self.config['JIRA_DEFAULT_ISSUE_TYPE']
                
            return self.client.create_issue(fields=fields)
        except Exception as e:
            raise JiraApiError(f"Failed to create issue: {str(e)}")

    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> None:
        """
        Update an existing Jira issue.

        Args:
            issue_key (str): The issue key to update (e.g., 'DATA-123')
            fields (Dict[str, Any]): Dictionary containing fields to update

        Raises:
            JiraApiError: If update fails
            ValidationError: If field values are invalid

        Example:
            >>> fields = {
            ...     'summary': 'Updated summary',
            ...     'priority': {'name': 'High'},
            ...     'labels': ['urgent', 'bug']
            ... }
            >>> client.update_issue('DATA-123', fields)
        """
        try:
            issue = self.client.issue(issue_key)
            issue.update(fields=fields)
        except Exception as e:
            raise JiraApiError(f"Failed to update issue {issue_key}: {str(e)}")

    def add_comment(self, issue_key: str, comment_text: str) -> None:
        """
        Add a comment to a Jira issue.

        Args:
            issue_key (str): The issue key to comment on
            comment_text (str): The comment text to add

        Raises:
            JiraApiError: If comment addition fails

        Example:
            >>> client.add_comment('DATA-123', 'Work in progress')
        """
        try:
            issue = self.client.issue(issue_key)
            self.client.add_comment(issue, comment_text)
        except Exception as e:
            raise JiraApiError(f"Failed to add comment to {issue_key}: {str(e)}")

    def export_issues(self, jql: str, output_file: str) -> None:
        """
        Export issues to CSV file.

        Args:
            jql (str): JQL query to select issues for export
            output_file (str): Path to the output CSV file

        Raises:
            JiraApiError: If export fails
            OSError: If file cannot be written

        Example:
            >>> client.export_issues('project = DATA', 'issues.csv')
        """
        try:
            issues = self.search_issues(jql)
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Key', 'Summary', 'Status', 'Priority', 'Assignee', 'Created', 'Updated'])
                
                for issue in issues:
                    writer.writerow([
                        issue.key,
                        issue.fields.summary,
                        issue.fields.status.name,
                        getattr(issue.fields.priority, 'name', 'None'),
                        getattr(issue.fields.assignee, 'displayName', 'Unassigned'),
                        issue.fields.created,
                        issue.fields.updated
                    ])
        except Exception as e:
            raise JiraApiError(f"Failed to export issues: {str(e)}")

    def add_attachment(self, issue_key: str, file_path: Union[str, BinaryIO]) -> None:
        """
        Attach a file to a Jira issue.

        Args:
            issue_key (str): The issue key to attach the file to
            file_path (Union[str, BinaryIO]): Path to file or file-like object

        Raises:
            JiraApiError: If attachment fails
            OSError: If file cannot be read

        Example:
            >>> client.add_attachment('DATA-123', 'screenshot.png')
            >>> with open('log.txt', 'rb') as f:
            ...     client.add_attachment('DATA-123', f)
        """
        try:
            if isinstance(file_path, str):
                with open(file_path, 'rb') as f:
                    self.client.add_attachment(issue_key, f)
            else:
                self.client.add_attachment(issue_key, file_path)
        except Exception as e:
            raise JiraApiError(f"Failed to attach file to {issue_key}: {str(e)}")

    def log_work(self, issue_key: str, time_spent: str, comment: Optional[str] = None) -> None:
        """
        Log work time on an issue.

        Args:
            issue_key (str): The issue key to log work on
            time_spent (str): Time spent in Jira format (e.g., "3h 30m")
            comment (Optional[str]): Optional comment for the work log

        Raises:
            JiraApiError: If work logging fails
            ValidationError: If time format is invalid

        Example:
            >>> client.log_work('DATA-123', '2h 30m', 'Code review')
            >>> client.log_work('DATA-123', '1d', 'Implementation')
        """
        try:
            self.client.add_worklog(
                issue=issue_key,
                timeSpent=time_spent,
                comment=comment
            )
        except Exception as e:
            raise JiraApiError(f"Failed to log work on {issue_key}: {str(e)}")

    def bulk_update_issues(self, jql: str, status: Optional[str] = None, 
                          assignee: Optional[str] = None, 
                          add_labels: Optional[str] = None) -> int:
        """
        Bulk update multiple issues matching a JQL query.

        Args:
            jql (str): JQL query to select issues for update
            status (Optional[str]): New status to set
            assignee (Optional[str]): New assignee username
            add_labels (Optional[str]): Comma-separated labels to add

        Returns:
            int: Number of issues updated

        Raises:
            JiraApiError: If bulk update fails
            ValidationError: If field values are invalid

        Example:
            >>> count = client.bulk_update_issues(
            ...     "project = DATA AND status = 'To Do'",
            ...     status="In Progress",
            ...     assignee="john.doe",
            ...     add_labels="urgent,critical"
            ... )
            >>> print(f"Updated {count} issues")
        """
        try:
            issues = self.search_issues(jql)
            updated = 0
            
            for issue in issues:
                fields = {}
                if status:
                    self.transition_issue(issue.key, status)
                if assignee:
                    fields['assignee'] = {'name': assignee}
                if add_labels:
                    current_labels = getattr(issue.fields, 'labels', [])
                    new_labels = add_labels.split(',')
                    fields['labels'] = list(set(current_labels + new_labels))
                
                if fields:
                    self.update_issue(issue.key, fields)
                    updated += 1
            
            return updated
        except Exception as e:
            raise JiraApiError(f"Bulk update failed: {str(e)}")

    def get_transitions(self, issue_key: str) -> List[Resource]:
        """
        Get available transitions for an issue.

        Args:
            issue_key (str): The issue key to get transitions for

        Returns:
            List[Resource]: List of available transitions

        Raises:
            JiraApiError: If transitions cannot be retrieved

        Example:
            >>> transitions = client.get_transitions('DATA-123')
            >>> for t in transitions:
            ...     print(f"{t['id']}: {t['name']} -> {t['to']['name']}")
        """
        try:
            return self.client.transitions(issue_key)
        except Exception as e:
            raise JiraApiError(f"Failed to get transitions for {issue_key}: {str(e)}")

    def transition_issue(self, issue_key: str, transition_name: str, resolution: Optional[str] = None) -> None:
        """
        Transition an issue to a new status.

        Args:
            issue_key (str): The issue key to transition
            transition_name (str): Name of the transition to perform
            resolution (Optional[str]): Resolution to set (for Done transitions)

        Raises:
            JiraApiError: If transition fails
            ValidationError: If transition name is invalid

        Example:
            >>> client.transition_issue('DATA-123', 'In Progress')
            >>> client.transition_issue('DATA-123', 'Done', resolution='Fixed')
        """
        try:
            transitions = self.get_transitions(issue_key)
            transition_id = None
            
            for t in transitions:
                if t['name'].lower() == transition_name.lower():
                    transition_id = t['id']
                    break
            
            if not transition_id:
                raise ValidationError(f"Transition '{transition_name}' not found")
            
            fields = {}
            if resolution:
                fields['resolution'] = {'name': resolution}
            
            self.client.transition_issue(issue_key, transition_id, fields=fields)
        except Exception as e:
            raise JiraApiError(f"Failed to transition {issue_key}: {str(e)}")

    def get_sprints(self, board_id: int, state: Optional[str] = None) -> List[Resource]:
        """
        Get sprints for a board.

        Args:
            board_id (int): ID of the board to get sprints from
            state (Optional[str]): Filter sprints by state (active/future/closed)

        Returns:
            List[Resource]: List of sprints

        Raises:
            JiraApiError: If sprints cannot be retrieved

        Example:
            >>> sprints = client.get_sprints(10, state='active')
            >>> for sprint in sprints:
            ...     print(f"{sprint.id}: {sprint.name} ({sprint.state})")
        """
        try:
            return self.client.sprints(board_id, state=state)
        except Exception as e:
            raise JiraApiError(f"Failed to get sprints for board {board_id}: {str(e)}")

    def add_to_sprint(self, sprint_id: int, issue_keys: List[str]) -> None:
        """
        Add issues to a sprint.

        Args:
            sprint_id (int): ID of the sprint to add issues to
            issue_keys (List[str]): List of issue keys to add

        Raises:
            JiraApiError: If issues cannot be added to sprint

        Example:
            >>> client.add_to_sprint(123, ['DATA-123', 'DATA-124'])
        """
        try:
            self.client.add_issues_to_sprint(sprint_id, issue_keys)
        except Exception as e:
            raise JiraApiError(f"Failed to add issues to sprint {sprint_id}: {str(e)}")

    def create_sprint(self, board_id: int, name: str, start_date: Optional[str] = None) -> Resource:
        """
        Create a new sprint.

        Args:
            board_id (int): ID of the board to create sprint in
            name (str): Name of the new sprint
            start_date (Optional[str]): Start date in YYYY-MM-DD format

        Returns:
            Resource: Created sprint resource

        Raises:
            JiraApiError: If sprint creation fails
            ValidationError: If date format is invalid

        Example:
            >>> sprint = client.create_sprint(10, "Sprint 1", "2024-01-01")
            >>> print(f"Created sprint {sprint.id}: {sprint.name}")
        """
        try:
            sprint_args = {'name': name, 'board_id': board_id}
            
            if start_date:
                sprint_args['startDate'] = datetime.strptime(start_date, '%Y-%m-%d').isoformat()
            
            return self.client.create_sprint(**sprint_args)
        except Exception as e:
            raise JiraApiError(f"Failed to create sprint: {str(e)}")

    def get_field_map(self, issue_key: Optional[str] = None) -> Dict[str, Any]:
        """Get all fields and their IDs, optionally with values from a specific issue"""
        try:
            # Get all fields
            fields = self.client.fields()
            
            # Create field map
            field_map = {}
            for field in fields:
                # Handle fields that might not have all attributes
                field_info = {
                    'id': field.get('id', 'unknown'),
                    'name': field.get('name', 'unknown'),
                    'type': field.get('schema', {}).get('type', 'unknown') if 'schema' in field else 'unknown',
                    'custom': field.get('custom', False)
                }
                
                # If issue key provided, get the value
                if issue_key:
                    try:
                        issue = self.get_issue(issue_key)
                        # Convert field ID to a valid Python attribute name
                        field_attr = field['id'].replace('-', '_').replace('.', '_')
                        value = getattr(issue.fields, field_attr, None)
                        
                        if value is not None:
                            if hasattr(value, 'value'):  # Handle custom field objects
                                field_info['value'] = value.value
                            elif hasattr(value, 'name'):  # Handle named resources (e.g., users, priorities)
                                field_info['value'] = value.name
                            elif isinstance(value, (list, dict)):  # Handle complex fields
                                field_info['value'] = str(value)
                            else:  # Handle simple values
                                field_info['value'] = str(value)
                    except Exception as e:
                        field_info['value'] = f"Error getting value: {str(e)}"
                
                field_map[field['name']] = field_info
            
            return field_map
        except Exception as e:
            raise JiraApiError(f"Failed to get field map: {str(e)}")

    def bulk_update_batch(self, issues: List[Issue], status: Optional[str] = None,
                         assignee: Optional[str] = None, add_labels: Optional[str] = None) -> None:
        """
        Update a batch of issues.

        Args:
            issues (List[Issue]): List of issues to update
            status (Optional[str]): New status to set
            assignee (Optional[str]): New assignee username
            add_labels (Optional[str]): Comma-separated labels to add

        Raises:
            JiraApiError: If batch update fails

        Example:
            >>> issues = client.search_issues('project = DATA')
            >>> client.bulk_update_batch(issues, status='In Progress')
        """
        try:
            for issue in issues:
                fields = {}
                if status:
                    self.transition_issue(issue.key, status)
                if assignee:
                    fields['assignee'] = {'name': assignee}
                if add_labels:
                    current_labels = getattr(issue.fields, 'labels', [])
                    new_labels = add_labels.split(',')
                    fields['labels'] = list(set(current_labels + new_labels))
                
                if fields:
                    self.update_issue(issue.key, fields)
        except Exception as e:
            raise JiraApiError(f"Failed to update batch: {str(e)}")

    def get_velocity_metrics(self, board_id: int, days: int = 14) -> List[Dict[str, Any]]:
        """
        Get velocity metrics for a board.

        Calculates velocity metrics including completed points, completed issues,
        and average points per issue for recent sprints.

        Args:
            board_id (int): ID of the board to analyze
            days (int, optional): Number of days to look back. Defaults to 14.

        Returns:
            List[Dict[str, Any]]: List of sprint metrics, each containing:
                - name: Sprint name
                - completed_points: Story points completed
                - completed_issues: Number of issues completed
                - average_points: Average points per issue

        Raises:
            JiraApiError: If metrics cannot be retrieved

        Example:
            >>> metrics = client.get_velocity_metrics(10, days=30)
            >>> for m in metrics:
            ...     print(f"{m['name']}: {m['completed_points']} points")
        """
        try:
            # Get completed sprints
            sprints = self.get_sprints(board_id, state='closed')
            metrics = []
            
            for sprint in sprints:
                # Get issues completed in sprint
                jql = (
                    f"sprint = {sprint.id} AND "
                    f"status = Done AND "
                    f"updated >= -{days}d"
                )
                issues = self.search_issues(jql)
                
                # Calculate metrics
                completed_points = sum(
                    getattr(issue.fields, 'customfield_10000', 0) or 0 
                    for issue in issues
                )
                completed_issues = len(issues)
                average_points = (
                    completed_points / completed_issues 
                    if completed_issues > 0 else 0
                )
                
                metrics.append({
                    'name': sprint.name,
                    'completed_points': completed_points,
                    'completed_issues': completed_issues,
                    'average_points': average_points
                })
            
            return metrics
        except Exception as e:
            raise JiraApiError(f"Failed to get velocity metrics: {str(e)}")

    def create_link(self, issue_key: str, target_issue: str, link_type: str) -> None:
        """
        Create a link between two issues.

        Args:
            issue_key (str): Source issue key
            target_issue (str): Target issue key
            link_type (str): Type of link (e.g., "blocks", "relates to")

        Raises:
            JiraApiError: If link creation fails
            ValidationError: If link type is invalid

        Example:
            >>> client.create_link('DATA-123', 'DATA-456', 'blocks')
            >>> client.create_link('DATA-123', 'DATA-789', 'relates to')
        """
        try:
            self.client.create_issue_link(
                type=link_type,
                inwardIssue=issue_key,
                outwardIssue=target_issue
            )
        except Exception as e:
            raise JiraApiError(f"Failed to create link: {str(e)}")

    def add_watcher(self, issue_key: str) -> None:
        """
        Add the current user as a watcher to an issue.

        Args:
            issue_key (str): The issue key to watch

        Raises:
            JiraApiError: If watcher cannot be added

        Example:
            >>> client.add_watcher('DATA-123')
        """
        try:
            self.client.add_watcher(issue_key, self.config['JIRA_EMAIL'])
        except Exception as e:
            raise JiraApiError(f"Failed to add watcher to {issue_key}: {str(e)}")

    def remove_watcher(self, issue_key: str) -> None:
        """
        Remove the current user as a watcher from an issue.

        Args:
            issue_key (str): The issue key to unwatch

        Raises:
            JiraApiError: If watcher cannot be removed

        Example:
            >>> client.remove_watcher('DATA-123')
        """
        try:
            self.client.remove_watcher(issue_key, self.config['JIRA_EMAIL'])
        except Exception as e:
            raise JiraApiError(f"Failed to remove watcher from {issue_key}: {str(e)}")

    def get_field_map(self, issue_key: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get all fields and their IDs, optionally with values from a specific issue.

        This method retrieves all available Jira fields and their metadata,
        including custom fields. If an issue key is provided, it also retrieves
        the current values of these fields for that issue.

        Args:
            issue_key (Optional[str]): Issue key to get field values from

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping field names to their details:
                - id: Field ID
                - name: Field name
                - type: Field type
                - custom: Whether it's a custom field
                - value: Current value (if issue_key provided)

        Raises:
            JiraApiError: If field information cannot be retrieved

        Example:
            >>> fields = client.get_field_map()
            >>> custom_fields = {k: v for k, v in fields.items() if v['custom']}
            >>> field_values = client.get_field_map('DATA-123')
        """
        try:
            fields = self.client.fields()
            field_map = {}
            
            for field in fields:
                field_info = {
                    'id': field.get('id', 'unknown'),
                    'name': field.get('name', 'unknown'),
                    'type': field.get('schema', {}).get('type', 'unknown') if 'schema' in field else 'unknown',
                    'custom': field.get('custom', False)
                }
                
                if issue_key:
                    try:
                        issue = self.get_issue(issue_key)
                        field_attr = field['id'].replace('-', '_').replace('.', '_')
                        value = getattr(issue.fields, field_attr, None)
                        
                        if value is not None:
                            if hasattr(value, 'value'):
                                field_info['value'] = value.value
                            elif hasattr(value, 'name'):
                                field_info['value'] = value.name
                            elif isinstance(value, (list, dict)):
                                field_info['value'] = str(value)
                            else:
                                field_info['value'] = str(value)
                    except Exception as e:
                        field_info['value'] = f"Error getting value: {str(e)}"
                
                field_map[field['name']] = field_info
            
            return field_map
        except Exception as e:
            raise JiraApiError(f"Failed to get field map: {str(e)}")