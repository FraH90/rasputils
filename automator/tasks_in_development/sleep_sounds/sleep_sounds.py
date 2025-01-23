import json
import random
import time
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import subprocess
import os
import sys
from bluetooth_handler import BluetoothHandler

# Those should be retrieved from a credentials.json file later
SPOTIPY_CLIENT_ID = 'your_spotify_client_id'
SPOTIPY_CLIENT_SECRET = 'your_spotify_client_secret'
SPOTIPY_REDIRECT_URI = 'your_spotify_redirect_uri'

class SleepSounds:
    def __init__(self):
        self.load_config()
        self.load_sources()
        self.authenticate_spotify()
        self.connect_bluetooth_speaker()

    def load_config(self):
        with open('config.json') as config_file:
            self.config = json.load(config_file)
        self.stop_time = self.config['stop_time']

    def load_sources(self):
        with open('sources.json') as sources_file:
            self.sources = json.load(sources_file)
        self.playlists = self.sources['playlists']

    def authenticate_spotify(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                            client_secret=SPOTIPY_CLIENT_SECRET,
                                                            redirect_uri=SPOTIPY_REDIRECT_URI,
                                                            scope="user-modify-playback-state,user-read-playback-state"))

    def connect_bluetooth_speaker(self):
        # Connect to the Bluetooth speaker
        bluetooth_mac_address = self.config['bluetooth_mac_address']
        bluetooth_handler = BluetoothHandler(bluetooth_mac_address)
        if bluetooth_handler.connect():
            self.play_playlist()
        else:
            print("Failed to connect to Bluetooth speaker. Exiting.")

    def play_playlist(self):
        playlist_url = random.choice(self.playlists)
        playlist_id = playlist_url.split('/')[-1].split('?')[0]
        devices = self.sp.devices()
        if devices['devices']:
            device_id = devices['devices'][0]['id']
            self.sp.start_playback(device_id=device_id, context_uri=f'spotify:playlist:{playlist_id}')

    def stop_playback(self):
        devices = self.sp.devices()
        if devices['devices']:
            device_id = devices['devices'][0]['id']
            self.sp.pause_playback(device_id=device_id)

    def run(self):
        stop_dt = datetime.strptime(self.stop_time, '%H:%M').replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        if datetime.now() > stop_dt:
            stop_dt += timedelta(days=1)
        
        self.play_playlist()
        time.sleep((stop_dt - datetime.now()).seconds)
        self.stop_playback()


def check_if_already_running():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pid_file = os.path.join(script_dir, 'sleep_sounds.pid')
    if os.path.isfile(pid_file):
        print("Another instance of sleep_sounds is already running.")
        sys.exit()
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

def delete_pid_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pid_file = os.path.join(script_dir, 'sleep_sounds.pid')
    if os.path.isfile(pid_file):
        os.remove(pid_file)

def main():
    check_if_already_running()
    try:
        sleep_sounds = SleepSounds()
        sleep_sounds.run()
    finally:
        delete_pid_file()

if __name__ == "__main__":
    main()