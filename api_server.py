#!/usr/bin/env python3
"""
Eagle's View - Release Leader Dashboard
API Server for Linear Integration

Handles label management and other Linear API operations
"""

import os
import json
import subprocess
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from dotenv import load_dotenv
import mimetypes

load_dotenv()

LINEAR_API_KEY = os.getenv('LINEAR_API_KEY')
LINEAR_API_URL = "https://api.linear.app/graphql"

class LinearAPIHandler(BaseHTTPRequestHandler):
    
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_POST(self):
        if self.path == '/api/add-label':
            self.handle_add_label()
        elif self.path == '/api/remove-label':
            self.handle_remove_label()
        elif self.path == '/api/available-labels':
            self.handle_get_available_labels()
        elif self.path == '/api/refresh-data':
            self.handle_refresh_data()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())
    
    def do_GET(self):
        if self.path.startswith('/api/issue-labels'):
            self.handle_get_issue_labels()
        elif self.path == '/api/latest-json':
            self.handle_get_latest_json()
        else:
            # Serve static files
            self.serve_static_file()
    
    def handle_add_label(self):
        """Add a label to an issue"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            issue_id = data.get('issueId')
            label_id = data.get('labelId')
            
            if not issue_id or not label_id:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing issueId or labelId'}).encode())
                return
            
            # GraphQL mutation to add label
            mutation = """
            mutation AddLabelToIssue($issueId: String!, $labelId: String!) {
              issueAddLabel(id: $issueId, labelId: $labelId) {
                success
                issue {
                  id
                  labels {
                    nodes {
                      id
                      name
                      color
                    }
                  }
                }
              }
            }
            """
            
            variables = {
                'issueId': issue_id,
                'labelId': label_id
            }
            
            response = requests.post(
                LINEAR_API_URL,
                headers={
                    'Authorization': LINEAR_API_KEY,
                    'Content-Type': 'application/json'
                },
                json={
                    'query': mutation,
                    'variables': variables
                }
            )
            
            result = response.json()
            
            if 'errors' in result:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': result['errors']}).encode())
                return
            
            self._set_headers(200)
            self.wfile.write(json.dumps(result['data']).encode())
            
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def handle_remove_label(self):
        """Remove a label from an issue"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            issue_id = data.get('issueId')
            label_id = data.get('labelId')
            
            if not issue_id or not label_id:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing issueId or labelId'}).encode())
                return
            
            # GraphQL mutation to remove label
            mutation = """
            mutation RemoveLabelFromIssue($issueId: String!, $labelId: String!) {
              issueRemoveLabel(id: $issueId, labelId: $labelId) {
                success
                issue {
                  id
                  labels {
                    nodes {
                      id
                      name
                      color
                    }
                  }
                }
              }
            }
            """
            
            variables = {
                'issueId': issue_id,
                'labelId': label_id
            }
            
            response = requests.post(
                LINEAR_API_URL,
                headers={
                    'Authorization': LINEAR_API_KEY,
                    'Content-Type': 'application/json'
                },
                json={
                    'query': mutation,
                    'variables': variables
                }
            )
            
            result = response.json()
            
            if 'errors' in result:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': result['errors']}).encode())
                return
            
            self._set_headers(200)
            self.wfile.write(json.dumps(result['data']).encode())
            
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def handle_get_available_labels(self):
        """Get all available labels from the team"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            team_id = data.get('teamId')
            
            query = """
            query GetTeamLabels($teamId: String!) {
              team(id: $teamId) {
                labels {
                  nodes {
                    id
                    name
                    color
                  }
                }
              }
            }
            """
            
            variables = {'teamId': team_id} if team_id else {}
            
            # If no team_id, get all labels from viewer
            if not team_id:
                query = """
                query GetAllLabels {
                  viewer {
                    organization {
                      labels {
                        nodes {
                          id
                          name
                          color
                        }
                      }
                    }
                  }
                }
                """
                variables = {}
            
            response = requests.post(
                LINEAR_API_URL,
                headers={
                    'Authorization': LINEAR_API_KEY,
                    'Content-Type': 'application/json'
                },
                json={
                    'query': query,
                    'variables': variables
                }
            )
            
            result = response.json()
            
            if 'errors' in result:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': result['errors']}).encode())
                return
            
            self._set_headers(200)
            self.wfile.write(json.dumps(result['data']).encode())
            
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def handle_get_issue_labels(self):
        """Get current labels for an issue"""
        try:
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            issue_id = params.get('issueId', [None])[0]
            
            if not issue_id:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing issueId'}).encode())
                return
            
            query = """
            query GetIssueLabels($issueId: String!) {
              issue(id: $issueId) {
                id
                labels {
                  nodes {
                    id
                    name
                    color
                  }
                }
              }
            }
            """
            
            variables = {'issueId': issue_id}
            
            response = requests.post(
                LINEAR_API_URL,
                headers={
                    'Authorization': LINEAR_API_KEY,
                    'Content-Type': 'application/json'
                },
                json={
                    'query': query,
                    'variables': variables
                }
            )
            
            result = response.json()
            
            if 'errors' in result:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': result['errors']}).encode())
                return
            
            self._set_headers(200)
            self.wfile.write(json.dumps(result['data']).encode())
            
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def handle_get_latest_json(self):
        """Get the filename of the most recent JSON data file"""
        try:
            import glob
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Find all JSON files matching the pattern
            json_files = glob.glob(os.path.join(script_dir, 'linear_view_issues_*.json'))
            
            if not json_files:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'No data files found'}).encode())
                return
            
            # Sort by modification time, most recent first
            json_files.sort(key=os.path.getmtime, reverse=True)
            latest_file = os.path.basename(json_files[0])
            
            self._set_headers(200)
            self.wfile.write(json.dumps({'filename': latest_file}).encode())
            
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    def handle_refresh_data(self):
        """Run the fetch script to get fresh data from Linear"""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(script_dir, 'fetch_v3_verify_items.py')
            
            # Run the fetch script
            print(f"[API] Running fetch script: {script_path}")
            
            # Use the same Python interpreter that's running this script
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=script_dir,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode == 0:
                print(f"[API] Fetch script completed successfully")
                self._set_headers(200)
                response = {
                    'success': True,
                    'message': 'Data refreshed successfully',
                    'output': result.stdout
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                print(f"[API] Fetch script failed with return code {result.returncode}")
                print(f"[API] Error output: {result.stderr}")
                self._set_headers(500)
                response = {
                    'success': False,
                    'error': f'Script failed: {result.stderr}',
                    'output': result.stdout
                }
                self.wfile.write(json.dumps(response).encode())
                
        except subprocess.TimeoutExpired:
            print(f"[API] Fetch script timed out")
            self._set_headers(500)
            response = {
                'success': False,
                'error': 'Script execution timed out (60s)'
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"[API] Error running fetch script: {str(e)}")
            self._set_headers(500)
            response = {
                'success': False,
                'error': str(e)
            }
            self.wfile.write(json.dumps(response).encode())
    
    def serve_static_file(self):
        """Serve static files (HTML, JSON, CSS, etc.)"""
        try:
            # Get the file path
            if self.path == '/':
                file_path = 'viewer.html'
            else:
                # Remove leading slash and query parameters
                file_path = self.path.lstrip('/').split('?')[0]
            
            # Get the full path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(script_dir, file_path)
            
            # Security check - ensure the file is within the script directory
            if not full_path.startswith(script_dir):
                self._set_headers(403, 'text/plain')
                self.wfile.write(b'Forbidden')
                return
            
            # Check if file exists
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                self._set_headers(404, 'text/html')
                self.wfile.write(b'<h1>404 Not Found</h1>')
                return
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(full_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # Read and serve the file
            with open(full_path, 'rb') as f:
                content = f.read()
            
            self._set_headers(200, content_type)
            self.wfile.write(content)
            
        except Exception as e:
            print(f"[ERROR] Failed to serve static file: {str(e)}")
            self._set_headers(500, 'text/plain')
            self.wfile.write(f'Internal Server Error: {str(e)}'.encode())
    
    def log_message(self, format, *args):
        # Custom log format
        print(f"[API] {self.address_string()} - {format % args}")


def run_server(port=None):
    # Use PORT from environment (for Render) or default to 8001 for local
    if port is None:
        port = int(os.getenv('PORT', 8001))
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, LinearAPIHandler)
    print(f"🦅 Eagle's View - Release Leader Dashboard")
    print(f"Server running on http://localhost:{port}")
    print("\nAvailable endpoints:")
    print("  GET  /                              - Web Dashboard")
    print("  POST /api/add-label                 - Add label to issue")
    print("  POST /api/remove-label              - Remove label from issue")
    print("  POST /api/available-labels          - Get available labels")
    print("  POST /api/refresh-data              - Refresh data from Linear")
    print("  GET  /api/latest-json               - Get latest data filename")
    print("  GET  /api/issue-labels?issueId=<id> - Get issue labels")
    print("\nPress Ctrl+C to stop the server\n")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
