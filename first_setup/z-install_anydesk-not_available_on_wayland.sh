#!/bin/bash

# Function to download the latest AnyDesk version
download_anydesk() {
    echo "Downloading the latest AnyDesk version..."
    # Get the latest AnyDesk download URL
    URL=$(curl -s https://anydesk.com/en/downloads/raspberry-pi | grep -oP '(?<=href=")[^"]*anydesk.*.deb(?=")' | head -1)
    
    if [ -z "$URL" ]; then
        echo "Failed to find the download URL."
        exit 1
    fi

    # Download the .deb file
    wget -O anydesk.deb "$URL"

    if [ $? -ne 0 ]; then
        echo "Failed to download AnyDesk."
        exit 1
    fi
}

# Function to add the armhf architecture and install required dependencies
install_dependencies() {
    echo "Adding armhf architecture and installing required dependencies..."
    sudo dpkg --add-architecture armhf

    sudo apt update
    sudo apt install -y libpolkit-gobject-1-0:armhf libraspberrypi0:armhf libraspberrypi-dev:armhf libraspberrypi-bin:armhf libgles-dev:armhf libegl-dev:armhf

    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies."
        exit 1
    fi

    # Create symbolic links
    sudo ln -sf /usr/lib/arm-linux-gnueabihf/libGLESv2.so /usr/lib/libbrcmGLESv2.so
    sudo ln -sf /usr/lib/arm-linux-gnueabihf/libEGL.so /usr/lib/libbrcmEGL.so
}

# Function to install AnyDesk
install_anydesk() {
    echo "Installing AnyDesk..."
    sudo dpkg -i anydesk.deb

    # Fix any dependency issues
    sudo apt-get install -f -y

    if [ $? -ne 0 ]; then
        echo "Failed to install AnyDesk."
        exit 1
    fi
}

# Function to clean up
cleanup() {
    echo "Cleaning up..."
    rm anydesk.deb
}

# Execute the functions
download_anydesk
install_dependencies
install_anydesk
cleanup

echo "AnyDesk installation completed successfully."
