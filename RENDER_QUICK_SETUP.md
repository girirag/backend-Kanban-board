# Render Backend Setup - Quick Reference

## 🚀 Quick Setup Steps

### 1. Go to Render Dashboard
👉 https://dashboard.render.com/

### 2. Create New Web Service
- Click **"New +"** → **"Web Service"**
- Connect GitHub repository: **backend-Kanban-board**

### 3. Configuration (Copy & Paste)

**Name**: `kanban-backend`

**Root Directory**: `backend`

**Build Command**:
```
pip install -r requirements.txt
```

**Start Command**:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables**:
- `PYTHON_VERSION` = `3.11.0`

**Auto-Deploy**: ✅ Yes

### 4. Deploy
Click **"Create Web Service"** and wait 2-5 minutes

### 5. Get Your URL
Copy the URL from the dashboard (e.g., `https://kanban-backend-xxxx.onrender.com`)

### 6. Test
Visit: `https://your-backend-url.onrender.com/docs`

---

## ⚠️ Common Issues

**Can't see repository?**
- Go to Account Settings → GitHub → Configure
- Grant access to backend-Kanban-board

**Build fails?**
- Make sure Root Directory is set to `backend`
- Check build logs for errors

**Service won't start?**
- Verify start command is correct
- Check deploy logs

---

## 📝 After Deployment

Update frontend API URL in `src/lib/api.ts`:
```typescript
const API_URL = 'https://your-backend-url.onrender.com';
```

Then push to GitHub to update Vercel deployment.
