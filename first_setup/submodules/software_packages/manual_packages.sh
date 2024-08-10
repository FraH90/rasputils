#!/bin/bash

# Installing python libraries
python ./submodules/dev/python_packages.py

# Installing retroarch:
# Do this via PiKiss, more straightfoward and no errors


# Pi-Hole. Info on https://pi-hole.net/
curl -sSL https://install.pi-hole.net | bash
# PiKiss
curl -sSL https://git.io/JfAPE | bash

# Utilities
# Pi-Apps
wget -qO- https://raw.githubusercontent.com/Botspot/pi-apps/master/install | bash

# Dev
# NvChad (customization package for NeoVim). Make sure to install this after neovim
git clone https://github.com/NvChad/NvChad ~/.config/nvim --depth 1 && nvim
# OhMyZSH (customization package for ZSH shell)
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"


sleep 100


############################################################
######### Software not installed for the moment ############
############################################################
# Install docker
# curl -sSL https://get.docker.com | sh

# Install Docker Composer
# sudo apt install -y libffi-dev libssl-dev
# sudo pip3 install docker-compose

# Other software to look in the future
# DNSCrypt, Privoxy