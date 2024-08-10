#!/bin/bash

# Multimedia
sudo apt install mplayer

# Developer tools
sudo apt install code
sudo apt -y install zsh
sudo apt -y install neovim

# Networking tools
# SAMBA: info on https://pimylifeup.com/raspberry-pi-samba/
sudo apt install samba samba-common-bin


# UI improovements
# CairoDock - Doesnt work because of wayland incompatibility
# sudo apt install cairo-dock-core
# sudo apt install cairo-dock-plug-ins


sleep 100