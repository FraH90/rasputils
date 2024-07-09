#!/bin/bash

# Set the desired SSH key file name here
SSH_KEY_NAME="id_rsa_github"

# Function to display messages in bold
bold=$(tput bold)
normal=$(tput sgr0)

# Check if ssh-keygen is installed
if ! command -v ssh-keygen &> /dev/null; then
    echo "${bold}ssh-keygen${normal} is not installed. Please install OpenSSH package."
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "${bold}git${normal} is not installed. Please install Git."
    exit 1
fi

# Function to generate SSH key
generate_ssh_key() {
    echo "Generating SSH key pair..."
    ssh-keygen -t rsa -b 4096 -C "$1" -f ~/.ssh/"$SSH_KEY_NAME"
    if [ $? -ne 0 ]; then
        echo "Error: SSH key generation failed."
        exit 1
    fi
}

# Function to add SSH key to ssh-agent
add_ssh_key_to_agent() {
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/"$SSH_KEY_NAME"
}

# Function to prompt user to copy SSH key to clipboard
prompt_copy_to_clipboard() {
    echo "Your SSH public key has been generated. Please copy the following key:"
    echo
    cat ~/.ssh/"$SSH_KEY_NAME".pub
    echo
    echo "Add this key to your Git hosting service (e.g., GitHub, GitLab)."
    read -p "Press Enter to continue..."
}

# Function to configure git with SSH
configure_git_ssh() {
    git config --global user.name "$1"
    git config --global user.email "$2"
    git config --global core.sshCommand "ssh -i ~/.ssh/$SSH_KEY_NAME -F /dev/null"
    echo "Git configured to use SSH."
}

# Main script starts here

echo "Welcome to Git SSH Configuration Script"

# Prompt user if they have an existing SSH key
read -p "Do you already have an existing SSH key? (y/n): " existing_ssh_key

if [ "$existing_ssh_key" == "y" ]; then
    # Prompt for path to existing SSH key
    read -p "Enter the full path to your existing SSH private key (e.g., /home/user/.ssh/$SSH_KEY_NAME): " ssh_key_path
    if [ ! -f "$ssh_key_path" ]; then
        echo "Error: SSH private key not found at $ssh_key_path"
        exit 1
    fi
    # Copy existing key to default location (~/.ssh/$SSH_KEY_NAME)
    cp "$ssh_key_path" ~/.ssh/"$SSH_KEY_NAME"
    chmod 600 ~/.ssh/"$SSH_KEY_NAME"
else
    # Generate new SSH key pair
    read -p "Enter your Git email address: " git_email
    generate_ssh_key "$git_email"
fi

# Add SSH key to ssh-agent
add_ssh_key_to_agent

# Prompt user to copy SSH key to clipboard if generating new key
if [ "$existing_ssh_key" != "y" ]; then
    prompt_copy_to_clipboard
fi

# Configure git with SSH
read -p "Enter your Git username: " git_username
configure_git_ssh "$git_username" "$git_email"

echo "Git SSH configuration completed successfully."
