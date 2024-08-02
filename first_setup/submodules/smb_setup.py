import os

# Define the configuration details
samba_conf = """
[shared]
path = /home/pi/shared
browseable = yes
writable = yes
only guest = no
create mask = 0777
directory mask = 0777
public = yes
"""

def run_command(command):
    """Run a shell command and print its output."""
    print(f"Running command: {command}")
    os.system(command)

def install_samba():
    """Install Samba and its common binaries."""
    run_command("sudo apt-get update")
    run_command("sudo apt-get install -y samba samba-common-bin")

def configure_samba():
    """Configure Samba by updating the smb.conf file."""
    # Write the Samba configuration to smb.conf
    with open('/etc/samba/smb.conf', 'a') as conf_file:
        conf_file.write(samba_conf)
    
    print("Samba configuration updated.")

def create_shared_directory():
    """Create and set permissions for the shared directory."""
    run_command("mkdir -p /home/pi/shared")
    run_command("chmod 777 /home/pi/shared")
    print("Shared directory created and permissions set.")

def restart_samba():
    """Restart the Samba service."""
    run_command("sudo systemctl restart smbd")
    print("Samba service restarted.")

def print_windows_instructions(ip_address):
    """Print instructions for accessing the Samba share from Windows."""
    instructions = f"""
    To access the shared directory from Windows:

    1. Open File Explorer.
    2. In the address bar, type: \\\\{ip_address}\\shared
    3. Press Enter.
    4. You should see the 'shared' directory listed.
    5. Drag and drop files into this directory to transfer them to your Raspberry Pi.

    If you are prompted for credentials, use the following:
        - Username: pi
        - Password: (Your Raspberry Pi password)

    Ensure that your Raspberry Pi and Windows PC are on the same network.
    """
    print(instructions)

def main():
    """Main function to run all steps."""
    install_samba()
    configure_samba()
    create_shared_directory()
    restart_samba()
    
    # Replace with your Raspberry Pi's IP address
    ip_address = input("Enter your Raspberry Pi's IP address: ")
    
    print("Samba setup completed.")
    print_windows_instructions(ip_address)

if __name__ == "__main__":
    main()
