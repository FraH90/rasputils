#!/bin/bash

# Remove eventual pre-existing dotnet installations
rm -rf $HOME/.dotnet
sed -i '/export DOTNET_ROOT/d' $HOME/.bashrc
sed -i '/export PATH=.*dotnet/d' $HOME/.bashrc

# Dotnet install (istructions from MS website https://learn.microsoft.com/en-us/dotnet/iot/deployment and https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-install-script)
curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --channel Current

# Add dotnet to environment variables
echo 'export DOTNET_ROOT=$HOME/.dotnet' >> $HOME/.bashrc
echo 'export PATH=$PATH:$HOME/.dotnet' >> $HOME/.bashrc
source $HOME/.bashrc

# Print installed version
dotnet --version
