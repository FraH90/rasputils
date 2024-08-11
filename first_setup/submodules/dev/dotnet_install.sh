#!/bin/bash

# Dotnet install (istructions from MS website https://learn.microsoft.com/en-us/dotnet/iot/deployment)
curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --channel STS

echo 'export DOTNET_ROOT=$HOME/.dotnet' >> $HOME/.bashrc
echo 'export PATH=$PATH:$HOME/.dotnet' >> $HOME/.bashrc
source $HOME/.bashrc

dotnet --version
