from fastapi import FastAPI
from pydantic import BaseModel
import heapq

# Initialize the FastAPI app
app = FastAPI(title="Distributed Task Scheduler API")

# Our in-memory queue from Phase 1
task_queue = []
task_counter = 1

# This defines the exact data structure we expect the user to send us
class TaskRequest(BaseModel):
    priority: int
    description: str

# Endpoint 1: Add a task to the queue
@app.post("/tasks")
def create_task(request: TaskRequest):
    global task_counter
    
    # Push to our heap using a tuple: (priority, task_id, description, status)
    # heapq automatically sorts tuples by their first element (priority)
    heapq.heappush(task_queue, (request.priority, task_counter, request.description, "PENDING"))
    
    assigned_id = task_counter
    task_counter += 1
    
    return {"message": "Task added successfully!", "task_id": assigned_id, "priority": request.priority}

# Endpoint 2: View the current queue
@app.get("/tasks")
def view_queue():
    # Returns the raw queue so we can see what's inside
    return {"current_queue_size": len(task_queue), "tasks": task_queue}