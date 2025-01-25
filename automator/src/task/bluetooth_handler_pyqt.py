import sys
import logging
from PyQt5.QtBluetooth import (QBluetoothDeviceDiscoveryAgent, 
                              QBluetoothLocalDevice,
                              QBluetoothAddress)
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

class BluetoothHandler:
    """Simple cross-platform Bluetooth handler using PyQt"""
    
    def __init__(self, mac_address):
        """Initialize the handler with a target MAC address"""
        self.mac_address = mac_address.upper()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Qt application
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Initialize Bluetooth
        self.local_device = QBluetoothLocalDevice()
        if not self.local_device.isValid():
            self.logger.error("No Bluetooth adapter found")
            raise RuntimeError("No Bluetooth adapter available")
            
        # Turn on Bluetooth if it's off
        if self.local_device.hostMode() == QBluetoothLocalDevice.HostPoweredOff:
            self.local_device.powerOn()
            
        self.device_found = False
        self.connected = False

    def connect(self):
        """Connect to the specified Bluetooth device"""
        try:
            self.logger.info(f"Attempting to connect to: {self.mac_address}")
            
            # Create discovery agent
            discovery_agent = QBluetoothDeviceDiscoveryAgent()
            
            # Set up discovery callback
            def on_device_discovered(device_info):
                if device_info.address().toString().upper() == self.mac_address:
                    self.device_found = True
                    discovery_agent.stop()
                    
                    # Attempt pairing
                    self.local_device.requestPairing(
                        QBluetoothAddress(self.mac_address),
                        QBluetoothLocalDevice.Paired
                    )
            
            discovery_agent.deviceDiscovered.connect(on_device_discovered)
            
            # Start discovery
            discovery_agent.start()
            
            # Set timeout for discovery
            timeout_timer = QTimer()
            timeout_timer.setSingleShot(True)
            timeout_timer.timeout.connect(lambda: discovery_agent.stop())
            timeout_timer.start(10000)  # 10 second timeout
            
            # Process events until device is found or timeout
            while not self.device_found and timeout_timer.isActive():
                self.app.processEvents()
            
            # Check connection status
            if self.device_found:
                # Wait a bit for pairing to complete
                QTimer.singleShot(2000, self.app.quit)
                self.app.exec_()
                
                pairing_status = self.local_device.pairingStatus(
                    QBluetoothAddress(self.mac_address)
                )
                self.connected = (pairing_status == QBluetoothLocalDevice.Paired)
                
                if self.connected:
                    self.logger.info("Successfully connected to device")
                    return True
                else:
                    self.logger.error("Failed to pair with device")
                    return False
            else:
                self.logger.error("Device not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from the current device"""
        try:
            if self.connected:
                self.local_device.requestPairing(
                    QBluetoothAddress(self.mac_address),
                    QBluetoothLocalDevice.Unpaired
                )
                self.connected = False
                self.logger.info("Successfully disconnected")
                return True
            return True
        except Exception as e:
            self.logger.error(f"Disconnection error: {str(e)}")
            return False

    def is_connected(self):
        """Check if currently connected to the device"""
        try:
            if not self.connected:
                return False
                
            pairing_status = self.local_device.pairingStatus(
                QBluetoothAddress(self.mac_address)
            )
            return pairing_status == QBluetoothLocalDevice.Paired
        except Exception as e:
            self.logger.error(f"Status check error: {str(e)}")
            return False