import os
import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(stderr.decode())
    return stdout.decode()

def install_retroarch():
    print("Updating package lists...")
    run_command("sudo apt-get update")

    print("Installing RetroArch...")
    run_command("sudo apt-get install -y retroarch")

def install_selected_cores():
    cores = [
        "libretro-snes9x",
        "libretro-nestopia",
        "libretro-genesis-plus-gx",
        "libretro-mupen64plus-next",
        "libretro-gambatte",
        "libretro-mame",
        "libretro-pcsx-rearmed",
        "libretro-mgba",
        "libretro-stella2014",
        "libretro-bsnes-mercury-balanced"
    ]

    print("Installing RetroArch cores...")
    for core in cores:
        print(f"Installing {core}...")
        run_command(f"sudo apt-get install -y {core}")

def install_all_libretro_cores():
    print("Installing all libretro cores...")
    run_command("sudo apt-get install -y libretro-*")

def configure_retroarch():
    config_file = os.path.expanduser("~/.config/retroarch/retroarch.cfg")
    
    print("Configuring RetroArch...")
    if not os.path.exists(os.path.dirname(config_file)):
        os.makedirs(os.path.dirname(config_file))
    
    # Edit RetroArch configuration file
    with open(config_file, "w") as f:
        f.write("video_fullscreen = true\n")
        f.write("video_scale_integer = true\n")
        f.write("audio_driver = \"alsathread\"\n")
        f.write("input_driver = \"udev\"\n")
        f.write('core_updater_buildbot_url = "http://buildbot.libretro.com/nightly/linux/armhf/latest/"\n')

    # Print additional setup instructions
    print("\nSetup instructions:")
    print("Online Updater -> Update Autoconfig Profiles -> Wait for the OSD text to stop flashing -> Quit and restart RetroArch")
    print("")
    print("If controller is still not found, go to Settings->Input->Input User 1 Binds")
    print("")
    print("Online Updater->Core Updater->2048")
    print("Then from the main menu select Load Core->2048->Start Core")

def main():
    install_retroarch()
    install_all_libretro_cores()
    configure_retroarch()
    print("\nRetroArch installation and setup complete!")

if __name__ == "__main__":
    main()
