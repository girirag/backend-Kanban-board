<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { apiService, type Collaborator } from '../api';
  import { db } from '../firebase';
  import { collection, query, where, getDocs, addDoc, deleteDoc, doc } from 'firebase/firestore';

  export let ownerUserId: string;
  export let currentUserEmail: string;
  export let open: boolean = false;

  const dispatch = createEventDispatcher<{ close: void }>();

  let collaborators: Collaborator[] = [];
  let emailInput: string = '';
  let errorMsg: string = '';
  let loading: boolean = false;
  let adding: boolean = false;

  async function fetchCollaborators() {
    loading = true;
    errorMsg = '';
    try {
      // Try API first, fall back to Firestore directly
      try {
        collaborators = await apiService.getCollaborators(ownerUserId);
      } catch {
        // Fallback: query Firestore directly
        const q = query(collection(db, 'collaborations'), where('ownerUserId', '==', ownerUserId));
        const snapshot = await getDocs(q);
        collaborators = snapshot.docs.map(d => ({
          id: d.id,
          collaboratorUid: d.data().collaboratorUid ?? '',
          collaboratorEmail: d.data().collaboratorEmail ?? '',
          pending: d.data().pending ?? false,
        }));
      }
    } catch (err) {
      console.error('Failed to load collaborators:', err);
      errorMsg = 'Failed to load collaborators.';
    } finally {
      loading = false;
    }
  }

  $: if (open) {
    emailInput = '';
    errorMsg = '';
    fetchCollaborators();
  }

  function handleClose() {
    dispatch('close');
  }

  function handleBackdropClick() {
    handleClose();
  }

  function handlePanelClick(e: MouseEvent) {
    e.stopPropagation();
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && open) handleClose();
  }

  async function handleAdd() {
    const email = emailInput.trim();
    if (!email) return;
    if (email.toLowerCase() === currentUserEmail.toLowerCase()) {
      errorMsg = 'You cannot invite yourself.';
      return;
    }
    adding = true;
    errorMsg = '';
    try {
      let newCollab: Collaborator;
      try {
        newCollab = await apiService.addCollaborator({ ownerUserId, collaboratorEmail: email });
      } catch (err) {
        if (err instanceof Error && err.message.includes('409')) {
          errorMsg = 'That user is already a collaborator.';
          adding = false;
          return;
        }
        // Fallback: write directly to Firestore
        const existingSnap = await getDocs(query(
          collection(db, 'collaborations'),
          where('ownerUserId', '==', ownerUserId),
          where('collaboratorEmail', '==', email)
        ));
        if (!existingSnap.empty) {
          errorMsg = 'That user is already a collaborator.';
          adding = false;
          return;
        }
        const docRef = await addDoc(collection(db, 'collaborations'), {
          ownerUserId,
          collaboratorUid: '',
          collaboratorEmail: email,
          createdAt: new Date().toISOString(),
          pending: true,
        });
        newCollab = { id: docRef.id, collaboratorUid: '', collaboratorEmail: email, pending: true };
      }
      collaborators = [...collaborators, newCollab];
      emailInput = '';
    } catch {
      errorMsg = 'Failed to add collaborator. Please try again.';
    } finally {
      adding = false;
    }
  }

  function handleEmailKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAdd();
    }
  }

  async function handleRemove(invite: Collaborator) {
    try {
      try {
        await apiService.removeCollaborator(invite.id);
      } catch {
        await deleteDoc(doc(db, 'collaborations', invite.id));
      }
      collaborators = collaborators.filter(c => c.id !== invite.id);
    } catch {
      errorMsg = 'Failed to remove collaborator. Please try again.';
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="backdrop" on:click={handleBackdropClick}>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="panel" on:click={handlePanelClick} role="dialog" aria-modal="true" aria-label="Manage collaborators" tabindex="-1">

      <div class="panel-header">
        <div class="header-title-row">
          <span class="header-icon">👥</span>
          <h2 class="header-title">Collaborators</h2>
        </div>
        <button class="close-btn" on:click={handleClose} aria-label="Close panel">✕</button>
      </div>

      {#if errorMsg}
        <div class="error-banner" role="alert">
          <span>⚠️ {errorMsg}</span>
          <button class="error-dismiss" on:click={() => errorMsg = ''}>✕</button>
        </div>
      {/if}

      <div class="panel-body">
        <section class="section">
          <span class="section-label">Current collaborators</span>
          {#if loading}
            <div class="loading-row">
              <span class="spinner"></span>
              <span class="loading-text">Loading…</span>
            </div>
          {:else if collaborators.length === 0}
            <p class="empty-state">No collaborators yet. Invite someone below.</p>
          {:else}
            <ul class="collaborator-list">
              {#each collaborators as collab (collab.id)}
                <li class="collaborator-item">
                  <span class="collab-avatar">{collab.collaboratorEmail.charAt(0).toUpperCase()}</span>
                  <span class="collab-email">{collab.collaboratorEmail}</span>
                  {#if collab.pending}
                    <span class="pending-badge">Pending</span>
                  {/if}
                  <button
                    class="remove-btn"
                    on:click={() => handleRemove(collab)}
                    aria-label="Remove {collab.collaboratorEmail}"
                  >Remove</button>
                </li>
              {/each}
            </ul>
          {/if}
        </section>

        <section class="section">
          <label class="section-label" for="invite-email">Invite by email</label>
          <div class="invite-row">
            <input
              id="invite-email"
              class="email-input"
              type="email"
              bind:value={emailInput}
              placeholder="colleague@example.com"
              on:keydown={handleEmailKeydown}
              on:input={() => errorMsg = ''}
              disabled={adding}
            />
            <button
              class="add-btn"
              on:click={handleAdd}
              disabled={adding || !emailInput.trim()}
            >
              {#if adding}
                <span class="spinner small"></span>
              {:else}
                Add
              {/if}
            </button>
          </div>
        </section>
      </div>

      <div class="panel-footer">
        <button class="done-btn" on:click={handleClose}>Done</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.2s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }

  .panel {
    background: #ffffff;
    border-radius: 20px;
    width: 100%;
    max-width: 480px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow:
      0 32px 64px rgba(0, 0, 0, 0.3),
      0 0 0 1px rgba(220, 38, 38, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.9);
    animation: slideUp 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    border-top: 4px solid #dc2626;
    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(24px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }

  /* Header */
  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    padding: 1.5rem 1.5rem 1rem;
    border-bottom: 1px solid #f1f5f9;
    background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
    border-radius: 16px 16px 0 0;
  }

  .header-title-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .header-icon {
    font-size: 1.4rem;
  }

  .header-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(135deg, #7f1d1d 0%, #dc2626 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .close-btn {
    background: none;
    border: none;
    color: #9ca3af;
    font-size: 1rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    transition: all 0.2s;
    line-height: 1;
  }

  .close-btn:hover {
    background: #fee2e2;
    color: #dc2626;
  }

  /* Error banner */
  .error-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin: 0.75rem 1.5rem 0;
    padding: 0.75rem 1rem;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-left: 4px solid #dc2626;
    border-radius: 8px;
    font-size: 0.875rem;
    color: #991b1b;
    font-weight: 500;
  }

  .error-dismiss {
    background: none;
    border: none;
    color: #dc2626;
    cursor: pointer;
    font-size: 0.875rem;
    padding: 0;
    line-height: 1;
    flex-shrink: 0;
  }

  /* Body */
  .panel-body {
    padding: 1.25rem 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .section-label {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #6b7280;
  }

  /* Loading */
  .loading-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
  }

  .loading-text {
    font-size: 0.875rem;
    color: #9ca3af;
  }

  /* Empty state */
  .empty-state {
    margin: 0;
    font-size: 0.875rem;
    color: #9ca3af;
    padding: 0.5rem 0;
  }

  /* Collaborator list */
  .collaborator-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .collaborator-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0.875rem;
    background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
    border: 1px solid #fecaca;
    border-radius: 10px;
    transition: all 0.2s;
  }

  .collaborator-item:hover {
    border-color: #fca5a5;
    background: #fef2f2;
  }

  .collab-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    color: white;
    font-size: 0.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .collab-email {
    flex: 1;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .remove-btn {
    padding: 0.3rem 0.75rem;
    background: none;
    border: 1.5px solid #fca5a5;
    border-radius: 6px;
    font-size: 0.775rem;
    font-weight: 600;
    color: #dc2626;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
    flex-shrink: 0;
  }

  .remove-btn:hover {
    background: #fee2e2;
    border-color: #dc2626;
  }

  .pending-badge {
    font-size: 0.7rem;
    font-weight: 600;
    color: #92400e;
    background: #fef3c7;
    border: 1px solid #fde68a;
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    white-space: nowrap;
    flex-shrink: 0;
  }

  /* Invite row */
  .invite-row {
    display: flex;
    gap: 0.5rem;
  }

  .email-input {
    flex: 1;
    padding: 0.6rem 0.875rem;
    border: 2px solid #fecaca;
    border-radius: 8px;
    font-size: 0.875rem;
    font-family: 'Inter', sans-serif;
    color: #1f2937;
    background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
    transition: all 0.25s;
  }

  .email-input::placeholder {
    color: #f87171;
  }

  .email-input:focus {
    outline: none;
    border-color: #dc2626;
    background: #ffffff;
    box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
  }

  .email-input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .add-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 64px;
    padding: 0.6rem 1rem;
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.25s;
    box-shadow: 0 4px 10px rgba(220, 38, 38, 0.25);
    font-family: 'Poppins', sans-serif;
  }

  .add-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
    box-shadow: 0 6px 14px rgba(220, 38, 38, 0.35);
    transform: translateY(-1px);
  }

  .add-btn:active:not(:disabled) {
    transform: translateY(0);
  }

  .add-btn:disabled {
    opacity: 0.55;
    cursor: not-allowed;
    box-shadow: none;
  }

  /* Footer */
  .panel-footer {
    display: flex;
    justify-content: flex-end;
    padding: 1rem 1.5rem 1.5rem;
    border-top: 1px solid #f1f5f9;
  }

  .done-btn {
    padding: 0.65rem 1.5rem;
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 0.875rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.25s;
    box-shadow: 0 6px 16px rgba(220, 38, 38, 0.3);
    font-family: 'Poppins', sans-serif;
  }

  .done-btn:hover {
    background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
    box-shadow: 0 10px 24px rgba(220, 38, 38, 0.4);
    transform: translateY(-1px);
  }

  .done-btn:active {
    transform: translateY(0);
  }

  /* Spinner */
  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(220, 38, 38, 0.3);
    border-top-color: #dc2626;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    display: inline-block;
    flex-shrink: 0;
  }

  .spinner.small {
    border-color: rgba(255, 255, 255, 0.4);
    border-top-color: white;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
