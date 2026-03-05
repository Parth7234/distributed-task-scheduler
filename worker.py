import time
import datetime
import redis
from database import SessionLocal
import models

# connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def start_worker():
    print("Worker started. Fetching tasks from the Redis queue...")
    
    # infinite loop to keep the worker alive 24/7
    while True:
        # ask Redis for the highest priority task (lowest score)
        task_data = redis_client.zpopmin("task_queue", count=1)# zpopmin pops the item with the lowest score off the sorted set
        
        if not task_data:
            # If the queue is empty, rest for 1 second 
            time.sleep(1)
            continue
            
        # unpack the data given by Redis
        # task_data format: [('1', 2.0)] -> [('task_id', priority_score)]
        task_id_str, priority = task_data[0]
        task_id = int(task_id_str)
        
        print(f"\n[Worker] Grabbed Task ID: {task_id} (Priority: {priority})")
        
        # open a database session to look up what the task is
        db = SessionLocal()
        try:
            task = db.query(models.Task).filter(models.Task.id == task_id).first()
            
            if task:
                # mark task as RUNNING so the API knows we are working on it
                task.status = "RUNNING"
                
                # record the exact UTC time the task started
                task.started_at = datetime.datetime.utcnow() 
                
                db.commit()
                
                print(f"[Worker] Executing: '{task.description}'...")
                
                # heavy work simulation (e.g., training a model, sending emails)
                time.sleep(5) 
                
                # mark task as completed
                task.status = "COMPLETED"
                db.commit()
                print(f"[Worker] Successfully finished Task ID: {task_id} ")
            else:
                print(f"[Worker] Error: Task {task_id} not found in database!")

        except Exception as e: #catch block
            print(f"[Worker] Error while executing task {task_id}: {e}")

        finally: #finally block always executes no matter success or failure
            # close the connection when done 
            db.close()

if __name__ == "__main__":
    start_worker()