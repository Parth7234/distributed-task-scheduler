import time
import datetime
import redis
from database import SessionLocal
import models

# connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

TIMEOUT_SECONDS = 60 

def run_sweeper():
    print("Sweeper started. Looking for ghost tasks every 10 seconds...")
    
    while True:
        db = SessionLocal()
        try:
            # calculate the cutoff time: Right now MINUS 60 seconds
            cutoff_time = datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=TIMEOUT_SECONDS)
            
            # query PostgreSQL for tasks that are RUNNING but started before the cutoff time
            ghost_tasks = db.query(models.Task).filter(
                models.Task.status == "RUNNING",
                models.Task.started_at < cutoff_time
            ).all()
            
            for task in ghost_tasks:
                print(f"\n[Sweeper] Found crashed Task ID: {task.id}. Requeuing...")
                
                # reset the database state
                task.status = "PENDING"
                task.started_at = None # Clear the old start time
                
                # put task back to the Redis queue
                redis_client.zadd("task_queue", {str(task.id): task.priority})
            
            # save all the updates to the database at once
            if ghost_tasks:
                db.commit()
                print("[Sweeper] Successfully rescued tasks.")
                
        except Exception as e:
            print(f"[Sweeper] Error: {e}")
            
        finally:
            db.close()
            
        # Rest for 10 seconds before sweeping the floor again
        time.sleep(10)

if __name__ == "__main__":
    run_sweeper()