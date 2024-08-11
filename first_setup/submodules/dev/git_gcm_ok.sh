#!/bin/sh

# Halt execution immediately on failure.
set -e

export DOTNET_ROOT=/home/frah/.dotnet
export PATH=$PATH:$DOTNET_ROOT

is_ci=
for i in "$@"; do
    case "$i" in
        -y)
        is_ci=true
        shift # Past argument=value
        ;;
        --install-prefix=*)
        installPrefix="${i#*=}"
        shift # past argument=value
        ;;
    esac
done

# If install-prefix is not passed, use default value
if [ -z "$installPrefix" ]; then
    installPrefix=/usr/local
fi

# Ensure install directory exists
if [ ! -d "$installPrefix" ]; then
    echo "The folder $installPrefix does not exist"
    exit
fi

# In non-ci scenarios, advertise what we will be doing and
# give user the option to exit.
if [ -z $is_ci ]; then
    echo "This script will download, compile, and install Git Credential Manager to:

    $installPrefix/bin

Git Credential Manager is licensed under the MIT License: https://aka.ms/gcm/license"

    while true; do
        read -p "Do you want to continue? [Y/n] " yn
        case $yn in
            [Yy]*|"")
                break
            ;;
            [Nn]*)
                exit
            ;;
            *)
                echo "Please answer yes or no."
            ;;
        esac
    done
fi

install_packages() {
    pkg_manager=$1
    install_verb=$2
    packages=$3

    for package in $packages; do
        # Ensure we don't stomp on existing installations.
        if [ ! -z $(which $package) ]; then
            continue
        fi

        if [ $pkg_manager = apk ]; then
            $sudo_cmd $pkg_manager $install_verb $package
        elif [ $pkg_manager = zypper ]; then
            $sudo_cmd $pkg_manager -n $install_verb $package
        elif [ $pkg_manager = pacman ]; then
            $sudo_cmd $pkg_manager --noconfirm $install_verb $package
        else
            $sudo_cmd $pkg_manager $install_verb $package -y
        fi
    done
}

ensure_dotnet_installed() {
    if [ -z "$(verify_existing_dotnet_installation)" ]; then
        curl -LO https://dot.net/v1/dotnet-install.sh
        chmod +x ./dotnet-install.sh
        bash -c "./dotnet-install.sh --channel 8.0 --arch arm64"

        cd ~
        export DOTNET_ROOT=$(pwd)/.dotnet
        add_to_PATH $DOTNET_ROOT
    fi
}

verify_existing_dotnet_installation() {
    sdks=$(dotnet --list-sdks | grep -oP '^\d+\.\d+')

    supported_dotnet_versions="8.0"
    for v in $supported_dotnet_versions; do
        if echo "$sdks" | grep -q "^$v"; then
            echo "$sdks"
            return 0
        fi
    done

    return 1
}

add_to_PATH () {
    for directory; do
        if [ ! -d "$directory" ]; then
            continue; # Skip nonexistent directory.
        fi
        case ":$PATH:" in
            *":$directory:"*)
                break
            ;;
            *)
                export PATH=$PATH:$directory
            ;;
        esac
    done
}

apt_install() {
    pkg_name=$1

    $sudo_cmd apt update
    $sudo_cmd apt install $pkg_name -y 2>/dev/null
}

print_unsupported_distro() {
    prefix=$1
    distro=$2

    echo "$prefix: $distro is not officially supported by the GCM project."
    echo "See https://gh.io/gcm/linux for details."
}

version_at_least() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$1" ]
}

sudo_cmd=

# If the user isn't root, we need to use `sudo` for certain commands
# (e.g. installing packages).
if [ -z "$sudo_cmd" ]; then
    if [ `id -u` != 0 ]; then
        sudo_cmd=sudo
    fi
fi

# Detect architecture
architecture=$(uname -m)

eval "$(sed -n 's/^ID=/distribution=/p' /etc/os-release)"
eval "$(sed -n 's/^VERSION_ID=/version=/p' /etc/os-release | tr -d '"')"
case "$distribution" in
    debian | ubuntu)
        $sudo_cmd apt update
        install_packages apt install "curl git"

        # ARM-specific packages (if needed)
        if [ "$architecture" = "armv7l" ] || [ "$architecture" = "aarch64" ]; then
            install_packages apt install "libssl-dev libffi-dev"
        fi

        ensure_dotnet_installed
    ;;
    # Other distributions handled similarly, omitted for brevity
    *)
        print_unsupported_distro "ERROR" "$distribution"
        exit
    ;;
esac

# Clone and build
script_path="$(cd "$(dirname "$0")" && pwd)"
toplevel_path="${script_path%/src/linux/Packaging.Linux}"
if [ "z$script_path" = "z$toplevel_path" ] || [ ! -f "$toplevel_path/Git-Credential-Manager.sln" ]; then
    toplevel_path="$PWD/git-credential-manager"
    test -d "$toplevel_path" || git clone https://github.com/git-ecosystem/git-credential-manager
fi

cd "$toplevel_path"
$sudo_cmd env "PATH=$PATH" $DOTNET_ROOT/dotnet build ./src/linux/Packaging.Linux/Packaging.Linux.csproj -c Release -p:InstallFromSource=true -p:installPrefix=$installPrefix
add_to_PATH "$installPrefix/bin"
