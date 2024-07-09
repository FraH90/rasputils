import os
import importlib.util
import time
import json
from datetime import datetime, timedelta

TASK_FILE_NAME = "task_main.py"
TRIGGER_FILE_NAME = "trigger.json"
LOG_FILE_NAME = "task_scheduler.log"

class Task:
    def __init__(self, task_dir):
        self.task_name = os.path.basename(task_dir)
        self.task_dir = task_dir
        self.task_module = self.import_task_module()
        self.trigger = self.load_trigger()
        self.next_run = self.calculate_next_run()
        self.schedule = self.trigger.get("schedule", {})
        
    def import_task_module(self):
        module_path = os.path.join(self.task_dir, TASK_FILE_NAME)
        spec = importlib.util.spec_from_file_location(self.task_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def load_trigger(self):
        trigger_file = os.path.join(self.task_dir, TRIGGER_FILE_NAME)
        try:
            with open(trigger_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Failed to load trigger file: {e}")
            return {}

    def calculate_next_run(self):
        schedule = self.schedule
        if not schedule.get("enabled", False):
            return None

        now = datetime.now()
        days = schedule.get("days_of_week", [])
        time_of_day = schedule.get("time_of_day", "10:00")

        if "interval" in schedule:
            interval = schedule["interval"]
            return now + timedelta(seconds=interval)

        if not days:
            return None

        try:
            time = datetime.strptime(time_of_day, "%H:%M").time()
            days_ahead = min((datetime.strptime(day, "%A").weekday() - now.weekday()) % 7 for day in days)
            next_run = datetime.combine(now.date() + timedelta(days=days_ahead), time)
            if next_run <= now:
                next_run += timedelta(days=7)
            return next_run
        except Exception as e:
            self.log(f"Failed to calculate next run: {e}")
            return None

    def should_terminate(self):
        terminate_file = os.path.join(self.task_dir, f"{self.task_name}.terminate")
        return os.path.exists(terminate_file)

    def run(self):
        if self.should_terminate():
            self.log(f"Terminating task: {self.task_name}")
            return False

        now = datetime.now()
        if self.next_run and now >= self.next_run:
            self.log(f"Running task: {self.task_name}")
            try:
                self.task_module.main()
            except Exception as e:
                self.log(f"Failed to run task: {e}")
            self.next_run = self.calculate_next_run()

        return True

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE_NAME, "a") as log_file:
            log_file.write(f"[{timestamp}] {message}\n")

def discover_tasks():
    tasks = []
    TASKS_ROOT_DIR = os.path.join(os.getcwd(), "tasks")
    for dir_name in os.listdir(TASKS_ROOT_DIR):
        task_dir = os.path.join(TASKS_ROOT_DIR, dir_name)
        if os.path.isdir(task_dir) and os.path.isfile(os.path.join(task_dir, TASK_FILE_NAME)):
            tasks.append(Task(task_dir))
    return tasks

def main():
    tasks = discover_tasks()
    while tasks:
        tasks = [task for task in tasks if task.run()]
        time.sleep(1)  # Main loop runs every second

if __name__ == '__main__':
    main()
