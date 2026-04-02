# Vercel Firebase Domain Authorization Bugfix Design

## Overview

The Kanban board application now builds and deploys successfully on Vercel, but Firebase Authentication fails at runtime with "This domain is not authorized" error when users attempt to sign in with Google. The root cause is that Firebase requires all domains using Firebase Authentication to be explicitly authorized in the Firebase Console. The Vercel deployment URL and wildcard domain for preview deployments need to be added to Firebase's authorized domains list.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when users attempt Firebase Authentication from an unauthorized domain (Vercel deployment URL)
- **Property (P)**: The desired behavior - Firebase Authentication should succeed from the Vercel deployment domain
- **Preservation**: Existing authentication behavior on localhost and other authorized domains must remain unchanged
- **Authorized Domains**: The list of domains in Firebase Console that are permitted to use Firebase Authentication
- **Vercel Deployment Domain**: The production URL assigned by Vercel for the deployed application
- **Vercel Preview Domains**: Temporary URLs created by Vercel for pull request previews (*.vercel.app)

## Bug Details

### Bug Condition

The bug manifests when a user attempts to authenticate using Firebase Authentication (Google Sign-In) from the Vercel deployment URL. Firebase's security rules block authentication requests from domains that are not explicitly listed in the authorized domains configuration.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type AuthenticationRequest
  OUTPUT: boolean
  
  RETURN input.originDomain == "frontend-kanban-board-lvl85w5an-giriraghav-kishores-projects.vercel.app"
         AND input.originDomain NOT IN Firebase.authorizedDomains
         AND input.authMethod == "GoogleSignIn"
END FUNCTION
```

### Examples

- User visits `https://frontend-kanban-board-lvl85w5an-giriraghav-kishores-projects.vercel.app/` and clicks "Sign in with Google" → Error: "This domain is not authorized"
- User visits a Vercel preview deployment URL (e.g., `https://frontend-kanban-board-abc123.vercel.app/`) and attempts authentication → Error: "This domain is not authorized"
- User visits `http://localhost:5173` and clicks "Sign in with Google" → Works correctly (localhost is already authorized)
- User visits an already authorized domain and authenticates → Works correctly (no change in behavior)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Authentication from localhost (development environment) must continue to work exactly as before
- Authentication from any previously authorized domains must continue to work without modification
- The Firebase Authentication flow, UI, and user experience must remain identical
- Backend API authentication and authorization logic must remain unchanged

**Scope:**
All authentication requests from domains that are ALREADY in the Firebase authorized domains list should be completely unaffected by this fix. This includes:
- Local development on localhost
- Any custom domains previously configured
- Firebase's default authorized domains (firebaseapp.com, etc.)

## Hypothesized Root Cause

Based on the error message and Firebase Authentication behavior, the root cause is:

1. **Missing Domain Configuration**: The Vercel deployment domain is not present in Firebase Console's authorized domains list
   - Firebase enforces a security policy requiring explicit domain authorization
   - New deployment domains are not automatically added to the authorized list
   - The error occurs at the Firebase SDK level before any authentication attempt

2. **Wildcard Domain Not Configured**: Vercel preview deployments use dynamic subdomains (*.vercel.app)
   - Each pull request creates a unique preview URL
   - Without wildcard authorization, each preview URL would need individual authorization
   - Firebase supports wildcard domains to handle this scenario

3. **Configuration-Only Issue**: This is not a code bug but a configuration gap
   - The application code is correct and functional
   - The Firebase project configuration is incomplete for production deployment
   - No code changes are required, only Firebase Console configuration updates

## Correctness Properties

Property 1: Bug Condition - Firebase Authentication from Vercel Domain

_For any_ authentication request originating from the Vercel deployment domain (frontend-kanban-board-lvl85w5an-giriraghav-kishores-projects.vercel.app) or any Vercel preview domain (*.vercel.app), the Firebase Authentication SHALL complete successfully, allowing users to sign in with Google and access the application.

**Validates: Requirements 2.1, 2.2, 2.3**

Property 2: Preservation - Existing Domain Authentication

_For any_ authentication request originating from a domain that was ALREADY authorized before this fix (localhost, firebaseapp.com, etc.), the Firebase Authentication SHALL produce exactly the same behavior as before, preserving all existing authentication functionality without any changes to the user experience or authentication flow.

**Validates: Requirements 3.2, 3.3, 3.4**

## Fix Implementation

### Changes Required

This fix requires configuration changes in Firebase Console, not code changes.

**Location**: Firebase Console → Authentication → Settings → Authorized domains

**Specific Changes**:
1. **Add Production Domain**: Add the specific Vercel deployment URL
   - Domain: `frontend-kanban-board-lvl85w5an-giriraghav-kishores-projects.vercel.app`
   - This authorizes the current production deployment

2. **Add Wildcard Domain**: Add wildcard pattern for all Vercel deployments
   - Domain: `*.vercel.app`
   - This authorizes all preview deployments and future production URLs
   - Enables testing on pull request preview deployments

3. **Verify Existing Domains**: Confirm localhost and other domains remain in the list
   - Ensure `localhost` is present for local development
   - Ensure Firebase default domains remain unchanged

4. **No Code Changes Required**: The application code does not need modification
   - Firebase SDK automatically respects the authorized domains configuration
   - No deployment or rebuild is necessary after configuration update

5. **Immediate Effect**: Changes take effect immediately after saving
   - No cache clearing or waiting period required
   - Users can authenticate immediately after configuration update

### Configuration Steps

1. Navigate to Firebase Console (https://console.firebase.google.com/)
2. Select the Kanban board project
3. Go to Authentication → Settings → Authorized domains
4. Click "Add domain"
5. Add: `frontend-kanban-board-lvl85w5an-giriraghav-kishores-projects.vercel.app`
6. Click "Add domain" again
7. Add: `*.vercel.app`
8. Save changes
9. Test authentication on Vercel deployment

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, confirm the bug exists on the current configuration, then verify the fix works correctly after adding the domains and confirm existing authentication remains unchanged.

### Exploratory Bug Condition Checking

**Goal**: Confirm the bug exists BEFORE making configuration changes. Verify that the error message matches expectations and understand the exact failure point.

**Test Plan**: Attempt to authenticate from the Vercel deployment URL before adding it to authorized domains. Document the exact error message and behavior.

**Test Cases**:
1. **Production Domain Authentication**: Visit Vercel URL and attempt Google Sign-In (will fail with "domain not authorized" error)
2. **Preview Domain Authentication**: Visit a preview deployment URL and attempt authentication (will fail with same error)
3. **Localhost Authentication**: Verify localhost authentication still works (should succeed, confirming the issue is domain-specific)
4. **Error Message Verification**: Confirm the error message explicitly mentions domain authorization (confirms root cause)

**Expected Counterexamples**:
- Authentication fails with "This domain is not authorized. Please add it in Firebase Console."
- Firebase SDK blocks the authentication attempt before reaching Google's OAuth flow
- Browser console shows Firebase Authentication error related to domain authorization

### Fix Checking

**Goal**: Verify that after adding the domains to Firebase Console, authentication succeeds from the Vercel deployment URL and all preview URLs.

**Pseudocode:**
```
FOR ALL authRequest WHERE isBugCondition(authRequest) DO
  result := attemptFirebaseAuth(authRequest)
  ASSERT result.success == true
  ASSERT result.user != null
  ASSERT result.error == null
END FOR
```

**Test Cases**:
1. **Production Domain Success**: After configuration, authenticate from production Vercel URL → Should succeed
2. **Preview Domain Success**: Authenticate from a preview deployment URL → Should succeed
3. **Multiple Preview URLs**: Test authentication on 2-3 different preview URLs → All should succeed
4. **Full Authentication Flow**: Complete the entire sign-in flow including redirect back to application → Should work end-to-end

### Preservation Checking

**Goal**: Verify that authentication from previously authorized domains continues to work exactly as before, with no changes to behavior or user experience.

**Pseudocode:**
```
FOR ALL authRequest WHERE NOT isBugCondition(authRequest) DO
  ASSERT attemptFirebaseAuth_beforeFix(authRequest) == attemptFirebaseAuth_afterFix(authRequest)
END FOR
```

**Testing Approach**: Since this is a configuration change that only adds new authorized domains without modifying existing ones, preservation is inherently guaranteed by Firebase's additive authorization model. However, explicit testing confirms no unintended side effects.

**Test Plan**: Test authentication on localhost and any other previously working domains after making the Firebase Console changes.

**Test Cases**:
1. **Localhost Preservation**: Authenticate from localhost after configuration change → Should work identically to before
2. **Authentication Flow Preservation**: Verify the sign-in UI, redirect flow, and user session creation remain unchanged
3. **Token Generation Preservation**: Verify Firebase ID tokens are generated correctly and backend API calls work
4. **Sign-Out Preservation**: Verify sign-out functionality continues to work correctly

### Unit Tests

- No unit tests required (configuration change only, not code change)
- Existing authentication unit tests should continue to pass without modification

### Property-Based Tests

- Not applicable for this fix (configuration change, not algorithmic code change)
- Existing property-based tests for authentication logic should remain unchanged

### Integration Tests

- Test full authentication flow from Vercel production URL after domain authorization
- Test authentication from multiple Vercel preview URLs to verify wildcard domain works
- Test that localhost authentication continues to work after configuration change
- Test that authenticated users can access protected routes and make API calls
- Test sign-out flow works correctly from Vercel deployment
- Verify Firebase ID tokens are valid and accepted by backend services
