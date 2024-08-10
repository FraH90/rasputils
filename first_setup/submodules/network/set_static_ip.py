import subprocess
import re
import sys
import os

# Function to execute shell commands and print their output for debugging
def run_command(command):
    print(f"Executing command: {' '.join(command)}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error executing command: {' '.join(command)}")
        print(result.stderr.decode('utf-8'))
        return False
    else:
        print(result.stdout.decode('utf-8'))
        return True

# Function to prompt user for valid static IP address
def get_valid_static_ip():
    while True:
        static_ip = input("Enter the static IP address (e.g., 192.168.1.100): ").strip()
        # Validate IP address using regex
        if re.match(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$', static_ip):
            return static_ip
        else:
            print("Invalid IP address format. Please enter a valid IP address.")

# Function to retrieve current IP configuration and extract router_ip and pi_ip
def get_ip_configuration():
    with subprocess.Popen(['ip', 'route'], stdout=subprocess.PIPE) as p:
        output = p.stdout.read().decode('utf-8')
        lines = output.split('\n')

    router_ip = None
    pi_ip = None
    for line in lines:
        if line.startswith('default'):
            router_ip = line.split()[2]
        if 'src' in line:
            pi_ip = line.split()[2]

    return router_ip, pi_ip

# Function to write static IP configuration to dhcpcd.conf
def write_dhcpcd_config(static_ip, router_ip):
    dhcpcd_conf_lines = [
        f'interface wlan0',
        f'static ip_address={static_ip}/24',
        f'static routers={router_ip}',
        f'static domain_name_servers=8.8.8.8 8.8.4.4'
    ]

    try:
        with open('/etc/dhcpcd.conf', 'a') as f:
            f.write('\n'.join(dhcpcd_conf_lines) + '\n')
        print("Added static IP configuration to /etc/dhcpcd.conf successfully.")
        return True
    except IOError as e:
        print(f"Error writing to /etc/dhcpcd.conf: {str(e)}")
        return False

# Function to execute commands to apply static IP configuration
def execute_commands(static_ip, router_ip):
    commands = [
        ['sudo', 'ip', 'addr', 'flush', 'dev', 'wlan0'],
        ['sudo', 'ip', 'addr', 'add', f"{static_ip}/24", 'dev', 'wlan0'],
        ['sudo', 'ip', 'link', 'set', 'wlan0', 'up'],
        ['sudo', 'ip', 'route', 'add', 'default', 'via', router_ip]
    ]

    for command in commands:
        if not run_command(command):
            return False

    print(f"Static IP {static_ip} configured successfully.")
    return True

if __name__ == "__main__":
    # Check sudo permissions
    if os.geteuid() != 0:
        print("This script requires sudo permissions to modify network configuration.")
        sys.exit(1)

    # Retrieve current IP configuration
    router_ip, pi_ip = get_ip_configuration()

    # Check if we successfully retrieved necessary IP addresses
    if router_ip and pi_ip:
        # Get a valid static IP address from user input
        static_ip = get_valid_static_ip()

        # Write static IP configuration to dhcpcd.conf
        if write_dhcpcd_config(static_ip, router_ip):
            # Execute commands to apply static IP configuration
            execute_commands(static_ip, router_ip)
        else:
            print("Failed to write static IP configuration to /etc/dhcpcd.conf.")
    else:
        print("Failed to retrieve necessary IP addresses (router IP or Raspberry Pi IP).")
