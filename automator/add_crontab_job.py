import subprocess
import os

def add_cron_job(script_path):
    try:
        # Command to list existing cron jobs for the user
        crontab_list = subprocess.check_output(['crontab', '-l'], text=True)
    except subprocess.CalledProcessError:
        # No existing cron jobs
        crontab_list = ''

    # Define the cron job entry
    cron_job = f'@reboot /usr/bin/python3 {script_path}\n'

    # Check if the cron job already exists
    if cron_job in crontab_list:
        print("Cron job already exists.")
        return

    # Add the new cron job entry
    new_crontab = crontab_list + cron_job
    temp_crontab_path = '/tmp/new_crontab'
    
    # Write the updated crontab to a temporary file
    with open(temp_crontab_path, 'w') as f:
        f.write(new_crontab)

    # Install the new crontab
    subprocess.run(['crontab', temp_crontab_path], check=True)
    print("Cron job added successfully.")

    # Clean up the temporary file
    os.remove(temp_crontab_path)
    print("Temporary crontab file removed.")

if __name__ == "__main__":
    # Get the current working directory
    cwd = os.getcwd()
    
    # Build the absolute path to src/main.py
    script_path = os.path.join(cwd, 'src', 'main.py')
    
    # Check if the script file exists
    if not os.path.isfile(script_path):
        print(f"Error: The script file {script_path} does not exist.")
    else:
        add_cron_job(script_path)
