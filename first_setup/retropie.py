#!/usr/bin/env python3

import os
import subprocess
import time

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(stderr.decode())
    return stdout.decode()

def install_retropie():
    print("Updating system...")
    run_command("sudo apt update && sudo apt upgrade -y")

    print("Installing dependencies...")
    run_command("sudo apt install -y git lsb-release")

    print("Downloading RetroPie setup script...")
    run_command("git clone --depth=1 https://github.com/RetroPie/RetroPie-Setup.git")

    print("Running RetroPie setup script...")
    os.chdir("RetroPie-Setup")
    
    # Run the basic install non-interactively
    run_command("sudo ./retropie_setup.sh basic_install")

    print("Setting up EmulationStation to start on boot...")
    autostart_file = "/opt/retropie/configs/all/autostart.sh"
    with open(autostart_file, "w") as f:
        f.write("emulationstation #auto")

    print("Creating desktop shortcut...")
    desktop_file = os.path.expanduser("~/Desktop/retropie.desktop")
    with open(desktop_file, "w") as f:
        f.write("[Desktop Entry]\n")
        f.write("Name=RetroPie\n")
        f.write("Exec=emulationstation\n")
        f.write("Type=Application\n")
        f.write("Terminal=false\n")
        f.write("Icon=/opt/retropie/supplementary/emulationstation/resources/icon_empty.png\n")

    print("Setting permissions for desktop shortcut...")
    run_command(f"chmod +x {desktop_file}")

def configure_controllers():
    print("Please connect your game controllers now.")
    time.sleep(5)  # Give user time to connect controllers
    print("Running controller configuration...")
    run_command("emulationstation")

def main():
    if os.geteuid() != 0:
        print("This script must be run as root. Please use sudo.")
        return

    install_retropie()
    print("RetroPie installation complete!")
    print("Now configuring controllers...")
    configure_controllers()
    print("Setup complete! You can now start RetroPie from the desktop shortcut or by running 'emulationstation'")

if __name__ == "__main__":
    main()