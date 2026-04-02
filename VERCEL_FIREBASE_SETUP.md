# Fix Firebase Authorization Error on Vercel

## Problem
When accessing the Vercel deployment, you see: "This domain is not authorized. Please add it in Firebase Console."

## Solution

### Step 1: Add Vercel Domain to Firebase Authorized Domains

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **firstapp-ddec4**
3. Click on **Authentication** in the left sidebar
4. Click on the **Settings** tab
5. Scroll down to **Authorized domains**
6. Click **Add domain**
7. Add the following domains one by one:

   ```
   frontend-kanban-board-lvl85w5an-giriraghav-kishores-projects.vercel.app
   ```

   And also add (for all preview deployments):
   ```
   *.vercel.app
   ```

8. Click **Add** for each domain

### Step 2: Wait for Changes to Propagate

Firebase changes usually take effect immediately, but sometimes it can take a few minutes.

### Step 3: Test the Application

1. Go to your Vercel URL: https://frontend-kanban-board-lvl85w5an-giriraghav-kishores-projects.vercel.app/
2. Click "Sign in with Google"
3. You should now be able to authenticate successfully

## Additional Notes

- If you get a new Vercel URL in the future, you'll need to add it to Firebase authorized domains
- The wildcard `*.vercel.app` covers all Vercel preview deployments
- You can also add custom domains if you set them up in Vercel

## Troubleshooting

If you still see the error after adding the domain:
1. Clear your browser cache
2. Try in an incognito/private window
3. Wait a few minutes for Firebase to propagate the changes
4. Verify the domain was added correctly in Firebase Console
