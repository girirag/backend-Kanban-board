const API_BASE_URL = import.meta.env.PROD 
  ? 'https://backend-kanban-board-q2ft.onrender.com'
  : 'http://localhost:8001';

const API_VERSION = '2.0';

if (typeof window !== 'undefined') {
  console.log('API Version:', API_VERSION);
  console.log('Environment:', import.meta.env.MODE);
  console.log('PROD mode:', import.meta.env.PROD);
  console.log('API Base URL:', API_BASE_URL);
}

export interface Task {
  id: number;
  text: string;
  column: string;
  userId?: string;
  description?: string;
  assignees?: string[];
}

export interface TaskCreate {
  text: string;
  column?: string;
  userId: string;
}

export interface TaskUpdate {
  text?: string;
  column?: string;
  description?: string;
  assignees?: string[];
}

export interface Collaborator {
  id: string;
  collaboratorUid: string;
  collaboratorEmail: string;
}

export interface InvitedBoard {
  inviteId: string;
  ownerUserId: string;
  ownerName: string;
  ownerEmail: string;
}

export interface CollaborationCreate {
  ownerUserId: string;
  collaboratorEmail: string;
}

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`API Request: ${options.method || 'GET'} ${url}`);
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      mode: 'cors',
      ...options,
    };

    try {
      const response = await fetch(url, config);
      console.log(`API Response: ${response.status} ${response.statusText}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`API Data:`, data);
      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async getTasks(userId: string): Promise<Task[]> {
    return this.request<Task[]>(`/tasks?userId=${userId}`);
  }

  async createTask(task: TaskCreate): Promise<Task> {
    return this.request<Task>('/tasks', {
      method: 'POST',
      body: JSON.stringify(task),
    });
  }

  async updateTask(taskId: number, updates: TaskUpdate): Promise<Task> {
    return this.request<Task>(`/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteTask(taskId: number): Promise<void> {
    await this.request(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async healthCheck(): Promise<{ status: string; firebase_connected: boolean }> {
    return this.request('/health');
  }

  async getCollaborators(ownerUserId: string): Promise<Collaborator[]> {
    return this.request<Collaborator[]>(`/collaborations?ownerUserId=${ownerUserId}`);
  }

  async addCollaborator(payload: CollaborationCreate): Promise<Collaborator> {
    return this.request<Collaborator>('/collaborations', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async removeCollaborator(inviteId: string): Promise<void> {
    await this.request(`/collaborations/${inviteId}`, {
      method: 'DELETE',
    });
  }

  async getInvitedBoards(collaboratorUid: string): Promise<InvitedBoard[]> {
    return this.request<InvitedBoard[]>(`/collaborations/invited?collaboratorUid=${collaboratorUid}`);
  }
}

export const apiService = new ApiService();