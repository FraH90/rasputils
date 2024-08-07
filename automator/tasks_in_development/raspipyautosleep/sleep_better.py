import bluetooth
import pygame
import schedule
import time
from datetime import datetime, timedelta

DEVICE_ADDRESS = '00:11:22:33:44:55'  # Replace with your Bluetooth device address
AUDIO_FILE = 'your_audio_file.mp3'  # Replace with your audio file path
PLAY_DURATION_HOURS = 2  # Number of hours to play the audio
SCHEDULE_TIME = "15:30"  # Time to start the task in HH:MM format

def check_bluetooth_device(address):
    nearby_devices = bluetooth.discover_devices()
    return address in nearby_devices

def connect_bluetooth_device(address):
    # This function will attempt to connect to the Bluetooth device
    # The actual implementation of connecting to a Bluetooth audio device may vary
    # Here we simply simulate the connection process
    try:
        # You would typically use a library specific to your Bluetooth stack
        # For example, using pybluez for Bluetooth connections
        print(f"Trying to connect to {address}...")
        # Assume connection is successful
        return True
    except Exception as e:
        print(f"Failed to connect to the device: {e}")
        return False

def play_audio_in_loop(audio_file, duration_hours):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play(loops=-1)  # Play the audio in a loop

    end_time = datetime.now() + timedelta(hours=duration_hours)
    while datetime.now() < end_time:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(loops=-1)
        time.sleep(1)  # Check every second

    pygame.mixer.music.stop()
    pygame.mixer.quit()
    print("Audio playback finished")

def job():
    print(f"Job started at {datetime.now()}")
    if check_bluetooth_device(DEVICE_ADDRESS) or connect_bluetooth_device(DEVICE_ADDRESS):
        play_audio_in_loop(AUDIO_FILE, PLAY_DURATION_HOURS)
    else:
        print("Failed to connect to the Bluetooth device.")
    print("Job finished")

# Schedule the job every day at a specific time
schedule.every().day.at(SCHEDULE_TIME).do(job)

print("Scheduler started. Waiting for the scheduled time...")

while True:
    schedule.run_pending()
    time.sleep(1)
