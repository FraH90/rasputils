import os
import shutil
import subprocess
import sys

def backup_config():
    config_path = os.path.expanduser("~/.config/wayfire.ini")
    backup_path = os.path.expanduser("~/Desktop/wayfire.ini.backup")
    
    if os.path.exists(config_path):
        try:
            shutil.copy(config_path, backup_path)
            print(f'Backed up wayfire configuration to {backup_path}')
            return backup_path  # Return path to backup file
        except Exception as e:
            print(f'Failed to backup wayfire configuration: {str(e)}')
            sys.exit(1)
    else:
        print(f'Wayfire configuration file {config_path} not found.')
        sys.exit(1)

def restore_config():
    config_path = os.path.expanduser("~/.config/wayfire.ini")
    backup_path = os.path.expanduser("~/Desktop/wayfire.ini.backup")

    try:
        shutil.copy(backup_path, config_path)
        print(f'Restored wayfire configuration from {backup_path}')
    except Exception as e:
        print(f'Failed to restore wayfire configuration: {str(e)}')
        sys.exit(1)

def install_dependencies():
    try:
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y'] + dependencies, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Failed to install dependencies: {e}')
        sys.exit(1)

def build_and_install():
    try:
        subprocess.run([
            'sudo', 'git', 'clone', 'https://github.com/WayfireWM/wf-install'
        ], check=True)
        os.chdir('wf-install')
        subprocess.run([
            'sudo', './install.sh', '--prefix', '/opt/wayfire', '--stream', '0.8.x'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Failed to build and install Wayfire: {e}')
        sys.exit(1)

if __name__ == '__main__':
    backup_config()
    
    # Define dependencies list
    dependencies = [
        'git', 'meson', 'python3-pip', 'pkg-config', 'libwayland-dev', 'autoconf',
        'libtool', 'libffi-dev', 'libxml2-dev', 'libegl1-mesa-dev', 'libgles2-mesa-dev',
        'libgbm-dev', 'libinput-dev', 'libxkbcommon-dev', 'libpixman-1-dev', 'xutils-dev',
        'xcb-proto', 'python3-xcbgen', 'libcairo2-dev', 'libglm-dev', 'libjpeg-dev',
        'libgtkmm-3.0-dev', 'xwayland', 'libdrm-dev', 'libgirepository1.0-dev',
        'libsystemd-dev', 'policykit-1', 'libx11-xcb-dev', 'libxcb-xinput-dev',
        'libxcb-composite0-dev', 'xwayland', 'libasound2-dev', 'libpulse-dev',
        'libseat-dev', 'valac', 'libdbusmenu-gtk3-dev', 'libxkbregistry-dev',
        'libdisplay-info-dev', 'hwdata'
    ]
    
    # Ask user to run sudo commands for dependencies and build/install
    print("Please enter your sudo password to continue installation.")
    install_dependencies()
    build_and_install()
    
    # After installation, restore the original config
    restore_config()
