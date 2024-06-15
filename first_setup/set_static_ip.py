import subprocess

# This script gets the gateway (IP of the router) and the current IP of the raspberry PI, and sets
# the IP of the device to the one assigned in the beginning (static IP, it won't change again)

# Get the current IP configuration
with subprocess.Popen(['ip', 'route'], stdout=subprocess.PIPE) as p:
    output = p.stdout.read().decode('utf-8')
    lines = output.split('\n')

# Extract the default gateway (router IP) and the IP address of the Raspberry Pi
router_ip = None
pi_ip = None
for line in lines:
    if line.startswith('default'):
        router_ip = line.split()[2]
    if 'src' in line:
        pi_ip = line.split()[2]

# Update the IP configuration
if router_ip and pi_ip:
    subprocess.run(['ip', 'route', 'add', 'default', 'via', router_ip, 'src', pi_ip], shell=True)
