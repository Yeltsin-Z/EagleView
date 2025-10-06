# 🦅 Eagle's View

**Release Leader Dashboard for Linear Issues**

A powerful web-based dashboard for release leaders to track, manage, and verify Linear issues throughout the release cycle.

## Features

### 📊 **Real-time Dashboard**
- Live statistics: Total issues, Urgent count, High priority count, Issues in QA
- Beautiful, modern UI with gradient design
- Responsive layout that works on desktop and mobile

### 🔍 **Advanced Filtering & Sorting**
- **Search**: Filter by issue title or identifier
- **State**: Filter by issue state (In QA Verification, In Dev Verification, etc.)
- **Priority**: Filter by priority level (Urgent, High, Medium, Low)
- **Assignee**: Filter by assigned team member
- **Verifier**: Filter by verification assignee
- **Sortable Columns**: Click any column header to sort

### 🏷️ **Label Management**
- Add labels to issues directly from the dashboard
- Remove labels with a single click
- Real-time sync with Linear
- Visual color-coded labels matching Linear's theme

### 🎨 **Beautiful UI/UX**
- Color-coded priority badges (red for urgent, orange for high, etc.)
- Clean, professional interface
- Smooth animations and transitions
- Direct links to Linear issues

## Architecture

### Frontend (`viewer.html`)
- Single-page application
- No build step required
- Vanilla JavaScript for maximum performance
- Real-time API communication

### Backend (`api_server.py`)
- Python-based API server
- Secure Linear API integration
- CORS-enabled for local development
- RESTful endpoints for label management

### Data Fetcher (`fetch_v3_verify_items.py`)
- Fetches issues from Linear custom views
- Exports to JSON and CSV formats
- Includes comprehensive issue metadata
- Configurable via environment variables

## Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file with:

```
LINEAR_API_KEY=your_linear_api_key_here
LINEAR_VIEW_ID=your_view_id_here
```

### 3. Fetch Issues

```bash
python fetch_v3_verify_items.py
```

### 4. Start Server

```bash
source venv/bin/activate
python api_server.py
```

The server handles both static files and API endpoints on port 8001.

### 5. Open Dashboard

Navigate to: http://localhost:8001

## Deployment on Render

### Quick Deploy

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create New Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

3. **Configure Environment Variables**
   - In Render dashboard, go to your service's "Environment" tab
   - Add the following variables:
     - `LINEAR_API_KEY`: Your Linear API key
     - `LINEAR_USER_ID`: Your Linear user ID
     - `LINEAR_VIEW_ID`: Your Linear custom view ID

4. **Deploy**
   - Render will automatically deploy your application
   - Your dashboard will be available at: `https://your-app-name.onrender.com`

### Manual Deploy Configuration

If you prefer manual configuration instead of using `render.yaml`:

1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `python api_server.py`
3. **Environment**: Python 3
4. **Plan**: Free (or choose your preferred plan)

### Automatic Deployments

- Render automatically deploys when you push to your main branch
- You can also manually trigger deployments from the Render dashboard

### First Time Data Load

After deployment:
1. Visit your deployed URL
2. Click the **"Refresh"** button to fetch initial data from Linear
3. The dashboard will populate with your Linear issues

## API Endpoints

- `GET /` - Web Dashboard (serves viewer.html)
- `POST /api/add-label` - Add a label to an issue
- `POST /api/remove-label` - Remove a label from an issue
- `POST /api/available-labels` - Get all available labels
- `POST /api/refresh-data` - Trigger data refresh from Linear
- `GET /api/latest-json` - Get the filename of the most recent data file
- `GET /api/issue-labels?issueId=<id>` - Get current labels for an issue

## Usage

### Viewing Issues
- All issues are displayed in an interactive table
- Click column headers to sort
- Use filters at the top to narrow down results

### Managing Labels
- Click the **"+ Add"** button in any row to add labels
- Click the **"×"** next to any label to remove it
- Changes sync instantly with Linear

### Filtering by Verifier
- Use the Verifier dropdown to see all issues assigned to a specific verifier
- Verifiers are pulled from issue subscribers in Linear

## Data Export

Issues are automatically exported to:
- **JSON**: Full issue data with all metadata
- **CSV**: Simplified view for spreadsheet analysis

## Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python 3, http.server
- **API**: Linear GraphQL API
- **Dependencies**: requests, python-dotenv

## Project Structure

```
Easy Linear/
├── viewer.html              # Main dashboard UI
├── api_server.py           # API server for Linear integration
├── fetch_v3_verify_items.py # Data fetching script
├── requirements.txt         # Python dependencies
├── .env                    # Configuration (not in repo)
├── venv/                   # Python virtual environment
└── linear_view_issues_*.json # Exported data
```

## License

Internal tool for Drivetrain.ai

## Support

For issues or feature requests, contact the engineering team.

---

**Built with ❤️ for Release Leaders**
