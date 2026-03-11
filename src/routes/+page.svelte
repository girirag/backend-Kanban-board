<script lang="ts">
  import { dndzone } from 'svelte-dnd-action';
  import { onMount, onDestroy } from "svelte";
  import { apiService, type Task } from '../lib/api';
  import { onAuthChange, logout, handleRedirectResult } from '../lib/auth';
  import Login from '../lib/components/Login.svelte';
  import type { User } from 'firebase/auth';

  const columns = ["Planning", "To Do", "In Progress", "In Review", "Done"];
  const columnEmojis: Record<string, string> = {
    "Planning": "💡",
    "To Do": "📝",
    "In Progress": "⚡",
    "In Review": "👀",
    "Done": "✅"
  };
  
  let currentUser: User | null = null;
  let authLoading = true;
  let newTask = '';
  let taskId = 1;
  let errorMessage = '';

  let board: Record<string, Task[]> = {};
  columns.forEach(col => board[col] = []);

  let originalBoardState: Record<string, Task[]> = {};
  let isDragging = false;
  let apiConnected = false;
  let unsubscribeAuth: (() => void) | null = null;

  function getAllTaskNames(): string[] {
    return Object.values(board).flat().map(task => task.text.toLowerCase().trim());
  }

  function getLocalStorageKey(): string {
    return `kanban-tasks-${currentUser?.uid || 'anonymous'}`;
  }

  function loadFromLocalStorage() {
    if (!currentUser) return;
    try {
      const savedTasks = localStorage.getItem(getLocalStorageKey());
      if (savedTasks) {
        const tasks = JSON.parse(savedTasks) as Task[];
        columns.forEach(col => board[col] = []);
        tasks.forEach(task => {
          if (board[task.column]) {
            board[task.column].push(task);
          }
        });
        if (tasks.length > 0) {
          taskId = Math.max(...tasks.map(t => t.id)) + 1;
        }
        board = { ...board };
      }
    } catch (error) {
      console.error('Error loading from localStorage:', error);
    }
  }

  function saveToLocalStorage() {
    if (!currentUser) return;
    try {
      const allTasks = Object.values(board).flat();
      localStorage.setItem(getLocalStorageKey(), JSON.stringify(allTasks));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }

  onMount(async () => {
    console.log('Component mounted, checking for redirect result...');
    
    // Handle redirect result from Google Sign-In
    try {
      const user = await handleRedirectResult();
      if (user) {
        console.log('User signed in via redirect:', user.email);
      } else {
        console.log('No redirect result found');
      }
    } catch (error: any) {
      console.error('Redirect result error:', error);
      if (error.code === 'auth/unauthorized-domain') {
        console.error('Domain not authorized in Firebase Console');
      }
    }
    
    unsubscribeAuth = onAuthChange(async (user) => {
      console.log('Auth state changed:', user?.email || 'No user');
      currentUser = user;
      authLoading = false;
      
      if (user) {
        loadFromLocalStorage();
        await connectToAPI();
      }
    });
  });

  onDestroy(() => {
    if (unsubscribeAuth) {
      unsubscribeAuth();
    }
  });

  async function handleLogout() {
    try {
      await logout();
      board = {};
      columns.forEach(col => board[col] = []);
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  async function connectToAPI() {
    if (!currentUser) return;
    
    try {
      console.log('Attempting to connect to API...');
      const healthCheck = await apiService.healthCheck();
      console.log('API Health Check:', healthCheck);
      apiConnected = healthCheck.status === 'healthy';
      
      if (apiConnected) {
        errorMessage = '';
        const tasks = await apiService.getTasks(currentUser.uid);
        console.log('Tasks loaded from API:', tasks);
        
        columns.forEach(col => board[col] = []);
        tasks.forEach(task => {
          if (board[task.column]) {
            board[task.column].push(task);
          }
        });
        
        if (tasks.length > 0) {
          const maxId = Math.max(...tasks.map(t => t.id));
          taskId = maxId + 1;
        }
        
        board = { ...board };
        saveToLocalStorage();
      }
    } catch (error) {
      console.error('API connection failed:', error);
      apiConnected = false;
      errorMessage = 'API connection failed - using offline mode. Click "Retry Connection" to try again.';
    }
  }

  async function addTask() {
    if (!currentUser) return;
    
    const trimmedTask = newTask.trim();
    if (!trimmedTask) {
      errorMessage = 'Task name cannot be empty';
      setTimeout(() => errorMessage = '', 3000);
      return;
    }
    const existingNames = getAllTaskNames();
    if (existingNames.includes(trimmedTask.toLowerCase())) {
      errorMessage = 'Task name already exists';
      setTimeout(() => errorMessage = '', 3000);
      return;
    }
    
    if (apiConnected) {
      try {
        const newTaskData = await apiService.createTask({
          text: trimmedTask,
          column: "Planning",
          userId: currentUser.uid
        });
        
        board["Planning"] = [...board["Planning"], newTaskData];
        board = { ...board };
        
        const allTasks = Object.values(board).flat();
        if (allTasks.length > 0) {
          const maxId = Math.max(...allTasks.map(t => t.id));
          taskId = maxId + 1;
        }
        
        saveToLocalStorage();
        
        console.log('Task created via API:', newTaskData);
      } catch (error) {
        console.error('API create failed:', error);
        const newItem: Task = {
          id: taskId++,
          text: trimmedTask,
          column: "Planning",
          userId: currentUser.uid
        };
        board["Planning"] = [...board["Planning"], newItem];
        board = { ...board };
        saveToLocalStorage();
        errorMessage = 'API save failed - saved locally';
        setTimeout(() => errorMessage = '', 3000);
      }
    } else {
      const newItem: Task = {
        id: taskId++,
        text: trimmedTask,
        column: "Planning",
        userId: currentUser.uid
      };
      board["Planning"] = [...board["Planning"], newItem];
      board = { ...board };
      saveToLocalStorage();
    }
    newTask = '';
  }

  function handleConsider(event: CustomEvent, column: string) {
    const { items } = event.detail;
    if (!isDragging) {
      isDragging = true;
      originalBoardState = {};
      columns.forEach(col => {
        originalBoardState[col] = [...board[col]];
      });
    }
    board[column] = items;
  }

  async function handleFinalize(event: CustomEvent, column: string) {
    const { items } = event.detail;
    const movedTask = items.find((item: Task) => item.column !== column);
    if (!movedTask) {
      board[column] = items;
      isDragging = false;
      originalBoardState = {};
      return;
    }
    const originalColumn = movedTask.column;
    const fromIndex = columns.indexOf(originalColumn);
    const toIndex = columns.indexOf(column);
    const canMoveForwardOneStep = toIndex === fromIndex + 1;
    const canMoveBackwardOneStep = toIndex === fromIndex - 1;
    const canMoveFromDone = originalColumn === "Done";
    
    if (canMoveForwardOneStep || canMoveBackwardOneStep || canMoveFromDone) {
      movedTask.column = column;
      board[column] = items;
      board[originalColumn] = board[originalColumn].filter(task => task.id !== movedTask.id);
      
      if (apiConnected) {
        try {
          await apiService.updateTask(movedTask.id, { column: column });
          console.log('Task updated via API:', movedTask.id);
        } catch (error) {
          console.error('API update failed:', error);
        }
      }
      saveToLocalStorage();
    } else {
      const restoredBoard: Record<string, Task[]> = {};
      columns.forEach(col => {
        restoredBoard[col] = [...originalBoardState[col]];
      });
      board = restoredBoard;
      board = { ...board };
      setTimeout(() => {
        board = { ...restoredBoard };
      }, 10);
    }
    isDragging = false;
    originalBoardState = {};
  }

  async function deleteTask(taskId: number, column: string, event?: Event) {
    event?.stopPropagation();
    
    if (apiConnected) {
      try {
        await apiService.deleteTask(taskId);
        console.log('Task deleted via API:', taskId);
      } catch (error) {
        console.error('API delete failed:', error);
      }
    }
    
    board[column] = board[column].filter(task => task.id !== taskId);
    board = { ...board };
    saveToLocalStorage();
  }
</script>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
  
  * {
    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }
  
  .board-container {
    background: 
      radial-gradient(circle at 20% 50%, rgba(220, 38, 38, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(239, 68, 68, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 40% 20%, rgba(185, 28, 28, 0.1) 0%, transparent 50%),
      linear-gradient(135deg, #7f1d1d 0%, #991b1b 15%, #b91c1c 30%, #dc2626 50%, #b91c1c 70%, #991b1b 85%, #7f1d1d 100%);
    background-size: 100% 100%;
    min-height: 100vh;
    padding: 2rem;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .board-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(255, 255, 255, 0.03) 35px, rgba(255, 255, 255, 0.03) 70px),
      repeating-linear-gradient(-45deg, transparent, transparent 35px, rgba(0, 0, 0, 0.03) 35px, rgba(0, 0, 0, 0.03) 70px);
    pointer-events: none;
    animation: shimmer 20s linear infinite;
  }
  
  @keyframes shimmer {
    0% { transform: translateX(0) translateY(0); }
    100% { transform: translateX(70px) translateY(70px); }
  }
  
  .board-wrapper {
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 1.75rem;
    box-shadow: 
      0 25px 50px rgba(0, 0, 0, 0.25),
      0 0 0 1px rgba(255, 255, 255, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.9);
    max-width: 1300px;
    width: 88%;
    margin: 0 auto;
    position: relative;
    border: 1px solid rgba(220, 38, 38, 0.1);
  }
  
  .board-header {
    display: flex;
    align-items: center;
    margin-bottom: 1.25rem;
    padding-bottom: 0.875rem;
    border-bottom: 2px solid transparent;
    background: linear-gradient(white, white) padding-box,
                linear-gradient(90deg, #dc2626, #ef4444, #f87171) border-box;
    border-image: linear-gradient(90deg, #dc2626, #ef4444, #f87171) 1;
    gap: 0.75rem;
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-left: auto;
    margin-right: 1rem;
  }
  
  .user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 2px solid #dc2626;
  }
  
  .user-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1f2937;
  }
  
  .logout-btn {
    padding: 0.5rem 1rem;
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.3s;
  }
  
  .logout-btn:hover {
    background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
  }
  
  .loading-container {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #7f1d1d 0%, #dc2626 50%, #ef4444 100%);
    color: white;
    gap: 1rem;
  }
  
  .loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .board-title {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .board-icon {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #f87171 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    box-shadow: 0 6px 20px rgba(220, 38, 38, 0.4);
    position: relative;
    overflow: hidden;
  }
  
  .board-icon::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: shine 3s infinite;
  }
  
  @keyframes shine {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
  }
  
  .board-name {
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7f1d1d 0%, #dc2626 50%, #ef4444 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.5px;
  }
  
  .add-task-section {
    margin-bottom: 1.25rem;
    display: flex;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .task-input {
    flex: 1;
    max-width: 400px;
    padding: 0.75rem 1rem;
    border: 2px solid #fecaca;
    border-radius: 10px;
    font-size: 0.875rem;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
    box-shadow: 
      0 4px 12px rgba(220, 38, 38, 0.08),
      inset 0 1px 2px rgba(255, 255, 255, 0.9);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    color: #1f2937;
  }
  
  .task-input::placeholder {
    color: #f87171;
    font-weight: 500;
  }
  
  .task-input:focus {
    outline: none;
    border-color: #dc2626;
    background: white;
    box-shadow: 
      0 8px 24px rgba(220, 38, 38, 0.15),
      0 0 0 4px rgba(220, 38, 38, 0.1),
      inset 0 1px 2px rgba(255, 255, 255, 0.9);
    transform: translateY(-2px);
  }
  
  .add-btn {
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 
      0 6px 16px rgba(220, 38, 38, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;
  }
  
  .add-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.5s;
  }
  
  .add-btn:hover {
    background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
    box-shadow: 
      0 12px 28px rgba(220, 38, 38, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }
  
  .add-btn:hover::before {
    left: 100%;
  }
  
  .add-btn:active {
    transform: translateY(0);
    box-shadow: 
      0 4px 12px rgba(220, 38, 38, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
  }
  
  .kanban {
    display: flex;
    gap: 1.25rem;
    width: 100%;
  }
  
  .column {
    flex: 1;
    min-width: 0;
    border-radius: 10px;
    padding: 0;
    min-height: 400px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border: 1px solid rgba(255,255,255,0.2);
  }
  
  .column:nth-child(1) {
    background: linear-gradient(180deg, #fee2e2 0%, #fecaca 50%, #fca5a5 100%);
    border: 2px solid #fca5a5;
  }
  .column:nth-child(2) {
    background: linear-gradient(180deg, #fed7aa 0%, #fdba74 50%, #fb923c 100%);
    border: 2px solid #fb923c;
  }
  .column:nth-child(3) {
    background: linear-gradient(180deg, #fef3c7 0%, #fde047 50%, #facc15 100%);
    border: 2px solid #facc15;
  }
  .column:nth-child(4) {
    background: linear-gradient(180deg, #fce7f3 0%, #fbcfe8 50%, #f9a8d4 100%);
    border: 2px solid #f9a8d4;
  }
  .column:nth-child(5) {
    background: linear-gradient(180deg, #dcfce7 0%, #bbf7d0 50%, #86efac 100%);
    border: 2px solid #86efac;
  }
  
  .column-header {
    padding: 0.875rem 1rem;
    border-bottom: 2px solid rgba(0, 0, 0, 0.1);
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
    border-radius: 10px 10px 0 0;
    position: relative;
    overflow: hidden;
  }
  
  .column-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    transition: left 0.6s;
  }
  
  .column-header:hover::before {
    left: 100%;
  }
  
  .column-title-wrapper {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    justify-content: center;
  }
  
  .column-emoji {
    font-size: 1.25rem;
    display: inline-block;
    transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  }
  
  .column-header:hover .column-emoji {
    transform: scale(1.2) rotate(10deg);
  }
  
  .column-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 1.1px;
    position: relative;
    transition: all 0.4s ease;
  }
  
  .column-header:hover .column-title {
    letter-spacing: 1.5px;
    transform: translateY(-1px);
  }
  
  .column:nth-child(1) .column-title {
    color: #dc2626;
  }
  
  .column:nth-child(2) .column-title {
    color: #ea580c;
  }
  
  .column:nth-child(3) .column-title {
    color: #ca8a04;
  }
  
  .column:nth-child(4) .column-title {
    color: #db2777;
  }
  
  .column:nth-child(5) .column-title {
    color: #059669;
  }
  
  .dnd-zone {
    padding: 0.875rem 1rem;
    min-height: 320px;
  }
  
  .task {
    background: linear-gradient(135deg, #ffffff 0%, #fef2f2 100%);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.875rem;
    box-shadow: 
      0 4px 12px rgba(0, 0, 0, 0.1),
      0 0 0 1px rgba(220, 38, 38, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.9);
    cursor: grab;
    border-left: 5px solid #dc2626;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
  }
  
  .task::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, transparent 0%, rgba(220, 38, 38, 0.03) 100%);
    pointer-events: none;
  }
  
  .task:hover {
    box-shadow: 
      0 8px 24px rgba(220, 38, 38, 0.2),
      0 0 0 1px rgba(220, 38, 38, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.9);
    transform: translateY(-3px) scale(1.02);
    border-left-width: 6px;
  }
  
  .task:active {
    cursor: grabbing;
    transform: scale(1.05);
    box-shadow: 
      0 12px 32px rgba(220, 38, 38, 0.3),
      0 0 0 2px rgba(220, 38, 38, 0.3);
  }
  
  .task-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .task-text {
    flex: 1;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #1f2937;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    position: relative;
    z-index: 1;
  }
  
  .task-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid #f1f5f9;
  }
  
  .task-id {
    font-size: 0.75rem;
    color: #6b7280;
    font-weight: 600;
  }
  
  .task-priority {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
  }
  
  .delete-btn {
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.4rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 700;
    cursor: pointer;
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
    z-index: 2;
  }
  
  .task:hover .delete-btn {
    opacity: 1;
    transform: scale(1);
  }
  
  .delete-btn:hover {
    background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
    box-shadow: 0 6px 16px rgba(220, 38, 38, 0.4);
    transform: scale(1.1);
  }
  
  .delete-btn:active {
    transform: scale(0.95);
  }
  
  .error-message {
    color: #ef4444;
    font-size: 0.875rem;
    margin-top: 0.5rem;
    padding: 0.5rem;
    background: #fef2f2;
    border-radius: 6px;
    border-left: 4px solid #ef4444;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }
  
  .retry-btn {
    padding: 0.5rem 1rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 0.875rem;
    cursor: pointer;
    white-space: nowrap;
  }
  
  .retry-btn:hover {
    background: #2563eb;
  }
  
  .connection-status {
    display: inline-flex;
    align-items: center;
    gap: 0.625rem;
    padding: 0.75rem 1.25rem;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 600;
    margin-left: auto;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
  }
  
  .connection-status.connected {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    color: #065f46;
    border: 2px solid #10b981;
  }
  
  .connection-status.disconnected {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    color: #991b1b;
    border: 2px solid #ef4444;
  }
  
  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    box-shadow: 0 0 8px currentColor;
  }
  
  .status-dot.connected {
    background: #10b981;
    animation: pulse-green 2s infinite;
  }
  
  .status-dot.disconnected {
    background: #ef4444;
    animation: pulse-red 2s infinite;
  }
  
  @keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 8px #10b981; }
    50% { box-shadow: 0 0 16px #10b981; }
  }
  
  @keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 8px #ef4444; }
    50% { box-shadow: 0 0 16px #ef4444; }
  }
</style>

{#if authLoading}
  <div class="loading-container">
    <div class="loading-spinner"></div>
    <p>Loading...</p>
  </div>
{:else if !currentUser}
  <Login />
{:else}
  <div class="board-container">
    <div class="board-wrapper">
      <div class="board-header">
        <div class="board-title">
          <div class="board-icon">📋</div>
          <h1 class="board-name">Project Board</h1>
        </div>
        {#if currentUser}
          <div class="user-info">
            <img src={currentUser.photoURL || ''} alt="Profile" class="user-avatar" />
            <span class="user-name">{currentUser.displayName}</span>
            <button class="logout-btn" on:click={handleLogout}>Logout</button>
          </div>
        {/if}
        <div class="connection-status {apiConnected ? 'connected' : 'disconnected'}">
          <div class="status-dot {apiConnected ? 'connected' : 'disconnected'}"></div>
          {apiConnected ? 'Connected to Firebase' : 'Offline Mode'}
        </div>
      </div>

    <div class="add-task-section">
      <input
        bind:value={newTask}
        placeholder="What needs to be done?"
        class="task-input"
        on:keydown={(e) => e.key === 'Enter' && addTask()}
      />
      <button
        on:click={addTask}
        class="add-btn"
      >
        Add Task
      </button>
    </div>

    {#if errorMessage}
      <div class="error-message">
        {errorMessage}
        {#if !apiConnected}
          <button class="retry-btn" on:click={connectToAPI}>Retry Connection</button>
        {/if}
      </div>
    {/if}

    <div class="kanban">
      {#each columns as column}
        <div class="column">
          <div class="column-header">
            <div class="column-title-wrapper">
              <span class="column-emoji">{columnEmojis[column]}</span>
              <h3 class="column-title">{column}</h3>
            </div>
          </div>
          <div
            class="dnd-zone"
            use:dndzone={{ items: board[column], flipDurationMs: 300, dropTargetStyle: {} }}
            on:consider={(event) => handleConsider(event, column)}
            on:finalize={(event) => handleFinalize(event, column)}
          >
            {#each board[column] as task (task.id)}
              <div class="task">
                <div class="task-content">
                  <div class="task-text">{task.text}</div>
                  {#if column === "Done"}
                    <button
                      class="delete-btn"
                      on:click={(e) => deleteTask(task.id, column, e)}
                      title="Delete task"
                    >
                      ✕
                    </button>
                  {/if}
                </div>
                <div class="task-meta">
                  <span class="task-id">TASK-{task.id}</span>
                  <div class="task-priority"></div>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  </div>
</div>
{/if}