from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import new database configuration and models
import database
import models

# tell SQLAlchemy to create the tables in PostgreSQL if they don't exist yet
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Distributed Task Scheduler API")

# Define the exact data structure expected from the user
class TaskRequest(BaseModel):
    priority: int
    description: str

# Endpoint 1: Add a task to the database
@app.post("/tasks")
def create_task(request: TaskRequest, db: Session = Depends(database.get_db)):
    # 1. Create a new Python object representing the row
    new_task = models.Task(
        priority=request.priority,
        description=request.description,
        status="PENDING"
    )
    
    # 2. Add it to the session and commit it to the database
    db.add(new_task)
    db.commit()
    db.refresh(new_task) # This grabs the auto-generated ID from PostgreSQL
    
    return {"message": "Task added successfully!", "task": new_task}

# Endpoint 2: View the current queue from the database
@app.get("/tasks")
def view_queue(db: Session = Depends(database.get_db)):
    # 3. Query the database for all tasks, ordered by priority (lowest number first)
    tasks = db.query(models.Task).order_by(models.Task.priority.asc()).all()
    return {"current_queue_size": len(tasks), "tasks": tasks}