import glob
import os
import pyRTOS
import time
from task import Task

class Orchestrator:
    # Future idea: insert in the orchestrator object the list of all the tasks (as objects) present in the folder
    def __init__(self, tasks_root_folder):
        self.tasks_root_folder = tasks_root_folder
        self.task_files = self.discover_task_files()
        pass

    # Get a list of all task scripts in the current directory and subdirectories
    def discover_task_files(self):
        task_files = []
        for root, dirs, files in os.walk(self.tasks_root_folder):
            for dir_name in dirs:
                task_file = os.path.join(root, dir_name, f"{dir_name}.py")
                if os.path.isfile(task_file):
                    task_files.append(task_file)
        return task_files
    
    def run(self):
        # Delete all the .terminate files in this folder (otherwise tasks won't start)
        terminate_list = glob.glob("*.terminate")
        for terminate_item in terminate_list:
            os.remove(terminate_item)
        # Import and add tasks to pyRTOS
        for task_file in self.task_files:
            task_instance = Task(task_file)
            pyRTOS.add_task(pyRTOS.Task(task_instance.run, name=task_instance.task_name))
        # Add a service routine to slow down the execution
        pyRTOS.add_service_routine(lambda: time.sleep(0.1))
        # Start pyRTOS
        pyRTOS.start()

    def run_task_debug(self, task_name):
        """Run a specific task in debug mode"""
        # Find the task file
        task_file = None
        for root, dirs, files in os.walk(self.tasks_root_folder):
            for dir_name in dirs:
                if dir_name == task_name:
                    task_file = os.path.join(root, dir_name, f"{dir_name}.py")
                    break
            if task_file:
                break

        if not task_file:
            raise ValueError(f"Task {task_name} not found")

        # Create and run the task in debug mode
        task_instance = Task(task_file, debug=True)
        pyRTOS.add_task(pyRTOS.Task(task_instance.run, name=task_instance.task_name))
        pyRTOS.add_service_routine(lambda: time.sleep(0.1))
        pyRTOS.start()