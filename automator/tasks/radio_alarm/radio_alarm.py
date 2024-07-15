import sys
import json
import random
import time
import vlc
import os
import subprocess

CURRENT_TASK_DIR = os.path.dirname(__file__)

CONFIG_FILE = os.path.join(CURRENT_TASK_DIR, 'config.json')
RADIO_STREAM_FILE = os.path.join(CURRENT_TASK_DIR, 'radio_stations.json')

class BluetoothHandler:
    def __init__(self, mac_address):
        self.mac_address = mac_address

    def run_command(self, command):
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        return process.stdout

    def connect(self):
        print(f"Connecting to Bluetooth speaker with MAC address: {self.mac_address}")
        
        # Turn on the Bluetooth device
        print("Turning on Bluetooth...")
        self.run_command("sudo hciconfig hci0 up")
        
        # Pair with the Bluetooth speaker
        print(f"Pairing with {self.mac_address}...")
        self.run_command(f"echo -e 'pair {self.mac_address}\\n' | sudo bluetoothctl")
        
        # Trust the Bluetooth speaker
        print(f"Trusting {self.mac_address}...")
        self.run_command(f"echo -e 'trust {self.mac_address}\\n' | sudo bluetoothctl")
        
        # Connect to the Bluetooth speaker
        print(f"Connecting to {self.mac_address}...")
        self.run_command(f"echo -e 'connect {self.mac_address}\\n' | sudo bluetoothctl")
        
        # Check if connected
        print("Checking connection status...")
        connection_status = self.run_command(f"echo -e 'info {self.mac_address}\\n' | sudo bluetoothctl")
        
        if "Connected: yes" in connection_status:
            print("Successfully connected to the Bluetooth speaker.")
            return True
        else:
            print("Failed to connect to the Bluetooth speaker.")
            return False

class RadioPlayer:
    def __init__(self):
        self.config = self.load_config()
        self.radio_streams = self.load_radio_streams()
    
    def load_config(self):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)

    def load_radio_streams(self):
        with open(RADIO_STREAM_FILE, 'r') as f:
            return json.load(f)

    def play_radio_for_one_hour(self, stream_url, radio_name):
        player = vlc.MediaPlayer(stream_url)
        player.play()
        print(f"{time.strftime('%H:%M')} - Playing radio {radio_name}")
        # Play for 1 hour (3600 seconds)
        time.sleep(3600)
        # Stop the player
        player.stop()
        print(f"{time.strftime('%H:%M')} - Stopped playing radio {radio_name}")

    def start(self):
        bluetooth_mac_address = self.config['bluetooth_mac_address']
        radio_stream = random.choice(self.radio_streams)
        radio_stream_url = radio_stream['url']
        radio_name = radio_stream['name']

        # Connect to the Bluetooth speaker
        bluetooth_handler = BluetoothHandler(bluetooth_mac_address)
        if bluetooth_handler.connect():
            self.play_radio_for_one_hour(radio_stream_url, radio_name)
        else:
            print("Failed to connect to Bluetooth speaker. Exiting.")

def main():
    radio_player = RadioPlayer()
    radio_player.start()

if __name__ == "__main__":
    main()
