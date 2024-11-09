import os
import csv
from datetime import datetime
from jira import JIRA
from dotenv import load_dotenv
from .config import load_config
from .exceptions import ConfigurationError, JiraApiError, AuthenticationError, ValidationError

class JiraClient:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.config = self._load_environment()
        try:
            self.client = JIRA(
                server=self.config['JIRA_SERVER'],
                basic_auth=(self.config['JIRA_EMAIL'], self.config['JIRA_API_TOKEN'])
            )
        except Exception as e:
            raise AuthenticationError(f"Failed to authenticate with Jira: {str(e)}")

    def _load_environment(self):
        """Load configuration from environment variables"""
        required_vars = [
            'JIRA_SERVER', 
            'JIRA_EMAIL', 
            'JIRA_API_TOKEN'
        ]
        optional_vars = [
            'JIRA_DEFAULT_PROJECT',
            'JIRA_DEFAULT_ISSUE_TYPE'
        ]
        config = {}
        
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

    def get_issue(self, issue_key):
        """Retrieve a specific issue"""
        try:
            return self.client.issue(issue_key)
        except Exception as e:
            raise JiraApiError(f"Failed to get issue {issue_key}: {str(e)}")

    def search_issues(self, jql):
        """Search issues using JQL"""
        try:
            return self.client.search_issues(jql)
        except Exception as e:
            raise JiraApiError(f"JQL search failed: {str(e)}")

    def create_issue(self, fields):
        """Create a new issue"""
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

    def update_issue(self, issue_key, fields):
        """Update an existing issue"""
        try:
            issue = self.client.issue(issue_key)
            issue.update(fields=fields)
        except Exception as e:
            raise JiraApiError(f"Failed to update issue {issue_key}: {str(e)}")

    def add_comment(self, issue_key, comment_text):
        """Add a comment to an issue"""
        try:
            issue = self.client.issue(issue_key)
            self.client.add_comment(issue, comment_text)
        except Exception as e:
            raise JiraApiError(f"Failed to add comment to {issue_key}: {str(e)}")

    def export_issues(self, jql, output_file):
        """Export issues to CSV"""
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

    def add_attachment(self, issue_key, file_path):
        """Attach a file to an issue"""
        try:
            with open(file_path, 'rb') as f:
                self.client.add_attachment(issue_key, f)
        except Exception as e:
            raise JiraApiError(f"Failed to attach file to {issue_key}: {str(e)}")

    def log_work(self, issue_key, time_spent, comment=None):
        """Log work on an issue"""
        try:
            self.client.add_worklog(
                issue=issue_key,
                timeSpent=time_spent,
                comment=comment
            )
        except Exception as e:
            raise JiraApiError(f"Failed to log work on {issue_key}: {str(e)}")

    def bulk_update_issues(self, jql, status=None, assignee=None, add_labels=None):
        """Bulk update issues matching JQL query"""
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

    def get_transitions(self, issue_key):
        """Get available transitions for an issue"""
        try:
            return self.client.transitions(issue_key)
        except Exception as e:
            raise JiraApiError(f"Failed to get transitions for {issue_key}: {str(e)}")

    def transition_issue(self, issue_key, transition_name, resolution=None):
        """Transition an issue to a new status"""
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

    def get_sprints(self, board_id, state=None):
        """Get sprints for a board"""
        try:
            return self.client.sprints(board_id, state=state)
        except Exception as e:
            raise JiraApiError(f"Failed to get sprints for board {board_id}: {str(e)}")

    def add_to_sprint(self, sprint_id, issue_keys):
        """Add issues to a sprint"""
        try:
            self.client.add_issues_to_sprint(sprint_id, issue_keys)
        except Exception as e:
            raise JiraApiError(f"Failed to add issues to sprint {sprint_id}: {str(e)}")

    def create_sprint(self, board_id, name, start_date=None):
        """Create a new sprint"""
        try:
            sprint_args = {'name': name, 'board_id': board_id}
            
            if start_date:
                sprint_args['startDate'] = datetime.strptime(start_date, '%Y-%m-%d').isoformat()
            
            return self.client.create_sprint(**sprint_args)
        except Exception as e:
            raise JiraApiError(f"Failed to create sprint: {str(e)}")

    def get_field_map(self, issue_key=None):
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