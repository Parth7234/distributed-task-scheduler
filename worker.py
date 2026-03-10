import os
import time
import datetime
import redis
import database
from database import SessionLocal
import models
import requests
from PIL import Image
from io import BytesIO

# ensure the tasks table exists (in case worker starts before the API)
models.Base.metadata.create_all(bind=database.engine)

# connect to Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# Create a dedicated folder to store the generated thumbnails
os.makedirs("thumbnails", exist_ok=True)

def start_worker():
    print("Worker started. Fetching tasks from the Redis queue...")
    
    while True:
        task_data = redis_client.zpopmin("task_queue", count=1)
        
        if not task_data:
            time.sleep(1)
            continue
            
        task_id_str, priority = task_data[0]
        task_id = int(task_id_str)
        
        print(f"\n[Worker] Grabbed Task ID: {task_id} (Priority: {priority})")
        
        db = SessionLocal()
        try:
            task = db.query(models.Task).filter(models.Task.id == task_id).first()
            
            if task:
                task.status = "RUNNING"
                task.started_at = datetime.datetime.now(datetime.UTC)
                db.commit()
                
                # the task description is the raw image URL
                image_url = task.description.strip() 

                if image_url == "sweeper_testing":
                    print("[Worker] sweeper testing mode")
                    print("[Worker] Sleeping for 15 seconds. CRASH NOW (Ctrl+C)!")
                    time.sleep(15)  
                    task.result = "Failed to crash the worker in time!"
                else:
                    print(f"[Worker] Downloading and compressing image from: '{image_url}'...")
                    
                    # 1. Download the raw image data into memory
                    # We use a custom User-Agent just in case the image host blocks raw Python scripts
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(image_url, headers=headers, timeout=10)
                    
                    if response.status_code != 200:
                        raise ValueError(f"Failed to download image. HTTP Status: {response.status_code}")
                    
                    # 2. Process the image using Pillow and BytesIO
                    # BytesIO tricks Pillow into thinking the raw RAM bytes are a physical file
                    img = Image.open(BytesIO(response.content))
                    
                    # Convert to RGB in case the image is a transparent PNG (JPEG doesn't support transparency)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # 3. Compress and Resize
                    img.thumbnail((128, 128))
                    
                    # 4. Save to the hard drive
                    file_name = f"thumbnails/task_{task_id}.jpg"
                    img.save(file_name, format="JPEG", quality=85)
                    
                    # Save the absolute file path to the database
                    absolute_path = os.path.abspath(file_name)
                    task.result = f"Thumbnail saved to: {absolute_path}"
                
                # mark task as completed
                task.status = "COMPLETED"
                db.commit()
                print(f"[Worker] Successfully finished Task ID: {task_id} -> {task.result}")
            else:
                print(f"[Worker] Error: Task {task_id} not found in database!")

        except Exception as e: 
            if 'task' in locals() and task:
                task.status = "FAILED"
                task.result = f"Error: {str(e)}"
                db.commit()
            print(f"[Worker] Error while executing task {task_id}: {e}")

        finally: 
            db.close()

if __name__ == "__main__":
    start_worker()