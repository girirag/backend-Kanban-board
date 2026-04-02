<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { InvitedBoard } from '../api';

  export let ownBoard: { userId: string; label: string };
  export let invitedBoards: InvitedBoard[];
  export let activeUserId: string;

  const dispatch = createEventDispatcher<{ switch: { userId: string; ownerName: string } }>();

  function handleChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    const value = select.value;

    if (value === ownBoard.userId) {
      dispatch('switch', { userId: ownBoard.userId, ownerName: ownBoard.label });
    } else {
      const board = invitedBoards.find(b => b.ownerUserId === value);
      if (board) {
        dispatch('switch', { userId: board.ownerUserId, ownerName: board.ownerName });
      }
    }
  }
</script>

{#if invitedBoards.length > 0}
  <select class="board-switcher" value={activeUserId} on:change={handleChange}>
    <option value={ownBoard.userId}>My Board</option>
    {#each invitedBoards as board (board.inviteId)}
      <option value={board.ownerUserId}>{board.ownerName}'s Board</option>
    {/each}
  </select>
{/if}

<style>
  .board-switcher {
    appearance: none;
    -webkit-appearance: none;
    padding: 0.4rem 2rem 0.4rem 0.75rem;
    border: 2px solid #fca5a5;
    border-radius: 8px;
    background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%)
      url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23dc2626' d='M6 8L1 3h10z'/%3E%3C/svg%3E")
      no-repeat right 0.6rem center;
    background-size: auto, 12px;
    color: #7f1d1d;
    font-size: 0.8rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(220, 38, 38, 0.12);
    transition: all 0.2s ease;
    min-width: 140px;
  }

  .board-switcher:hover {
    border-color: #dc2626;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
  }

  .board-switcher:focus {
    outline: none;
    border-color: #dc2626;
    box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.15);
  }
</style>
