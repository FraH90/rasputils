#!/bin/bash

# Installing python libraries
python python_packages.py

# Installing retroarch
# sudo python retroarch_setup.python
# Do this via PiKiss, more straightfoward and no errors

# Networking tools
# SAMBA: info on https://pimylifeup.com/raspberry-pi-samba/
# Pi-Hole. Info on https://pi-hole.net/
sudo apt install samba samba-common-bin
curl -sSL https://install.pi-hole.net | bash
# PiKiss
curl -sSL https://git.io/JfAPE | bash

# Developer tools
sudo apt install code

# UI improovements. Doesnt work because of wayland incompatibility
# sudo apt install cairo-dock-core
# sudo apt install cairo-dock-plug-ins

# Multimedia
sudo apt-get install mplayer

# Utilities
# Pi-Apps
wget -qO- https://raw.githubusercontent.com/Botspot/pi-apps/master/install | bash

############################################################
######### Software not installed for the moment ############
############################################################
# Install docker
# curl -sSL https://get.docker.com | sh

# Install Docker Composer
# sudo apt-get install -y libffi-dev libssl-dev
# sudo pip3 install docker-compose

# Other software to look in the future
# DNSCrypt, Privoxy

sleep 100