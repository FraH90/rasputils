import os
import importlib.util
import time
import json
from datetime import datetime, timedelta

TASKS_ROOT_DIR = os.path.join(os.getcwd(), "tasks")

class Task:
    def __init__(self, task_dir):
        self.task_name = os.path.basename(task_dir)
        self.task_dir = task_dir
        self.task_module = self.import_task_module()
        self.config = self.load_config()
        self.next_run = self.calculate_next_run()

    def import_task_module(self):
        module_path = os.path.join(self.task_dir, "task_main.py")
        spec = importlib.util.spec_from_file_location(self.task_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def load_config(self):
        config_file = os.path.join(self.task_dir, "trigger.json")
        with open(config_file, 'r') as f:
            return json.load(f)

    def calculate_next_run(self):
        schedule = self.config.get("schedule", {})
        if not schedule.get("enabled", False):
            return None

        now = datetime.now()
        days = schedule.get("days_of_week", [])
        time = datetime.strptime(schedule.get("time_of_day", "00:00"), "%H:%M").time()

        if not days:
            return None

        days_ahead = min((datetime.strptime(day, "%A").weekday() - now.weekday()) % 7 for day in days)
        next_run = datetime.combine(now.date() + timedelta(days=days_ahead), time)
        if next_run <= now:
            next_run += timedelta(days=7)

        return next_run

    def should_terminate(self):
        terminate_file = os.path.join(self.task_dir, f"{self.task_name}.terminate")
        return os.path.exists(terminate_file)

    def run(self):
        if self.should_terminate():
            print(f"Terminating task: {self.task_name}")
            return False

        now = datetime.now()
        if self.next_run and now >= self.next_run:
            self.task_module.main()
            self.next_run = self.calculate_next_run()
        
        return True

def discover_tasks():
    tasks = []
    for dir_name in os.listdir(TASKS_ROOT_DIR):
        task_dir = os.path.join(TASKS_ROOT_DIR, dir_name)
        if os.path.isdir(task_dir) and os.path.isfile(os.path.join(task_dir, "task_main.py")):
            tasks.append(Task(task_dir))
    return tasks

def main():
    tasks = discover_tasks()
    while tasks:
        tasks = [task for task in tasks if task.run()]
        time.sleep(1)  # Main loop runs every second

if __name__ == '__main__':
    main()