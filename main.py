from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse  
from pydantic import BaseModel, Field
import controllers
import json 
from typing import Optional

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Task Management System",
    description="Backend API with JSON Lines persistence and automatic backups."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows any "webpage" to talk to your API
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskCreate(BaseModel):
    title: str = Field(
        ..., 
        example="Finish Final Project", 
        description="The name of the task"
    )
    description: Optional[str] = Field(
        None, 
        example="Implement the upgraded Pydantic models", 
        description="Optional details about the task"
    )
    completed: bool = Field(
        False, 
        example=False, 
        description="Whether the task is finished"
    )

# --- Endpoints ---

@app.get("/", tags=["General"])
def root():
    return {"message": "Task Management API is running"}

@app.get("/tasks/export", tags=["System Operations"])
def export_tasks():
    """
    Optional: Returns tasks as a downloadable, pretty-printed JSON file.
    """
    tasks = controllers.load_tasks()
    export_filename = "exported_tasks.json"
    
    with open(export_filename, "w") as f:
        json.dump(tasks, f, indent=4)
    
    return FileResponse(
        path=export_filename, 
        filename="my_tasks_export.json", 
        media_type='application/json'
    )

@app.get("/tasks/stats", tags=["Reporting"])
def get_statistics():
    tasks = controllers.load_tasks()
    total = len(tasks)
    completed = len([t for t in tasks if t["completed"]])
    pending = total - completed
    percentage = (completed / total * 100) if total > 0 else 0
    
    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "completion_percentage": round(percentage, 2)
    }

@app.get("/tasks", tags=["Task Operations"])
def get_tasks(completed: Optional[bool] = Query(default=None), q: Optional[str] = None):
    tasks = controllers.load_tasks()
    
    # Filter by completion if requested
    if completed is not None:
        tasks = [t for t in tasks if t["completed"] == completed]
    
    # Filter by search term (case-insensitive) if requested
    if q:
        tasks = [t for t in tasks if q.lower() in t["title"].lower()]
        
    return tasks

@app.get("/tasks/{task_id}", tags=["Task Operations"])
def get_single_task(task_id: int):
    return controllers.get_task_by_id(task_id)

@app.post("/tasks", status_code=201, tags=["Task Operations"])
def create_task(task: TaskCreate):
    return controllers.create_new_task(task)

@app.put("/tasks/{task_id}", tags=["Task Operations"])
def update_task(task_id: int, task: TaskCreate):
    return controllers.update_existing_task(task_id, task)

@app.delete("/tasks/{task_id}", tags=["Task Operations"])
def delete_task(task_id: int):
    return controllers.delete_task_by_id(task_id)

@app.delete("/tasks", tags=["Task Operations"])
def delete_all():
    return controllers.delete_all_tasks()

@app.post("/tasks/backup/trigger", tags=["System Operations"])
def trigger_backup():
    tasks = controllers.load_tasks()
    controllers.save_tasks(tasks) # This automatically triggers shutil.copy internally
    return {"message": "Backup created successfully as tasks_backup.txt"}