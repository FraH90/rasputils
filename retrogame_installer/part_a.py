#!/usr/bin/env python3

import os
import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(stderr.decode())
    return stdout.decode()

def configure_locale():
    print("Configuring locale settings...")
    run_command("sudo raspi-config nonint do_change_locale en_US.UTF-8")
    run_command("sudo raspi-config nonint do_change_timezone Europe/Rome")
    run_command("sudo raspi-config nonint do_configure_keyboard it")
    run_command("sudo raspi-config nonint do_wifi_country IT")
    run_command("sudo update-locale LANGUAGE=\"en_US:en\"")
    run_command("sudo update-locale LC_ALL=en_US.UTF-8")
    
    print("Scheduling the second part of the script to run after reboot...")
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    cron_job = f"@reboot /usr/bin/python3 {script_dir}/part2_install_retropie.py"
    with open("/etc/cron.d/retropie_setup", "w") as f:
        f.write(cron_job + "\n")
    
    print("Rebooting to apply locale settings...")
    run_command("sudo reboot")

def main():
    if os.geteuid() != 0:
        print("This script must be run as root. Please use sudo.")
        return

    configure_locale()

if __name__ == "__main__":
    main()
