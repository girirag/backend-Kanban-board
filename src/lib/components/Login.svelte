<script lang="ts">
  import { signInWithGoogle } from '../auth';

  let loading = false;
  let error = '';
  let showPopupHelp = false;

  async function handleGoogleSignIn() {
    loading = true;
    error = '';
    showPopupHelp = false;
    
    try {
      console.log('Starting Google Sign-In...');
      await signInWithGoogle();
      console.log('Sign-in successful');
    } catch (err: any) {
      console.error('Sign in error:', err);
      loading = false;
      
      if (err.code === 'auth/popup-blocked') {
        showPopupHelp = true;
        error = 'Popup was blocked by your browser. Please allow popups for this site and try again.';
      } else if (err.code === 'auth/popup-closed-by-user') {
        error = 'Sign-in popup was closed. Please try again.';
      } else if (err.code === 'auth/unauthorized-domain') {
        error = 'This domain is not authorized. Please add it in Firebase Console.';
      } else if (err.code === 'auth/operation-not-allowed') {
        error = 'Google Sign-In is not enabled. Please enable it in Firebase Console (Authentication > Sign-in method > Google).';
      } else if (err.code === 'auth/cancelled-popup-request') {
        error = 'Another sign-in attempt is in progress. Please wait.';
      } else {
        error = `Failed to sign in: ${err.message || 'Please try again.'}`;
      }
    }
  }
</script>

<style>
  .login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 15%, #b91c1c 30%, #dc2626 50%, #b91c1c 70%, #991b1b 85%, #7f1d1d 100%);
    padding: 2rem;
  }

  .login-card {
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 3rem;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
    max-width: 450px;
    width: 100%;
    text-align: center;
  }

  .login-icon {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    margin: 0 auto 1.5rem;
    box-shadow: 0 8px 24px rgba(220, 38, 38, 0.4);
  }

  .login-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7f1d1d 0%, #dc2626 50%, #ef4444 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
  }

  .login-subtitle {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 2rem;
  }

  .google-btn {
    width: 100%;
    padding: 1rem 2rem;
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
  }

  .google-btn:hover {
    border-color: #dc2626;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
    transform: translateY(-2px);
  }

  .google-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .google-icon {
    width: 24px;
    height: 24px;
  }

  .error {
    color: #dc2626;
    font-size: 0.875rem;
    margin-top: 1rem;
    padding: 0.75rem;
    background: #fee2e2;
    border-radius: 8px;
  }

  .popup-help {
    margin-top: 1rem;
    padding: 1rem;
    background: #fef3c7;
    border-radius: 8px;
    text-align: left;
    font-size: 0.875rem;
    color: #92400e;
  }

  .popup-help strong {
    display: block;
    margin-bottom: 0.5rem;
    color: #78350f;
  }

  .popup-help ul {
    margin: 0;
    padding-left: 1.25rem;
  }

  .popup-help li {
    margin-bottom: 0.25rem;
  }

  @media (max-width: 480px) {
    .login-card {
      padding: 2rem 1.25rem;
      border-radius: 16px;
    }

    .login-title {
      font-size: 1.5rem;
    }

    .login-icon {
      width: 64px;
      height: 64px;
      font-size: 2.2rem;
    }
  }
</style>

<div class="login-container">
  <div class="login-card">
    <div class="login-icon">📋</div>
    <h1 class="login-title">Project Board</h1>
    <p class="login-subtitle">Sign in to access your personal Kanban board</p>
    
    <button 
      class="google-btn" 
      on:click={handleGoogleSignIn}
      disabled={loading}
    >
      <svg class="google-icon" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
      </svg>
      {loading ? 'Signing in...' : 'Sign in with Google'}
    </button>

    {#if error}
      <div class="error">{error}</div>
    {/if}
    
    {#if showPopupHelp}
      <div class="popup-help">
        <p><strong>How to allow popups:</strong></p>
        <ul>
          <li>Look for a popup blocked icon in your browser's address bar</li>
          <li>Click it and select "Always allow popups from this site"</li>
          <li>Then click "Sign in with Google" again</li>
        </ul>
      </div>
    {/if}
  </div>
</div>
