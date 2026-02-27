import json
import os
import shutil 
from fastapi import HTTPException


FILE_NAME = "tasks.txt"

def save_tasks(tasks):
    # 2. CREATE BACKUP: Copy existing file to tasks_backup.txt if it exists
    if os.path.exists(FILE_NAME):
        shutil.copy(FILE_NAME, "tasks_backup.txt")
    
    # 3. SAVE DATA: Proceed with normal JSON Lines writing
    with open(FILE_NAME, "w") as file:
        for task in tasks:
            file.write(json.dumps(task) + "\n")


# File Operations

def load_tasks():
    tasks = []
    if not os.path.exists(FILE_NAME):
        return tasks

    with open(FILE_NAME, "r") as file:
        for line in file:
            if line.strip():
                tasks.append(json.loads(line))
    return tasks


def save_tasks(tasks):
    # Create a backup of the current file before overwriting it
    if os.path.exists(FILE_NAME):
        shutil.copy(FILE_NAME, "tasks_backup.txt")
    
    with open(FILE_NAME, "w") as file:
        for task in tasks:
            file.write(json.dumps(task) + "\n")


def get_next_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

# Task Logic

def get_task_by_id(task_id: int):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


# In create_new_task: Change "completed": False to task_data.completed
def create_new_task(task_data):
    tasks = load_tasks()
    new_task = {
        "id": get_next_id(tasks),
        "title": task_data.title,
        "description": task_data.description,
        "completed": task_data.completed  # Use the user's input
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

# In update_existing_task: Add the completed line
def update_existing_task(task_id: int, task_data):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = task_data.title
            task["description"] = task_data.description
            task["completed"] = task_data.completed  # Save the new status
            save_tasks(tasks)
            return task
    raise HTTPException(status_code=404, detail="Task not found")


def delete_task_by_id(task_id: int):
    tasks = load_tasks()
    updated_tasks = [task for task in tasks if task["id"] != task_id]

    if len(tasks) == len(updated_tasks):
        raise HTTPException(status_code=404, detail="Task not found")

    save_tasks(updated_tasks)
    return {"message": "Task deleted successfully"}


def delete_all_tasks():
    save_tasks([])
    return {"message": "All tasks deleted successfully"}
