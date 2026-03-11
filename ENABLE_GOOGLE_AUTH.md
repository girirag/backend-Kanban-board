# Enable Google Authentication in Firebase

## Steps to Enable Google Sign-In:

1. Go to [Firebase Console](https://console.firebase.google.com/)

2. Select your project: **firstapp-ddec4**

3. In the left sidebar, click on **Authentication**

4. Click on the **Sign-in method** tab

5. Click on **Google** in the list of providers

6. Toggle the **Enable** switch to ON

7. Enter a **Project support email** (your email)

8. Click **Save**

9. (Optional) Add authorized domains:
   - Go to **Settings** tab in Authentication
   - Under **Authorized domains**, add:
     - `localhost` (already there)
     - Your Vercel domain when you deploy

## After Enabling:

Refresh your app at http://localhost:5173/ and try signing in again!

## Troubleshooting:

If you still have issues:
- Make sure you're using the correct Firebase project
- Check that the API key in `src/lib/firebase.ts` matches your project
- Clear browser cache and try again
