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
    chmod 600 ~/.ssh/"$SSH_KEY_NAME"
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
    echo "Add this key to your GitHub account:"
    echo "1. Go to GitHub.com and log in"
    echo "2. Click your profile picture and select 'Settings'"
    echo "3. In the user settings sidebar, click 'SSH and GPG keys'"
    echo "4. Click 'New SSH key' or 'Add SSH key'"
    echo "5. Paste your key into the 'Key' field"
    echo "6. Click 'Add SSH key'"
    read -p "Press Enter when you have added the key to GitHub..."
}

# Function to configure git with SSH
configure_git_ssh() {
    git config --global user.name "$1"
    git config --global user.email "$2"
    git config --global core.sshCommand "ssh -i ~/.ssh/$SSH_KEY_NAME -F /dev/null"
    echo "Git configured to use SSH."
}

# Function to add SSH remote
add_ssh_remote() {
    local repo_path="$1"
    cd "$repo_path" || return
    local current_url=$(git remote get-url origin 2>/dev/null)
    if [[ $current_url == https://github.com/* ]]; then
        local ssh_url=$(echo "$current_url" | sed 's#https://github.com/#git@github.com:#')
        if git remote get-url origin-ssh &>/dev/null; then
            git remote set-url origin-ssh "$ssh_url"
            echo "Updated origin-ssh remote for $repo_path"
        else
            git remote add origin-ssh "$ssh_url"
            echo "Added origin-ssh remote to $repo_path"
        fi
    else
        echo "Skipping $repo_path: not a GitHub HTTPS repository"
    fi
}

# Function to check and warn about existing SSH config
check_ssh_config() {
    if grep -q "Host github.com" ~/.ssh/config; then
        echo "Warning: Existing SSH config found for github.com in ~/.ssh/config"
        echo "This may override the settings we've just configured."
        echo "Please review your ~/.ssh/config file to ensure it doesn't conflict."
    fi
}

# Function to test GitHub SSH connection
test_github_connection() {
    echo "Testing connection to GitHub..."
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "Successfully connected to GitHub!"
    else
        echo "Failed to connect to GitHub. Please check your SSH key and GitHub account settings."
    fi
}

# Main script starts here
echo "Welcome to Git SSH Configuration Script"

# Prompt user if they have an existing SSH key
read -p "Do you already have an existing SSH key? (y/n): " existing_ssh_key
if [ "$existing_ssh_key" == "y" ]; then
    # Prompt for path to existing SSH key
    read -p "Enter the full path to your existing SSH private key (e.g., /home/user/.ssh/id_rsa_github): " ssh_key_path
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
read -p "Enter your Git email address: " git_email
configure_git_ssh "$git_username" "$git_email"

# Check for existing SSH config
check_ssh_config

# Offer to add SSH remotes
read -p "Do you want to add SSH remotes (origin-ssh) to existing repositories? (y/n): " add_ssh_remotes
if [ "$add_ssh_remotes" == "y" ]; then
    read -p "Enter the path to your Git repositories (e.g., /home/user/projects): " repos_path
    for repo in "$repos_path"/*/.git; do
        repo_dir=$(dirname "$repo")
        add_ssh_remote "$repo_dir"
    done
fi

# Test GitHub connection
test_github_connection

echo "Git SSH configuration completed successfully."