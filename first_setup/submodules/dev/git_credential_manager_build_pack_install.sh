#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Clone GCM repository
git clone https://github.com/GitCredentialManager/git-credential-manager.git
cd git-credential-manager

# Modify architecture to linux-arm64
sed -i 's/RUNTIME=linux-x64/RUNTIME=linux-arm64/' src/linux/Packaging.Linux/layout.sh

# Build Git Credential Manager into a deb package
src/linux/Packaging.Linux/layout.sh
src/linux/Packaging.Linux/pack.sh --version=2.5.1 --payload=out/linux/Packaging.Linux/Debug/payload/ --symbols=out/linux/Packaging.Linux/Debug/payload.sym

# Install from the deb package
sudo dpkg -i out/linux/Packaging.Linux/Debug/deb/gcm-linux_arm64.2.5.1.deb

# Configure git to work with git credential manager as default credential helper
git-credential-manager configure
git config --global credential.credentialStore secretservice

# Configure for specific services (GitHub, Azure, BitBucket)
git config --global credential.https://github.com.useHttpPath true
git config --global credential.https://dev.azure.com.useHttpPath true
git config --global credential.https://bitbucket.org.useHttpPath true
