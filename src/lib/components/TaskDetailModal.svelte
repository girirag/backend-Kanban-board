<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Task } from '../api';
  import { addAssignee, removeAssignee, validateDescription } from '../taskDetailsUtils';

  export let task: Task;
  export let open: boolean;

  const dispatch = createEventDispatcher<{
    save: Task;
    close: void;
  }>();

  let draftDescription: string = '';
  let draftAssignees: string[] = [];
  let assigneeInput: string = '';
  let assigneeError: string = '';
  let saveError: string = '';
  let saving: boolean = false;

  // Sync draft state when task or open changes
  $: if (open && task) {
    draftDescription = task.description ?? '';
    draftAssignees = [...(task.assignees ?? [])];
    assigneeInput = '';
    assigneeError = '';
    saveError = '';
    saving = false;
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
    if (e.key === 'Escape' && open) {
      handleClose();
    }
  }

  function handleAddAssignee() {
    if (!assigneeInput.trim()) return;
    const result = addAssignee(draftAssignees, assigneeInput);
    if ('error' in result) {
      assigneeError = result.error;
    } else {
      draftAssignees = result.list;
      assigneeInput = '';
      assigneeError = '';
    }
  }

  function handleAssigneeKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddAssignee();
    }
  }

  function handleRemoveAssignee(index: number) {
    draftAssignees = removeAssignee(draftAssignees, index);
  }

  async function handleSave() {
    if (!validateDescription(draftDescription)) return;
    saving = true;
    saveError = '';
    try {
      const updatedTask: Task = {
        ...task,
        description: draftDescription,
        assignees: [...draftAssignees],
      };
      dispatch('save', updatedTask);
    } catch (err) {
      saveError = err instanceof Error ? err.message : 'Failed to save. Please try again.';
      saving = false;
    }
  }

  // Allow parent to signal save failure by watching saving prop externally
  // The parent should set saving=false and pass an error via a store if needed.
  // For now, saving is reset after dispatch.
  $: if (!open) {
    saving = false;
  }

  const charLimit = 500;
  $: charsLeft = charLimit - draftDescription.length;
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
  <!-- Backdrop -->
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="backdrop" on:click={handleBackdropClick}>
    <!-- Modal panel -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="modal" on:click={handlePanelClick} role="dialog" aria-modal="true" aria-label="Task details" tabindex="-1">
      <!-- Header -->
      <div class="modal-header">
        <div class="modal-title-row">
          <span class="modal-icon">📋</span>
          <h2 class="modal-title">{task.text}</h2>
        </div>
        <button class="close-btn" on:click={handleClose} aria-label="Close modal">✕</button>
      </div>

      <!-- Error banner -->
      {#if saveError}
        <div class="error-banner" role="alert">
          <span>⚠️ {saveError}</span>
          <button class="error-dismiss" on:click={() => saveError = ''}>✕</button>
        </div>
      {/if}

      <!-- Body -->
      <div class="modal-body">
        <!-- Description section -->
        <section class="section">
          <label class="section-label" for="description-input">Description</label>
          <div class="textarea-wrapper">
            <textarea
              id="description-input"
              class="description-textarea"
              bind:value={draftDescription}
              maxlength="500"
              placeholder="Add a description…"
              rows="4"
            ></textarea>
            <span class="char-counter" class:warn={charsLeft <= 50} class:danger={charsLeft <= 10}>
              {charsLeft} / {charLimit}
            </span>
          </div>
        </section>

        <!-- Assignees section -->
        <section class="section">
          <label class="section-label" for="assignee-input">Assignees</label>

          <!-- Assignee list -->
          {#if draftAssignees.length > 0}
            <ul class="assignee-list">
              {#each draftAssignees as assignee, i}
                <li class="assignee-chip">
                  <span class="assignee-avatar">{assignee.charAt(0).toUpperCase()}</span>
                  <span class="assignee-name">{assignee}</span>
                  <button
                    class="remove-assignee-btn"
                    on:click={() => handleRemoveAssignee(i)}
                    aria-label="Remove {assignee}"
                  >✕</button>
                </li>
              {/each}
            </ul>
          {/if}

          <!-- Add assignee input -->
          <div class="assignee-input-row">
            <input
              id="assignee-input"
              class="assignee-input"
              type="text"
              bind:value={assigneeInput}
              placeholder="Name or email…"
              on:keydown={handleAssigneeKeydown}
              on:input={() => assigneeError = ''}
            />
            <button class="add-assignee-btn" on:click={handleAddAssignee}>Add</button>
          </div>
          {#if assigneeError}
            <p class="assignee-error" role="alert">{assigneeError}</p>
          {/if}
        </section>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button class="cancel-btn" on:click={handleClose}>Cancel</button>
        <button
          class="save-btn"
          on:click={handleSave}
          disabled={saving || !validateDescription(draftDescription)}
        >
          {#if saving}
            <span class="spinner"></span> Saving…
          {:else}
            Save
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

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

  .modal {
    background: #ffffff;
    border-radius: 20px;
    width: 100%;
    max-width: 520px;
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

  /* ── Header ── */
  .modal-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.75rem;
    padding: 1.5rem 1.5rem 1rem;
    border-bottom: 1px solid #f1f5f9;
    background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
    border-radius: 16px 16px 0 0;
  }

  .modal-title-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 1;
    min-width: 0;
  }

  .modal-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
  }

  .modal-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0;
    line-height: 1.4;
    word-break: break-word;
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
    flex-shrink: 0;
    line-height: 1;
  }

  .close-btn:hover {
    background: #fee2e2;
    color: #dc2626;
  }

  /* ── Error banner ── */
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

  /* ── Body ── */
  .modal-body {
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

  /* ── Description ── */
  .textarea-wrapper {
    position: relative;
  }

  .description-textarea {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 2px solid #fecaca;
    border-radius: 10px;
    font-size: 0.9rem;
    font-family: 'Inter', sans-serif;
    color: #1f2937;
    background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
    resize: vertical;
    transition: all 0.25s;
    box-sizing: border-box;
    line-height: 1.6;
  }

  .description-textarea::placeholder {
    color: #f87171;
  }

  .description-textarea:focus {
    outline: none;
    border-color: #dc2626;
    background: #ffffff;
    box-shadow:
      0 0 0 4px rgba(220, 38, 38, 0.1),
      0 4px 12px rgba(220, 38, 38, 0.08);
  }

  .char-counter {
    position: absolute;
    bottom: 0.5rem;
    right: 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: #9ca3af;
    pointer-events: none;
    transition: color 0.2s;
  }

  .char-counter.warn   { color: #f59e0b; }
  .char-counter.danger { color: #dc2626; }

  /* ── Assignees ── */
  .assignee-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .assignee-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    border: 1px solid #fca5a5;
    border-radius: 999px;
    padding: 0.3rem 0.6rem 0.3rem 0.4rem;
    font-size: 0.8rem;
    font-weight: 600;
    color: #991b1b;
    transition: all 0.2s;
  }

  .assignee-chip:hover {
    background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
  }

  .assignee-avatar {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .assignee-name {
    max-width: 160px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .remove-assignee-btn {
    background: none;
    border: none;
    color: #dc2626;
    cursor: pointer;
    font-size: 0.7rem;
    padding: 0;
    line-height: 1;
    opacity: 0.7;
    transition: opacity 0.2s;
    flex-shrink: 0;
  }

  .remove-assignee-btn:hover {
    opacity: 1;
  }

  .assignee-input-row {
    display: flex;
    gap: 0.5rem;
  }

  .assignee-input {
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

  .assignee-input::placeholder {
    color: #f87171;
  }

  .assignee-input:focus {
    outline: none;
    border-color: #dc2626;
    background: #ffffff;
    box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
  }

  .add-assignee-btn {
    padding: 0.6rem 1rem;
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.25s;
    white-space: nowrap;
    box-shadow: 0 4px 10px rgba(220, 38, 38, 0.25);
  }

  .add-assignee-btn:hover {
    background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
    box-shadow: 0 6px 14px rgba(220, 38, 38, 0.35);
    transform: translateY(-1px);
  }

  .add-assignee-btn:active {
    transform: translateY(0);
  }

  .assignee-error {
    margin: 0;
    font-size: 0.8rem;
    font-weight: 600;
    color: #dc2626;
    padding: 0.35rem 0.75rem;
    background: #fef2f2;
    border-radius: 6px;
    border-left: 3px solid #dc2626;
  }

  /* ── Footer ── */
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    padding: 1rem 1.5rem 1.5rem;
    border-top: 1px solid #f1f5f9;
  }

  .cancel-btn {
    padding: 0.65rem 1.25rem;
    background: #f9fafb;
    color: #6b7280;
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'Poppins', sans-serif;
  }

  .cancel-btn:hover {
    background: #f3f4f6;
    border-color: #d1d5db;
    color: #374151;
  }

  .save-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
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

  .save-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
    box-shadow: 0 10px 24px rgba(220, 38, 38, 0.4);
    transform: translateY(-1px);
  }

  .save-btn:active:not(:disabled) {
    transform: translateY(0);
  }

  .save-btn:disabled {
    opacity: 0.55;
    cursor: not-allowed;
    box-shadow: none;
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    display: inline-block;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
