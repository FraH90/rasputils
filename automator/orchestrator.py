import glob
import os
import importlib.util
import pyRTOS
import time
from datetime import datetime, timedelta


def import_task_module(module_path):
    module_name = os.path.basename(module_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def next_run_time(schedule):
    now = datetime.now()
    if not schedule["enabled"]:
        return None

    days_of_week = schedule["days_of_week"]
    time_of_day = datetime.strptime(schedule["time_of_day"], "%H:%M").time()

    # Calculate the next run time based on the schedule
    days_ahead = min(
        (day - now.weekday()) % 7
        for day in [datetime.strptime(day, "%A").weekday() for day in days_of_week]
    )

    next_run = datetime.combine(now + timedelta(days=days_ahead), time_of_day)
    if next_run < now:
        next_run += timedelta(days=7)

    return next_run


def create_task(task_module, task_name):
    def task(self):
        # The timeout of each specific task is returned by the setup function
        # This obviously also executes the setup function, with all the setup code inside it
        task_timeout, schedule = task_module.setup()
        next_run = next_run_time(schedule)
        yield
        while True:
            now = datetime.now()
            if schedule["enabled"] and next_run and now < next_run:
                # If scheduling is enabled, sleep until the next run time
                sleep_time = (next_run - now).total_seconds()
                yield [pyRTOS.timeout(sleep_time)]
            else:
                # Execute the main thread of the task, with the appropriate timeout (if schedule not enabled)
                task_module.thread_loop()
                if schedule["enabled"]:
                    next_run = next_run_time(schedule)
                yield [pyRTOS.timeout(task_timeout)]
            # Execute the main thread of the task, with the appropriate timeout

            # If the "all.terminate" file exists in the root folder, terminate the task
            # This should be true even if the $name_task.terminate is found into the root folder
            # where $name_task is the name of the folder containing the task.py file
            if os.path.exists('all.terminate') or os.path.exists(f'{task_name}.terminate'):
                return
    return task


def main():
    # Delete all the .terminate files in this folder (otherwise tasks won't start)
    terminate_list = glob.glob("*.terminate")
    for terminate_item in terminate_list:
        os.remove(terminate_item)

    # Get a list of all task scripts in the current directory and subdirectories
    task_files = glob.glob("**/task.py", recursive=True)

    # Import and add tasks to pyRTOS
    for task_file in task_files:
        task_module = import_task_module(task_file)
        task_name = os.path.dirname(task_file)
        task_func = create_task(task_module, task_name)
        pyRTOS.add_task(pyRTOS.Task(task_func, name=os.path.basename(task_file).replace(".py", "")))

    # Add a service routine to slow down the execution
    pyRTOS.add_service_routine(lambda: time.sleep(0.1))
    
    # Start pyRTOS
    pyRTOS.start()

if __name__ == '__main__':
    main()
