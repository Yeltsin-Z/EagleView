#!/usr/bin/env python3
"""
Eagle's View - Release Leader Dashboard
Data Fetcher for Linear Issues

This script fetches issues from two sources and merges them:
1. Issues with 'preprod-v3' label (excluding 'launched' items) - for main table
2. All issues with 'Release Blocker' label - for release blocker tracking
"""

import os
import sys
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LinearViewFetcher:
    """Fetch items from a Linear custom view"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('LINEAR_API_KEY')
        if not self.api_key:
            raise ValueError("LINEAR_API_KEY is required. Set it in .env file or pass as argument.")
        
        self.base_url = "https://api.linear.app/graphql"
        self.headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json',
        }
    
    def _make_request(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GraphQL request to Linear API"""
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if 'errors' in result:
            raise Exception(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}")
        
        return result
    
    def get_custom_view(self, view_id: str) -> Optional[Dict[str, Any]]:
        """Fetch custom view details by ID"""
        query = """
        query GetCustomView($viewId: String!) {
          customView(id: $viewId) {
            id
            name
            description
            icon
            color
            createdAt
            updatedAt
            team {
              id
              name
              key
            }
            creator {
              id
              name
              email
            }
            filters
          }
        }
        """
        
        variables = {'viewId': view_id}
        
        try:
            result = self._make_request(query, variables)
            return result.get('data', {}).get('customView')
        except Exception as e:
            print(f"Error fetching custom view: {e}")
            return None
    
    def get_issues_from_view(self, view_id: str, max_issues: int = 1000) -> List[Dict[str, Any]]:
        """Fetch all issues from a custom view"""
        
        # First get the view details to understand the filters
        view = self.get_custom_view(view_id)
        if not view:
            print(f"Could not find view with ID: {view_id}")
            return []
        
        print(f"Fetching issues from view: {view.get('name', 'Unknown')}")
        team = view.get('team')
        print(f"Team: {team.get('name', 'Unknown') if team else 'Unknown'}")
        
        # Fetch issues with pagination
        all_issues = []
        has_next_page = True
        end_cursor = None
        
        while has_next_page:
            query = """
            query GetViewIssues($viewId: String!, $first: Int!, $after: String) {
              customView(id: $viewId) {
                id
                name
                issues(first: $first, after: $after) {
                  pageInfo {
                    hasNextPage
                    endCursor
                  }
                  nodes {
                    id
                    identifier
                    title
                    description
                    url
                    number
                    state {
                      id
                      name
                      type
                      color
                    }
                    priority
                    priorityLabel
                    estimate
                    dueDate
                    createdAt
                    updatedAt
                    completedAt
                    canceledAt
                    archivedAt
                    labels {
                      nodes {
                        id
                        name
                        color
                      }
                    }
                    team {
                      id
                      name
                      key
                    }
                    project {
                      id
                      name
                    }
                    cycle {
                      id
                      name
                      number
                    }
                    assignee {
                      id
                      name
                      email
                      displayName
                    }
                    creator {
                      id
                      name
                      email
                    }
                    subscribers {
                      nodes {
                        id
                        name
                        email
                        displayName
                      }
                    }
                    parent {
                      id
                      identifier
                      title
                    }
                    children {
                      nodes {
                        id
                        identifier
                        title
                      }
                    }
                  }
                }
              }
            }
            """
            
            variables = {
                'viewId': view_id,
                'first': min(100, max_issues - len(all_issues)),
                'after': end_cursor
            }
            
            try:
                result = self._make_request(query, variables)
                custom_view = result.get('data', {}).get('customView', {})
                issues_data = custom_view.get('issues', {})
                
                nodes = issues_data.get('nodes', [])
                all_issues.extend(nodes)
                
                page_info = issues_data.get('pageInfo', {})
                has_next_page = page_info.get('hasNextPage', False) and len(all_issues) < max_issues
                end_cursor = page_info.get('endCursor')
                
                print(f"Fetched {len(nodes)} issues (total: {len(all_issues)})")
                
                if not has_next_page:
                    break
                    
            except Exception as e:
                print(f"Error fetching issues: {e}")
                break
        
        return all_issues
    
    def get_issues_by_label(self, label_name: str, team_key: str = "ENG", max_issues: int = 1000) -> List[Dict[str, Any]]:
        """Fetch all issues with a specific label"""
        
        print(f"Fetching issues with label: {label_name}")
        
        # Fetch issues with pagination
        all_issues = []
        has_next_page = True
        end_cursor = None
        
        while has_next_page:
            query = """
            query GetIssuesByLabel($first: Int!, $after: String, $labelName: String!, $teamKey: String!) {
              issues(
                first: $first
                after: $after
                filter: {
                  labels: { name: { eq: $labelName } }
                  team: { key: { eq: $teamKey } }
                }
              ) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                    id
                    identifier
                    title
                    description
                    url
                    number
                    state {
                      id
                      name
                      type
                      color
                    }
                    priority
                    priorityLabel
                    estimate
                    dueDate
                    createdAt
                    updatedAt
                    completedAt
                    canceledAt
                    archivedAt
                    labels {
                      nodes {
                        id
                        name
                        color
                      }
                    }
                    team {
                      id
                      name
                      key
                    }
                    project {
                      id
                      name
                    }
                    cycle {
                      id
                      name
                      number
                    }
                    assignee {
                      id
                      name
                      email
                      displayName
                    }
                    creator {
                      id
                      name
                      email
                    }
                    subscribers {
                      nodes {
                        id
                        name
                        email
                        displayName
                      }
                    }
                    parent {
                      id
                      identifier
                      title
                    }
                    children {
                      nodes {
                        id
                        identifier
                        title
                      }
                    }
                  }
                }
              }
            """
            
            variables = {
                'teamKey': team_key,
                'labelName': label_name,
                'first': min(100, max_issues - len(all_issues)),
                'after': end_cursor
            }
            
            try:
                result = self._make_request(query, variables)
                issues_data = result.get('data', {}).get('issues', {})
                
                nodes = issues_data.get('nodes', [])
                all_issues.extend(nodes)
                
                page_info = issues_data.get('pageInfo', {})
                has_next_page = page_info.get('hasNextPage', False) and len(all_issues) < max_issues
                end_cursor = page_info.get('endCursor')
                
                print(f"Fetched {len(nodes)} issues (total: {len(all_issues)})")
                
                if not has_next_page:
                    break
                    
            except Exception as e:
                print(f"Error fetching issues: {e}")
                break
        
        return all_issues
    
    def export_to_json(self, issues: List[Dict[str, Any]], filename: str = None):
        """Export issues to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"linear_view_issues_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(issues, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(issues)} issues to {filename}")
        return filename
    
    def export_to_csv(self, issues: List[Dict[str, Any]], filename: str = None):
        """Export issues to CSV file"""
        if not issues:
            print("No issues to export")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"linear_view_issues_{timestamp}.csv"
        
        # Define CSV columns
        fieldnames = [
            'identifier', 'title', 'url', 'state', 'priority', 'estimate',
            'assignee', 'team', 'project', 'cycle', 'labels',
            'created_at', 'updated_at', 'due_date'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for issue in issues:
                row = {
                    'identifier': issue.get('identifier', ''),
                    'title': issue.get('title', ''),
                    'url': issue.get('url', ''),
                    'state': issue.get('state', {}).get('name', ''),
                    'priority': issue.get('priorityLabel', ''),
                    'estimate': issue.get('estimate', ''),
                    'assignee': issue.get('assignee', {}).get('displayName', '') if issue.get('assignee') else '',
                    'team': issue.get('team', {}).get('name', ''),
                    'project': issue.get('project', {}).get('name', '') if issue.get('project') else '',
                    'cycle': issue.get('cycle', {}).get('name', '') if issue.get('cycle') else '',
                    'labels': ', '.join([label.get('name', '') for label in issue.get('labels', {}).get('nodes', [])]),
                    'created_at': issue.get('createdAt', ''),
                    'updated_at': issue.get('updatedAt', ''),
                    'due_date': issue.get('dueDate', ''),
                }
                writer.writerow(row)
        
        print(f"Exported {len(issues)} issues to {filename}")
        return filename
    
    def print_summary(self, issues: List[Dict[str, Any]]):
        """Print a summary of the issues"""
        if not issues:
            print("No issues found")
            return
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: {len(issues)} issues found")
        print(f"{'='*80}\n")
        
        # Group by state
        by_state = {}
        for issue in issues:
            state = issue.get('state', {}).get('name', 'Unknown')
            by_state[state] = by_state.get(state, 0) + 1
        
        print("By State:")
        for state, count in sorted(by_state.items(), key=lambda x: x[1], reverse=True):
            print(f"  {state}: {count}")
        
        # Group by assignee
        by_assignee = {}
        for issue in issues:
            assignee = issue.get('assignee')
            name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
            by_assignee[name] = by_assignee.get(name, 0) + 1
        
        print("\nBy Assignee:")
        for assignee, count in sorted(by_assignee.items(), key=lambda x: x[1], reverse=True):
            print(f"  {assignee}: {count}")
        
        # Group by priority
        by_priority = {}
        for issue in issues:
            priority = issue.get('priorityLabel', 'No priority')
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        print("\nBy Priority:")
        priority_order = ['Urgent', 'High', 'Medium', 'Low', 'No priority']
        for priority in priority_order:
            if priority in by_priority:
                print(f"  {priority}: {by_priority[priority]}")
        
        print(f"\n{'='*80}\n")


def main():
    """Main function to fetch and export Linear issues"""
    
    # Configuration
    TEAM_KEY = os.getenv('LINEAR_TEAM_KEY', "ENG")
    
    print("🦅 Eagle's View - Release Leader Dashboard")
    print("="*80)
    print(f"Fetching issues from two sources:")
    print(f"1. Items with 'preprod-v3' label (excluding 'launched' items)")
    print(f"2. Release Blockers with 'Release Blocker' label")
    print("="*80 + "\n")
    
    try:
        # Initialize the fetcher
        fetcher = LinearViewFetcher()
        
        # Fetch preprod-v3 issues
        print("📋 Fetching preprod-v3 items...")
        preprod_issues = fetcher.get_issues_by_label("preprod-v3", TEAM_KEY)
        print(f"Found {len(preprod_issues)} preprod-v3 issues\n")
        
        # Filter out issues with "launched" label
        preprod_issues_filtered = [
            issue for issue in preprod_issues
            if not any(label['name'].lower() == 'launched' 
                      for label in issue.get('labels', {}).get('nodes', []))
        ]
        print(f"After removing 'launched' items: {len(preprod_issues_filtered)} issues\n")
        
        # Fetch release blocker issues
        print("🚨 Fetching Release Blockers...")
        blocker_issues = fetcher.get_issues_by_label("Release Blocker", TEAM_KEY)
        print(f"Found {len(blocker_issues)} release blocker issues\n")
        
        # Merge issues (remove duplicates by ID)
        issues_dict = {}
        for issue in preprod_issues_filtered + blocker_issues:
            issues_dict[issue['id']] = issue
        
        # Final filter: remove any items with "launched" label
        all_issues = [
            issue for issue in issues_dict.values()
            if not any(label['name'].lower() == 'launched' 
                      for label in issue.get('labels', {}).get('nodes', []))
        ]
        
        print(f"📊 Total unique issues: {len(all_issues)}")
        print(f"   - Preprod-v3 (not launched): {len(preprod_issues_filtered)}")
        print(f"   - Release blockers: {len(blocker_issues)}")
        print(f"   - Combined & filtered (no launched): {len(all_issues)}\n")
        
        if not all_issues:
            print("No issues found")
            return
        
        # Print summary
        fetcher.print_summary(all_issues)
        
        # Export to JSON
        json_file = fetcher.export_to_json(all_issues)
        
        # Export to CSV
        csv_file = fetcher.export_to_csv(all_issues)
        
        print("\n✅ Done!")
        print(f"   JSON: {json_file}")
        print(f"   CSV:  {csv_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
