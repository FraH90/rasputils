#!/bin/bash

# Installing python libraries
python python_packages.py

# Networking tools
# SAMBA: info on https://pimylifeup.com/raspberry-pi-samba/
# Pi-Hole. Info on https://pi-hole.net/
sudo apt install samba samba-common-bin
curl -sSL https://install.pi-hole.net | bash

# Developer tools
sudo apt install code

# UI improovements
sudo apt install cairo-dock

# Multimedia
sudo apt-get install mplayer


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