# 🚀 Deployment Guide for Eagle's View

## Prerequisites

- GitHub account
- Render account (free tier available at [render.com](https://render.com))
- Linear API key and credentials

## Step-by-Step Deployment to Render

### 1. Prepare Your Repository

If you haven't already created a Git repository:

```bash
cd "/Users/yeltsinz/PycharmProjects/Easy Linear"
git init
git add .
git commit -m "Initial commit - Eagle's View Dashboard"
```

### 2. Push to GitHub

Create a new repository on GitHub, then:

```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git branch -M main
git push -u origin main
```

### 3. Deploy on Render

#### Option A: One-Click Deploy with render.yaml

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect GitHub"** and authorize Render
4. Select your repository
5. Render will automatically detect the `render.yaml` file
6. Click **"Apply"** to use the configuration

#### Option B: Manual Configuration

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the following:
   - **Name**: `eagles-view-dashboard` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api_server.py`
   - **Plan**: Free (or your preferred plan)

### 4. Configure Environment Variables

In the Render dashboard, navigate to your service's **"Environment"** tab and add:

| Key | Value | Description |
|-----|-------|-------------|
| `LINEAR_API_KEY` | `lin_api_...` | Your Linear API key |
| `LINEAR_USER_ID` | `0f313a70-...` | Your Linear user ID |
| `LINEAR_VIEW_ID` | `153db179a33a` | Your Linear custom view ID |

**Important**: Keep these values secret! Never commit them to your repository.

### 5. Deploy!

- Render will automatically build and deploy your application
- Deployment typically takes 2-3 minutes
- Your app will be available at: `https://eagles-view-dashboard.onrender.com`
  (or your custom domain)

### 6. Initialize Data

Once deployed:
1. Visit your deployed URL
2. Click the **"🔄 Refresh"** button in the top right
3. Wait for the data to load from Linear
4. Your dashboard is now live!

## Automatic Updates

Render automatically deploys when you push to your `main` branch:

```bash
# Make changes to your code
git add .
git commit -m "Update dashboard features"
git push

# Render will automatically deploy the changes
```

## Monitoring

- View logs: Render Dashboard → Your Service → "Logs" tab
- Check status: Render Dashboard → Your Service → "Events" tab
- Monitor usage: Render Dashboard → Your Service → "Metrics" tab

## Free Tier Limitations

On Render's free tier:
- Service spins down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- 750 hours/month of free usage
- Upgrade to paid plans for always-on service

## Troubleshooting

### Service Won't Start

Check the logs for errors:
```
Render Dashboard → Your Service → Logs
```

Common issues:
- Missing environment variables
- Python version mismatch
- Dependency installation failures

### API Errors

Verify your environment variables are set correctly:
```
Render Dashboard → Your Service → Environment
```

### Data Not Loading

1. Check if Linear API key is valid
2. Verify the VIEW_ID is correct
3. Use the Refresh button to reload data

## Custom Domain (Optional)

To use a custom domain:
1. Go to your service settings on Render
2. Navigate to "Custom Domains"
3. Add your domain and follow DNS configuration instructions

## Support

For issues:
- Check Render documentation: [docs.render.com](https://docs.render.com)
- Review application logs in Render dashboard
- Contact your engineering team

---

**Happy Deploying! 🚀**
