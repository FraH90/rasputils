import json
import os
import subprocess
import sys

def create_service_file(service_name, script_path, working_directory, user):
    service_content = f"""[Unit]
Description={service_name}
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 {script_path}
WorkingDirectory={working_directory}
StandardOutput=inherit
StandardError=inherit
Restart=always
User={user}

[Install]
WantedBy=multi-user.target
"""

    service_file_path = f"/etc/systemd/system/{service_name}.service"
    
    try:
        # Write the service file
        with open(service_file_path, 'w') as service_file:
            service_file.write(service_content)
        print(f"Service file created at {service_file_path}")

        # Reload systemd daemon
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        print("Systemd daemon reloaded")

        # Enable the service to start on boot
        subprocess.run(["sudo", "systemctl", "enable", service_name], check=True)
        print(f"Service {service_name} enabled")

        # Start the service
        subprocess.run(["sudo", "systemctl", "start", service_name], check=True)
        print(f"Service {service_name} started")
    except Exception as e:
        print(f"Failed to create or enable service {service_name}: {e}")

def main():
    # Check if the script is running with sudo/root privileges
    if os.geteuid() != 0:
        print("This script requires sudo/root privileges. Please run the script with 'sudo'.")
        sys.exit(1)

    # Load JSON file
    try:
        with open('services.json', 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        print("The 'services.json' file was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error decoding JSON from 'services.json'.")
        sys.exit(1)

    for service in data['services']:
        service_name = service['service_name']
        script_path = service['script_path']
        working_directory = service['working_directory']
        user = service['user']
        
        create_service_file(service_name, script_path, working_directory, user)

if __name__ == "__main__":
    main()
