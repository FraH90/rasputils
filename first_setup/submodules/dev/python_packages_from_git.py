import os
import subprocess
import shutil
import json

def run_command(command, sudo=False):
    """Run a command with optional sudo."""
    if sudo:
        command = f"sudo {command}"
    result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout

def confirm(prompt):
    """Prompt the user for confirmation."""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ('y', 'n'):
            return response == 'y'
        print("Please respond with 'y' or 'n'.")

def install_module(repo_url, subfolder, destination):
    """Clone a repo, copy a subfolder, and clean up."""

    # Name of the directory of the repo; this is retrieved from the repo_url by getting the name of the last folder
    repo_dir = repo_url.split('/')[-1].replace('.git', '')

    # Clone the repository (not that repo_url must have the .git extension at the end)
    print(f"Cloning the repository from {repo_url}...")
    run_command(f"git clone {repo_url}")

    # Change current directory into the repository directory
    os.chdir(repo_dir)

    # Construct the full destination path. OSS: the "destination" parameter  in json is relative to "/usr/lib/python3/dist-packages"
    destination_path = os.path.join("/usr/lib/python3/dist-packages", destination)

    # Check if the destination directory exists
    if os.path.exists(destination_path):
        response = input(f"Directory {destination_path} already exists. Do you want to remove it and install only the new content? (y/n): ").strip().lower()
        if response == 'y':
            print(f"Removing {destination_path}...")
            run_command(f"rm -rf {destination_path}", sudo=True)
        else:
            print(f"{destination_path} is already present and you chose not to overwrite its content.")
            os.chdir("..")
            shutil.rmtree(repo_dir)
            return

    # Copy the subfolder to the destination directory
    print(f"Copying {subfolder} to {destination_path}...")
    source_path = os.path.abspath(subfolder)
    copy_command = f"cp -r {source_path} {destination_path}"
    run_command(copy_command, sudo=True)


    # Go back to the previous directory
    os.chdir("..")

    # Delete the repository folder
    print(f"Deleting the repository folder {repo_dir}...")
    shutil.rmtree(repo_dir)

    print(f"Module from {repo_url} installed successfully.")

def main():
    # Load configuration from JSON file
    with open('config.json', 'r') as f:
        config_entries = json.load(f)

    for entry in config_entries:
        git_repo = entry.get("git_repo")
        subfolder = entry.get("subfolder")
        destination = entry.get("destination")
        
        if not git_repo or not subfolder or not destination:
            print("Skipping entry due to missing required fields.")
            continue

        install_module(git_repo, subfolder, destination)

if __name__ == "__main__":
    main()
