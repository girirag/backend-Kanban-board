from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime

app = FastAPI(title="Kanban Board API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    id: int
    text: str
    column: str
    userId: Optional[str] = None
    description: Optional[str] = None
    assignees: Optional[List[str]] = []

class TaskCreate(BaseModel):
    text: str
    column: str = "Planning"
    userId: str

class TaskUpdate(BaseModel):
    text: Optional[str] = None
    column: Optional[str] = None
    description: Optional[str] = None
    assignees: Optional[List[str]] = None

class CollaborationCreate(BaseModel):
    ownerUserId: str
    collaboratorEmail: str

class CollaborationRecord(BaseModel):
    id: str
    ownerUserId: str
    collaboratorUid: str
    collaboratorEmail: str
    createdAt: str
    pending: Optional[bool] = False

class InvitedBoard(BaseModel):
    inviteId: str
    ownerUserId: str
    ownerName: str
    ownerEmail: str

# In-memory storage for now (will be replaced with Firebase)
tasks_db = []
next_id = 1

# Try to load existing tasks from file
TASKS_FILE = "tasks_backup.json"

def load_tasks():
    global tasks_db, next_id
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                data = json.load(f)
                tasks_db = data.get('tasks', [])
                next_id = data.get('next_id', 1)
                print(f"Loaded {len(tasks_db)} tasks from backup")
    except Exception as e:
        print(f"Error loading tasks: {e}")
        tasks_db = []
        next_id = 1

def save_tasks():
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump({
                'tasks': tasks_db,
                'next_id': next_id,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    except Exception as e:
        print(f"Error saving tasks: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize Firebase and sync data on startup"""
    load_tasks()
    if firebase_connected:
        await sync_with_firebase()

@app.get("/")
async def root():
    return {
        "message": "Kanban Board API is running",
        "tasks_count": len(tasks_db),
        "firebase_status": "connecting..."
    }

@app.get("/tasks", response_model=List[Task])
async def get_tasks(userId: str):
    try:
        user_tasks = [Task(**task) for task in tasks_db if task.get('userId') == userId]
        return user_tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")

@app.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    global next_id
    try:
        new_task = {
            "id": next_id,
            "text": task.text,
            "column": task.column,
            "userId": task.userId
        }
        
        tasks_db.append(new_task)
        next_id += 1
        
        # Save to Firebase if connected
        if firebase_connected:
            await save_task_to_firebase(new_task)
        
        save_tasks()
        
        print(f"Created task: {new_task}")
        return Task(**new_task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: TaskUpdate):
    try:
        # Find the task
        task_index = None
        for i, task in enumerate(tasks_db):
            if task['id'] == task_id:
                task_index = i
                break
        
        if task_index is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update the task
        update_data = {}
        if task_update.text is not None:
            tasks_db[task_index]['text'] = task_update.text
            update_data['text'] = task_update.text
        if task_update.column is not None:
            tasks_db[task_index]['column'] = task_update.column
            update_data['column'] = task_update.column
        if task_update.description is not None:
            tasks_db[task_index]['description'] = task_update.description
            update_data['description'] = task_update.description
        if task_update.assignees is not None:
            tasks_db[task_index]['assignees'] = task_update.assignees
            update_data['assignees'] = task_update.assignees
        
        # Update in Firebase if connected
        if firebase_connected and update_data:
            await update_task_in_firebase(task_id, update_data)
        
        save_tasks()
        
        print(f"Updated task {task_id}: {tasks_db[task_index]}")
        return Task(**tasks_db[task_index])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    try:
        # Find and remove the task
        task_index = None
        for i, task in enumerate(tasks_db):
            if task['id'] == task_id:
                task_index = i
                break
        
        if task_index is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        deleted_task = tasks_db.pop(task_index)
        
        # Delete from Firebase if connected
        if firebase_connected:
            await delete_task_from_firebase(task_id)
        
        save_tasks()
        
        print(f"Deleted task {task_id}: {deleted_task}")
        return {"message": f"Task {task_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "tasks_count": len(tasks_db),
        "firebase_connected": firebase_connected,
        "storage": "firebase" if firebase_connected else "file_backup"
    }

# --- Collaboration endpoints ---

@app.post("/collaborations", response_model=CollaborationRecord)
async def create_collaboration(payload: CollaborationCreate):
    if not firebase_connected or not firebase_db:
        raise HTTPException(status_code=503, detail="Firebase not connected")

    collabs_ref = firebase_db.collection('collaborations')

    # Check for duplicate by email (works for both registered and pending invites)
    dup_query = (
        collabs_ref
        .where('ownerUserId', '==', payload.ownerUserId)
        .where('collaboratorEmail', '==', payload.collaboratorEmail)
        .limit(1)
        .stream()
    )
    if next(dup_query, None) is not None:
        raise HTTPException(status_code=409, detail="Already a collaborator")

    # Look up collaborator by email — if not found, store as pending invite
    users_ref = firebase_db.collection('users')
    query = users_ref.where('email', '==', payload.collaboratorEmail).limit(1).stream()
    user_doc = next(query, None)
    collaborator_uid = user_doc.id if user_doc else ''

    # Write new collaboration record (uid may be empty for pending invites)
    created_at = datetime.utcnow().isoformat()
    doc_ref = collabs_ref.document()
    record = {
        'ownerUserId': payload.ownerUserId,
        'collaboratorUid': collaborator_uid,
        'collaboratorEmail': payload.collaboratorEmail,
        'createdAt': created_at,
        'pending': collaborator_uid == '',
    }
    doc_ref.set(record)

    return CollaborationRecord(id=doc_ref.id, **record)


@app.get("/collaborations/invited", response_model=List[InvitedBoard])
async def get_invited_boards(collaboratorUid: str):
    if not firebase_connected or not firebase_db:
        raise HTTPException(status_code=503, detail="Firebase not connected")

    collabs_ref = firebase_db.collection('collaborations')
    docs = collabs_ref.where('collaboratorUid', '==', collaboratorUid).stream()

    results: List[InvitedBoard] = []
    for doc in docs:
        data = doc.to_dict()
        owner_uid = data.get('ownerUserId', '')
        owner_doc = firebase_db.collection('users').document(owner_uid).get()
        if owner_doc.exists:
            owner_data = owner_doc.to_dict()
            owner_name = owner_data.get('displayName', '')
            owner_email = owner_data.get('email', '')
        else:
            owner_name = ''
            owner_email = ''
        results.append(InvitedBoard(
            inviteId=doc.id,
            ownerUserId=owner_uid,
            ownerName=owner_name,
            ownerEmail=owner_email,
        ))

    return results


@app.get("/collaborations", response_model=List[CollaborationRecord])
async def get_collaborations(ownerUserId: str):
    if not firebase_connected or not firebase_db:
        raise HTTPException(status_code=503, detail="Firebase not connected")

    collabs_ref = firebase_db.collection('collaborations')
    docs = collabs_ref.where('ownerUserId', '==', ownerUserId).stream()

    results: List[CollaborationRecord] = []
    for doc in docs:
        data = doc.to_dict()
        results.append(CollaborationRecord(
            id=doc.id,
            ownerUserId=data.get('ownerUserId', ''),
            collaboratorUid=data.get('collaboratorUid', ''),
            collaboratorEmail=data.get('collaboratorEmail', ''),
            createdAt=data.get('createdAt', ''),
        ))

    return results


@app.delete("/collaborations/{invite_id}")
async def delete_collaboration(invite_id: str):
    if not firebase_connected or not firebase_db:
        raise HTTPException(status_code=503, detail="Firebase not connected")

    doc_ref = firebase_db.collection('collaborations').document(invite_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Collaboration not found")

    doc_ref.delete()
    return {"message": f"Collaboration {invite_id} deleted successfully"}


# Firebase integration
firebase_db = None
firebase_connected = False

def init_firebase():
    global firebase_db, firebase_connected
    try:
        if not os.path.exists("firebase-service-account.json"):
            print("❌ Firebase service account file not found")
            return False
            
        # Check if the file contains placeholder values
        with open("firebase-service-account.json", 'r') as f:
            service_account = json.load(f)
            
        if (service_account.get("private_key", "").strip() == "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----" or
            "your-private-key" in service_account.get("private_key", "") or
            "xxxxx" in service_account.get("client_email", "")):
            print("❌ Firebase service account contains placeholder values")
            print("📝 Please replace firebase-service-account.json with real credentials from Firebase Console")
            return False
            
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Check if app is already initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate("firebase-service-account.json")
            firebase_admin.initialize_app(cred)
        
        firebase_db = firestore.client()
        firebase_connected = True
        
        print("✅ Firebase initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        if "InvalidData" in str(e):
            print("📝 The private key in firebase-service-account.json is invalid")
            print("📝 Please download a new service account key from Firebase Console")
        firebase_connected = False
    return False

async def sync_with_firebase():
    """Sync local tasks with Firebase"""
    global tasks_db
    if not firebase_connected or not firebase_db:
        return
    
    try:
        # Get tasks from Firebase
        tasks_ref = firebase_db.collection('kanban-tasks')
        docs = tasks_ref.stream()
        
        firebase_tasks = []
        for doc in docs:
            task_data = doc.to_dict()
            task_data['id'] = int(doc.id)
            firebase_tasks.append(task_data)
        
        if firebase_tasks:
            tasks_db = firebase_tasks
            print(f"Synced {len(firebase_tasks)} tasks from Firebase")
        
    except Exception as e:
        print(f"Firebase sync failed: {e}")

async def save_task_to_firebase(task_data):
    """Save task to Firebase"""
    if not firebase_connected or not firebase_db:
        return False
    
    try:
        doc_ref = firebase_db.collection('kanban-tasks').document(str(task_data['id']))
        doc_ref.set(task_data)
        print(f"Saved task {task_data['id']} to Firebase")
        return True
    except Exception as e:
        print(f"Failed to save task to Firebase: {e}")
        return False

async def update_task_in_firebase(task_id, task_data):
    """Update task in Firebase"""
    if not firebase_connected or not firebase_db:
        return False
    
    try:
        doc_ref = firebase_db.collection('kanban-tasks').document(str(task_id))
        doc_ref.update(task_data)
        print(f"Updated task {task_id} in Firebase")
        return True
    except Exception as e:
        print(f"Failed to update task in Firebase: {e}")
        return False

async def delete_task_from_firebase(task_id):
    """Delete task from Firebase"""
    if not firebase_connected or not firebase_db:
        return False
    
    try:
        doc_ref = firebase_db.collection('kanban-tasks').document(str(task_id))
        doc_ref.delete()
        print(f"Deleted task {task_id} from Firebase")
        return True
    except Exception as e:
        print(f"Failed to delete task from Firebase: {e}")
        return False

# Try to initialize Firebase on startup
init_firebase()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    print("🚀 Starting Kanban Board API...")
    print(f"📊 API Documentation: http://localhost:{port}/docs")
    print("🔥 Firebase Status:", "Connected" if firebase_connected else "Using file backup")
    uvicorn.run(app, host="0.0.0.0", port=port)