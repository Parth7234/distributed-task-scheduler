import heapq
import time

class Task:
    def __init__(self, task_id, priority, description):
        self.task_id = task_id
        # In this design, a lower number means HIGHER priority (e.g., 1 runs before 5)
        self.priority = priority 
        self.description = description
        self.status = "PENDING"

    def __lt__(self, other):
        # This tells heapq how to sort the tasks
        return self.priority < other.priority

    def __repr__(self):
        return f"Task({self.task_id}, Priority: {self.priority}, Status: '{self.status}')"

# 1. Initialize the empty queue
task_queue = []

# 2. Add some dummy tasks (ID, Priority, Description)
heapq.heappush(task_queue, Task(1, 3, "Send welcome email"))
heapq.heappush(task_queue, Task(2, 1, "Process payment")) # Highest priority!
heapq.heappush(task_queue, Task(3, 2, "Generate report"))

print("Tasks submitted. Starting the worker loop...\n")

# 3. The Worker Loop: Pop tasks based on priority and execute them
while task_queue:
    # Pop the task with the lowest priority number
    current_task = heapq.heappop(task_queue)
    
    current_task.status = "RUNNING"
    print(f"Executing: {current_task.description}...")
    
    # Simulate the time it takes to do the work
    time.sleep(1) 
    
    current_task.status = "COMPLETED"
    print(f"Done! {current_task}\n")

print("All tasks completed.")