#!/bin/bash

# Function to disable Bluetooth permanently
disable_bluetooth_permanently() {
    echo "Disabling internal bluetooth..."
    # Backup existing configuration
    sudo cp /boot/config.txt /boot/config.txt.bak
    # Add the configuration to disable Bluetooth
    echo "dtoverlay=disable-bt" | sudo tee -a /boot/firmware/config.txt
    # Disable Bluetooth service
    sudo systemctl stop bluetooth
    sudo systemctl disable bluetooth
    echo "Bluetooth has been permanently disabled. Please reboot your system for changes to take effect."
}

# Prompt the user
read -p "Do you want to permanently disable the internal Bluetooth on the Raspberry Pi 5? (yes/no): " response
# Convert response to lowercase
response=$(echo "$response" | tr '[:upper:]' '[:lower:]')
# Check the response and act accordingly
if [[ "$response" == "yes" ]]; then
    disable_bluetooth_permanently
else
    echo "Bluetooth remains enabled."
fi