import os
import sys

def add_to_bashrc(shell_script_path, output_path):
    bashrc_path = os.path.expanduser("~/.bashrc")
    entry = f"\n# Run shell script at startup\n(nohup {shell_script_path} > {output_path} 2>&1 &)\n"
    
    with open(bashrc_path, "a") as bashrc:
        bashrc.write(entry)

def find_sh_files():
    return [f for f in os.listdir() if f.endswith('.sh')]

def prompt_for_script_choice(scripts):
    print("Multiple .sh files found:")
    for idx, script in enumerate(scripts, start=1):
        print(f"{idx}. {script}")
    choice = input(f"Enter the number of the script you want to install (1-{len(scripts)}): ")
    
    try:
        choice = int(choice)
        if 1 <= choice <= len(scripts):
            return scripts[choice - 1]
        else:
            print("Invalid choice. Please run the script again and select a valid option.")
            sys.exit(1)
    except ValueError:
        print("Invalid input. Please enter a number.")
        sys.exit(1)

def main():
    sh_files = find_sh_files()

    if sh_files:
        if len(sh_files) == 1:
            selected_script = sh_files[0]
        else:
            selected_script = prompt_for_script_choice(sh_files)
    else:
        print("No .sh files found in the current directory.")
        input_choice = input("Would you like to provide the absolute or relative path to the script? (a/r): ").strip().lower()
        
        if input_choice == 'a':
            selected_script = input("Enter the absolute path to the shell script: ").strip()
        elif input_choice == 'r':
            selected_script = input("Enter the relative path to the shell script: ").strip()
        else:
            print("Invalid option. Please run the script again and select a valid option.")
            sys.exit(1)

    absolute_path = os.path.abspath(selected_script)
    script_dir = os.path.dirname(absolute_path)

    if not os.path.exists(absolute_path):
        print(f"Error: The file {absolute_path} does not exist.")
        sys.exit(1)

    if not os.access(absolute_path, os.X_OK):
        print(f"Warning: The script {absolute_path} is not executable. Attempting to make it executable...")
        try:
            os.chmod(absolute_path, 0o755)
            print("Successfully made the script executable.")
        except OSError:
            print(f"Error: Unable to make {absolute_path} executable. Please check file permissions.")
            sys.exit(1)

    # Create logs directory and set output path
    logs_dir = os.path.join(script_dir, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    output_path = os.path.join(logs_dir, "output.out")

    add_to_bashrc(absolute_path, output_path)
    print(f"Installation complete. The script {absolute_path} will run at startup.")
    print(f"Output will be written to {output_path}")

if __name__ == "__main__":
    main()
