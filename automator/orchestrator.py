import glob
import os
import importlib.util
import pyRTOS
import time
from datetime import datetime, timedelta

class Task:
    def __init__(self, task_file):
        # Initialize the task by setting the task name and importing the task module
        self.task_name = os.path.dirname(task_file)
        self.task_module = self.import_task_module(task_file)
        self.schedule = None
        self.task_timeout = None
        self.next_run = None

    def import_task_module(self, module_path):
        # Dynamically import the task module from the given path
        module_name = os.path.basename(module_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def next_run_time(self, schedule):
        # Calculate the next run time based on the schedule
        now = datetime.now()
        if not schedule["enabled"]:
            return None

        days_of_week = schedule["days_of_week"]
        time_of_day = datetime.strptime(schedule["time_of_day"], "%H:%M").time()

        days_ahead = min(
            (day - now.weekday()) % 7
            for day in [datetime.strptime(day, "%A").weekday() for day in days_of_week]
        )

        next_run = datetime.combine(now + timedelta(days=days_ahead), time_of_day)
        if next_run < now:
            next_run += timedelta(days=7)

        return next_run

    def setup(self):
        # Execute the setup function of the task module to initialize the task
        # The timeout of each specific task and the schedule are returned by the setup function
        self.task_timeout, self.schedule = self.task_module.setup()
        self.next_run = self.next_run_time(self.schedule)

    def run(self, self_task):
        self.setup()
        yield
        while True:
            now = datetime.now()
            if self.schedule["enabled"] and self.next_run and now < self.next_run:
                # If scheduling is enabled, sleep until the next run time
                sleep_time = (self.next_run - now).total_seconds()
                yield [pyRTOS.timeout(sleep_time)]
            else:
                # Execute the main thread of the task, with the appropriate timeout
                self.task_module.thread_loop()
                if self.schedule["enabled"]:
                    self.next_run = self.next_run_time(self.schedule)
                yield [pyRTOS.timeout(self.task_timeout)]

            # If the "all.terminate" file exists in the root folder, terminate the task
            # This should be true even if the $name_task.terminate file is found in the root folder
            # where $name_task is the name of the folder containing the task.py file
            if os.path.exists('all.terminate') or os.path.exists(f'{self.task_name}.terminate'):
                return

class Orchestrator:
    # Future idea: insert in the orchestrator object the list of all the tasks (as objects) present in the folder
    def __init__(self):
        pass

    def run(self):
        # Delete all the .terminate files in this folder (otherwise tasks won't start)
        terminate_list = glob.glob("*.terminate")
        for terminate_item in terminate_list:
            os.remove(terminate_item)

        # Get a list of all task scripts in the current directory and subdirectories
        task_files = []
        for root, dirs, files in os.walk("."):
            # Scan through directories
            for dir_name in dirs:
                # Hypothesis: task_file exists inside a the subfolder, with the same name of subfolder itself
                task_file = os.path.join(root, dir_name, f"{dir_name}.py")
                # Look if the task_file exists (and is a file)
                if os.path.isfile(task_file):
                    task_files.append(task_file)

        # Import and add tasks to pyRTOS
        for task_file in task_files:
            task_instance = Task(task_file)
            pyRTOS.add_task(pyRTOS.Task(task_instance.run, name=os.path.basename(task_file).replace(".py", "")))

        # Add a service routine to slow down the execution
        pyRTOS.add_service_routine(lambda: time.sleep(0.1))

        # Start pyRTOS
        pyRTOS.start()


def main():
    orchestrator = Orchestrator()
    orchestrator.run()


if __name__ == '__main__':
    main()
