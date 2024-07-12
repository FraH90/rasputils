import sys
import json
import random
import time
import asyncio
import vlc
import os
from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtBluetooth import (QBluetoothDeviceDiscoveryAgent, QBluetoothSocket,
                               QBluetoothLocalDevice, QBluetoothAddress,
                               QBluetoothUuid, QBluetoothServiceInfo)

CURRENT_TASK_DIR = os.path.dirname(__file__)

CONFIG_FILE = os.path.join(CURRENT_TASK_DIR, 'config.json')
RADIO_STREAM_FILE = os.path.join(CURRENT_TASK_DIR, 'radio_stations.json')

class BluetoothHandler:
    def __init__(self, mac_address):
        self.mac_address = QBluetoothAddress(mac_address)
        self.socket = None
        self.local_device = QBluetoothLocalDevice()

    async def pair_device(self):
        print(f"Attempting to pair with {self.mac_address.toString()}")
        self.local_device.requestPairing(self.mac_address, QBluetoothLocalDevice.Paired)
        for _ in range(20):  # Wait up to 10 seconds for pairing
            await asyncio.sleep(0.5)
            if self.local_device.pairingStatus(self.mac_address) == QBluetoothLocalDevice.Paired:
                print("Pairing successful")
                return True
        print("Pairing failed or timed out")
        return False

    async def connect_to_device(self):
        print(f"Attempting to connect to {self.mac_address.toString()}")
        
        # Check if the device is paired
        pairing_status = self.local_device.pairingStatus(self.mac_address)
        if pairing_status == QBluetoothLocalDevice.Unpaired:
            print(f"Device {self.mac_address.toString()} is not paired. Attempting to pair...")
            self.local_device.requestPairing(self.mac_address, QBluetoothLocalDevice.Paired)
            await asyncio.sleep(5)  # Wait for pairing to complete
        
        self.socket = QBluetoothSocket(QBluetoothServiceInfo.RfcommProtocol)
        self.socket.connected.connect(self.on_connected)
        self.socket.error.connect(self.on_error)
        
        print(f"Connecting to {self.mac_address.toString()}...")
        self.socket.connectToService(self.mac_address, QBluetoothUuid(QBluetoothUuid.SerialPort))
        
        # Wait for connection or error
        for _ in range(20):  # Wait up to 10 seconds
            await asyncio.sleep(0.5)
            if self.socket.state() == QBluetoothSocket.ConnectedState:
                print("Connection established!")
                return True
            elif self.socket.error() != QBluetoothSocket.NoSocketError:
                print(f"Connection failed: {self.socket.errorString()}")
                return False
        
        print("Connection timeout")
        return False

    def on_connected(self):
        print(f"Connected to {self.mac_address.toString()}")

    def on_error(self, error):
        print(f"Error connecting to {self.mac_address.toString()}: {self.socket.errorString()}")

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def load_radio_streams():
    with open(RADIO_STREAM_FILE, 'r') as f:
        return json.load(f)

def play_radio_for_one_hour(stream_url, radio_name):
    player = vlc.MediaPlayer(stream_url)
    player.play()
    print(f"{time.strftime('%H:%M')} - Playing radio {radio_name}")
    # Play for 1 hour (3600 seconds)
    time.sleep(3600)
    # Stop the player
    player.stop()
    print(f"{time.strftime('%H:%M')} - Stopped playing radio {radio_name}")

async def main():
    config = load_config()
    radio_streams = load_radio_streams()
    bluetooth_mac_address = config['bluetooth_mac_address']
    radio_stream = random.choice(radio_streams)
    radio_stream_url = radio_stream['url']
    radio_name = radio_stream['name']

    app = QCoreApplication(sys.argv)

    # Discover Bluetooth devices
    discovery_agent = QBluetoothDeviceDiscoveryAgent()
    discovery_agent.deviceDiscovered.connect(device_discovered)
    discovery_agent.finished.connect(lambda: QTimer.singleShot(0, app.quit))
    discovery_agent.start()

    # Run the event loop until all devices are discovered
    app.exec()

    # Now continue with the main logic
    bluetooth_handler = BluetoothHandler(bluetooth_mac_address)
    bluetooth_handler.connect_to_device()
    await asyncio.sleep(5)  # Wait for connection
    play_radio_for_one_hour(radio_stream_url, radio_name)

def device_discovered(info):
    # Callback function to handle discovered devices
    print(f"Device found: {info.name()} [{info.address().toString()}]")
    print(f"\tDevice Type: {info.coreConfigurations()}")
    # Check if the device is connected using QBluetoothLocalDevice
    local_device = QBluetoothLocalDevice()
    pairing_status = local_device.pairingStatus(info.address())
    print(f"\tConnected: {pairing_status != QBluetoothLocalDevice.Unpaired}")
    print(f"\tPaired: {pairing_status == QBluetoothLocalDevice.Paired}")

def thread_loop():
    asyncio.run(main())

if __name__ == "__main__":
    thread_loop()