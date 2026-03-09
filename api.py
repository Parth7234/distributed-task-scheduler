import os
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import redis  
import database
import models

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Distributed Task Scheduler API")

# connect to Redis (defaults to localhost for local development)
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

class TaskRequest(BaseModel):
    priority: int
    description: str

@app.post("/tasks")
def create_task(request: TaskRequest, db: Session = Depends(database.get_db)):
    # save task to the PostgreSQL database
    new_task = models.Task(
        priority=request.priority,
        description=request.description,
        status="PENDING"
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task) # grab new ID from the database
    
    # add Task ID to Redis priority queue  
    redis_client.zadd("task_queue", {str(new_task.id): new_task.priority})
    
    return {"message": "Task added to database and queued in Redis!", "task": new_task}

@app.get("/tasks")
def view_queue(db: Session = Depends(database.get_db)):
    tasks = db.query(models.Task).order_by(models.Task.priority.asc()).all()
    return {"current_queue_size": len(tasks), "tasks": tasks}