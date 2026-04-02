# Render Environment Variables Setup

## Required Environment Variables

### 1. PYTHON_VERSION
**Key**: `PYTHON_VERSION`  
**Value**: `3.11.0`  
**Description**: Specifies the Python version to use

---

## Optional: Firebase Integration

Your backend currently works WITHOUT Firebase (uses file backup). If you want to add Firebase later, you'll need to add the Firebase service account as a secret file.

### Option A: Without Firebase (Current Setup - Recommended for Quick Start)
Just add the `PYTHON_VERSION` variable above. The backend will:
- Store tasks in memory and backup to file
- Work perfectly for testing and development
- No additional configuration needed

### Option B: With Firebase (Advanced)
If you want to use Firebase for persistent storage:

1. **Add Secret File in Render**:
   - Go to your service in Render Dashboard
   - Click "Environment" tab
   - Scroll to "Secret Files"
   - Click "Add Secret File"
   - **Filename**: `firebase-service-account.json`
   - **Contents**: Paste your entire Firebase service account JSON

2. **Get Firebase Service Account JSON**:
   - Go to Firebase Console: https://console.firebase.google.com/
   - Select your project: `firstapp-ddec4`
   - Go to Project Settings (gear icon) → Service Accounts
   - Click "Generate New Private Key"
   - Download the JSON file
   - Copy its entire contents and paste into Render's Secret File

---

## How to Add Environment Variables in Render

### During Initial Setup:
1. When creating the web service, scroll to "Environment Variables"
2. Click "Add Environment Variable"
3. Enter Key: `PYTHON_VERSION`
4. Enter Value: `3.11.0`
5. Click "Add"

### After Service is Created:
1. Go to your service dashboard
2. Click "Environment" in the left sidebar
3. Click "Add Environment Variable"
4. Enter the key and value
5. Click "Save Changes"
6. Service will automatically redeploy

---

## Complete Environment Variables List

Copy and paste these into Render:

```
Key: PYTHON_VERSION
Value: 3.11.0
```

That's it! Your backend will work with just this one variable.

---

## Verification

After deployment, test your backend:

1. Visit: `https://your-backend-url.onrender.com/health`
2. You should see:
   ```json
   {
     "status": "healthy",
     "tasks_count": 0,
     "firebase_connected": false,
     "storage": "file_backup"
   }
   ```

3. Visit: `https://your-backend-url.onrender.com/docs`
4. You should see the FastAPI documentation

---

## Notes

- **PORT**: Automatically set by Render (don't add this manually)
- **Firebase**: Optional - backend works without it using file backup
- **CORS**: Already configured to allow all origins
- **Auto-Deploy**: Enable this so updates push automatically from GitHub

---

## Troubleshooting

**Service won't start?**
- Check you added `PYTHON_VERSION=3.11.0`
- Verify Root Directory is set to `backend`
- Check deploy logs for errors

**Firebase errors?**
- Ignore them if you're not using Firebase
- Backend will automatically fall back to file storage
- You can add Firebase later if needed
