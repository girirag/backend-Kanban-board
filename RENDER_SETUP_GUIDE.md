# Deploy Backend to Render - Complete Guide

## Prerequisites
- GitHub account with backend repository: https://github.com/girirag/backend-Kanban-board
- Render account (sign up at https://render.com if you don't have one)

## Step 1: Sign in to Render
1. Go to https://dashboard.render.com/
2. Sign in with your GitHub account (recommended) or email

## Step 2: Create New Web Service
1. Click the **"New +"** button in the top right
2. Select **"Web Service"**

## Step 3: Connect Repository
1. If this is your first time, click **"Connect GitHub"** and authorize Render
2. In the repository list, find and select: **backend-Kanban-board**
   - If you don't see it, click "Configure account" and grant access to the repository
3. Click **"Connect"**

## Step 4: Configure Service Settings

Fill in the following details:

### Basic Settings
- **Name**: `kanban-backend` (or any name you prefer)
- **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch**: `main`
- **Root Directory**: `backend` (IMPORTANT: This tells Render where the backend code is)
- **Runtime**: `Python 3`

### Build & Deploy Settings
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```

- **Start Command**: 
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

### Instance Type
- Select **"Free"** (for testing) or **"Starter"** (for production)

### Environment Variables
Click **"Add Environment Variable"** and add:

1. **PYTHON_VERSION**
   - Value: `3.11.0`

2. **FIREBASE_CREDENTIALS** (if using Firebase)
   - Value: Copy the entire content from `backend/firebase-service-account.json`
   - Or set this up later in the service settings

### Auto-Deploy
- **Auto-Deploy**: Set to **"Yes"** (this will auto-deploy when you push to GitHub)

## Step 5: Deploy
1. Click **"Create Web Service"** at the bottom
2. Render will start building and deploying your backend
3. Wait for the deployment to complete (usually 2-5 minutes)

## Step 6: Get Your Backend URL
1. Once deployed, you'll see your service URL at the top (e.g., `https://kanban-backend-xxxx.onrender.com`)
2. Copy this URL - you'll need it for the frontend

## Step 7: Test Your Backend
1. Open your backend URL in a browser
2. Add `/docs` to the end (e.g., `https://kanban-backend-xxxx.onrender.com/docs`)
3. You should see the FastAPI documentation page

## Step 8: Update Frontend with Backend URL
1. Go to your frontend code
2. Update the API URL in `src/lib/api.ts`:
   ```typescript
   const API_URL = 'https://your-backend-url.onrender.com';
   ```
3. Commit and push to trigger Vercel deployment

## Troubleshooting

### Build Fails
- Check the build logs in Render dashboard
- Verify `requirements.txt` exists in the backend folder
- Ensure Python version is correct

### Service Won't Start
- Check the deploy logs
- Verify the start command is correct
- Make sure `main.py` exists and has the FastAPI app

### Can't See Repository
- Go to Render Account Settings → GitHub
- Click "Configure" and grant access to the repository

### 404 Errors
- Verify the Root Directory is set to `backend`
- Check that all files are in the correct location

## Important Notes
- Free tier services sleep after 15 minutes of inactivity
- First request after sleep will be slow (cold start)
- For production, consider upgrading to a paid plan
- Keep your Firebase credentials secure (use environment variables)

## Current Repository Structure
```
backend-Kanban-board/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── firebase-service-account.json
│   └── render.yaml
```

Make sure Render is pointing to the `backend` folder as the root directory!
