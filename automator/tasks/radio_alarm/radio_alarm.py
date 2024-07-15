import sys
import json
import random
import time
import vlc
import os
import pexpect

CURRENT_TASK_DIR = os.path.dirname(__file__)

CONFIG_FILE = os.path.join(CURRENT_TASK_DIR, 'config.json')
RADIO_STREAM_FILE = os.path.join(CURRENT_TASK_DIR, 'radio_stations.json')

class BluetoothHandler:
    def __init__(self, mac_address):
        self.mac_address = mac_address

    def run_command(self, command, timeout=10):
        process = pexpect.spawn(command, timeout=timeout)
        process.expect(pexpect.EOF)
        return process.before.decode()

    def is_paired(self):
        print(f"Checking if {self.mac_address} is paired...")
        bluetoothctl = pexpect.spawn('sudo bluetoothctl')
        bluetoothctl.sendline(f'info {self.mac_address}')
        try:
            bluetoothctl.expect(['Paired: yes', 'Device has not been found'], timeout=10)
            result = bluetoothctl.after.decode()
            bluetoothctl.sendline('exit')
            return 'Paired: yes' in result
        except pexpect.TIMEOUT:
            bluetoothctl.sendline('exit')
            return False

    def is_connected(self):
        print(f"Checking if {self.mac_address} is connected...")
        bluetoothctl = pexpect.spawn('sudo bluetoothctl')
        bluetoothctl.sendline(f'info {self.mac_address}')
        try:
            bluetoothctl.expect(['Connected: yes', 'Device has not been found'], timeout=10)
            result = bluetoothctl.after.decode()
            bluetoothctl.sendline('exit')
            return 'Connected: yes' in result
        except pexpect.TIMEOUT:
            bluetoothctl.sendline('exit')
            return False

    def connect(self):
        if not self.is_paired():
            print(f"Pairing with {self.mac_address}...")
            bluetoothctl = pexpect.spawn('sudo bluetoothctl')
            bluetoothctl.sendline(f'pair {self.mac_address}')
            bluetoothctl.expect('Pairing successful', timeout=10)
            bluetoothctl.sendline(f'trust {self.mac_address}')
            bluetoothctl.expect('trust succeeded', timeout=10)
            bluetoothctl.sendline('exit')
        else:
            print(f"{self.mac_address} is already paired.")

        if not self.is_connected():
            print(f"Connecting to {self.mac_address}...")
            bluetoothctl = pexpect.spawn('sudo bluetoothctl')
            bluetoothctl.sendline(f'connect {self.mac_address}')
            try:
                bluetoothctl.expect('Connection successful', timeout=10)
                print("Successfully connected to the Bluetooth speaker.")
            except pexpect.TIMEOUT:
                print("Failed to connect to the Bluetooth speaker.")
            bluetoothctl.sendline('exit')

        # Double-check connection status
        if self.is_connected():
            print("Verified: Successfully connected to the Bluetooth speaker.")
            return True
        else:
            print("Failed to verify connection to the Bluetooth speaker.")
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
        # Increase VLC buffer and set audio output to ALSA
        instance = vlc.Instance('--network-caching=3000', '--file-caching=3000', '--live-caching=3000', '--aout=alsa')
        player = instance.media_player_new()
        media = instance.media_new(stream_url)
        player.set_media(media)
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
