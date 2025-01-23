import platform
import os
import logging
import time
from abc import ABC, abstractmethod

class BluetoothInterface(ABC):
    """Abstract base class for platform-specific bluetooth implementations"""
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

class LinuxBluetoothHandler(BluetoothInterface):
    """Linux implementation using bluetoothctl with enhanced connection management"""
    def __init__(self, devices):
        self.devices = devices
        import pexpect
        self.pexpect = pexpect
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def _get_connected_devices(self):
        """Get list of devices currently connected to the speaker"""
        try:
            bluetoothctl = self.pexpect.spawn('bluetoothctl')
            bluetoothctl.sendline('devices')
            bluetoothctl.expect('Controller', timeout=5)
            devices_output = bluetoothctl.before.decode()
            bluetoothctl.sendline('quit')
            
            # Parse device list
            devices = []
            for line in devices_output.split('\n'):
                if 'Device' in line:
                    mac = line.split()[1]
                    devices.append(mac)
            return devices
        except Exception as e:
            logging.error(f"Error getting connected devices: {str(e)}")
            return []

    def _force_disconnect_others(self):
        """Disconnect other devices from the speaker"""
        try:
            bluetoothctl = self.pexpect.spawn('bluetoothctl')
            
            # Get list of connected devices
            bluetoothctl.sendline('paired-devices')
            bluetoothctl.expect('Controller', timeout=5)
            devices_output = bluetoothctl.before.decode()
            
            # Disconnect each device except our target
            for line in devices_output.split('\n'):
                if 'Device' in line:
                    device_mac = line.split()[1]
                    if device_mac not in self.devices:
                        logging.info(f"Attempting to disconnect device: {device_mac}")
                        bluetoothctl.sendline(f'disconnect {device_mac}')
                        bluetoothctl.expect(['successful', 'Failed'], timeout=5)
            
            bluetoothctl.sendline('quit')
            return True
        except Exception as e:
            logging.error(f"Error forcing disconnections: {str(e)}")
            return False

    def connect(self):
        """Connect to the speaker with retry mechanism and force disconnect"""
        for attempt in range(self.max_retries):
            try:
                logging.info(f"Connection attempt {attempt + 1} of {self.max_retries}")
                
                # First, try to connect normally
                if self._try_connect():
                    logging.info("Connected successfully")
                    return True
                
                # If failed, try forcing disconnection of other devices
                logging.info("Connection failed, attempting to force disconnect other devices")
                self._force_disconnect_others()
                
                # Wait a bit for disconnections to take effect
                time.sleep(self.retry_delay)
                
                # Try connecting again
                if self._try_connect():
                    logging.info("Connected successfully after forcing disconnections")
                    return True
                
                # If still failed, wait before next attempt
                time.sleep(self.retry_delay)
                
            except Exception as e:
                logging.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:  # Don't sleep on last attempt
                    time.sleep(self.retry_delay)
        
        logging.error("All connection attempts failed")
        return False

    def _try_connect(self):
        """Single connection attempt"""
        try:
            bluetoothctl = self.pexpect.spawn('bluetoothctl')
            
            # Remove and re-add device
            bluetoothctl.sendline(f'remove {self.devices[0]}')
            time.sleep(1)
            bluetoothctl.sendline('scan on')
            time.sleep(2)  # Give it time to discover
            bluetoothctl.sendline('scan off')
            
            # Pair and connect
            bluetoothctl.sendline(f'pair {self.devices[0]}')
            bluetoothctl.expect(['successful', 'Failed'], timeout=10)
            
            bluetoothctl.sendline(f'trust {self.devices[0]}')
            bluetoothctl.expect(['successful', 'Failed'], timeout=5)
            
            bluetoothctl.sendline(f'connect {self.devices[0]}')
            index = bluetoothctl.expect(['Connection successful', 'Failed to connect'], timeout=10)
            
            bluetoothctl.sendline('quit')
            return index == 0
            
        except Exception as e:
            logging.error(f"Connection attempt failed: {str(e)}")
            return False

    def is_connected(self):
        try:
            bluetoothctl = self.pexpect.spawn('bluetoothctl')
            bluetoothctl.sendline(f'info {self.devices[0]}')
            bluetoothctl.expect(['Connected: yes', 'Connected: no', 'Device not found'], timeout=5)
            result = 'Connected: yes' in bluetoothctl.after.decode()
            bluetoothctl.sendline('quit')
            return result
        except Exception as e:
            logging.error(f"Linux Bluetooth status check error: {str(e)}")
            return False

    def disconnect(self):
        try:
            bluetoothctl = self.pexpect.spawn('bluetoothctl')
            bluetoothctl.sendline(f'disconnect {self.devices[0]}')
            bluetoothctl.expect(['Successful disconnected', 'Failed to disconnect'], timeout=5)
            result = 'Successful' in bluetoothctl.after.decode()
            bluetoothctl.sendline('quit')
            return result
        except Exception as e:
            logging.error(f"Linux Bluetooth disconnection error: {str(e)}")
            return False

class WindowsBluetoothHandler(BluetoothInterface):
    """Windows implementation using Qt Bluetooth"""
    def __init__(self, devices):
        self.devices = devices
        self.current_device = None
        try:
            from PyQt5.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo
            from PyQt5.QtCore import QTimer, QEventLoop, QCoreApplication
            import sys
            self.QtBluetooth = QBluetoothDeviceDiscoveryAgent
            self.QtDeviceInfo = QBluetoothDeviceInfo
            self.QTimer = QTimer
            self.QEventLoop = QEventLoop
            self.discovered_devices = []
            
            # Initialize Qt application if not already initialized
            self.app = QCoreApplication.instance()
            if not self.app:
                self.app = QCoreApplication(sys.argv)
        except ImportError as e:
            logging.error("Please install PyQt5: pip install PyQt5")
            raise

    def _discover_devices(self, timeout=10000):
        """
        Discover nearby Bluetooth devices using Qt's discovery agent
        timeout: time in milliseconds to scan for devices
        """
        self.discovered_devices = []
        discovery_agent = self.QtBluetooth()
        
        # Set up event loop for synchronous discovery
        loop = self.QEventLoop()
        
        def device_discovered(device_info):
            device_address = device_info.address().toString()
            device_name = device_info.name()
            logging.info(f"Found device: {device_name} ({device_address})")
            self.discovered_devices.append((device_address, device_name))
        
        def discovery_finished():
            loop.quit()
        
        # Connect signals
        discovery_agent.deviceDiscovered.connect(device_discovered)
        discovery_agent.finished.connect(discovery_finished)
        
        # Start discovery
        discovery_agent.start()
        
        # Set timeout
        timer = self.QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(timeout)
        
        # Wait for discovery to complete or timeout
        loop.exec_()
        
        # Clean up
        discovery_agent.stop()
        return self.discovered_devices

    def connect(self):
        for device in self.devices:
            try:
                logging.info(f"Attempting to connect to {device['name']} ({device['mac_address']})")
                self.current_device = device
                
                # Discover devices
                discovered = self._discover_devices()
                
                # Check if our device is among discovered devices
                device_addr = device['mac_address'].upper()  # Qt returns uppercase addresses
                for addr, name in discovered:
                    if addr == device_addr:
                        logging.info(f"Found device {device['name']}")
                        return True

                logging.warning(f"Device {device['name']} not found in range")
                
            except Exception as e:
                logging.error(f"Windows Bluetooth connection error for {device['name']}: {str(e)}")
                logging.debug("Full error details:", exc_info=True)
                continue

        return False

    def is_connected(self):
        try:
            if not self.current_device:
                return False

            # Do a quick discovery to check if device is in range
            discovered = self._discover_devices(timeout=5000)  # 5 seconds timeout
            device_addr = self.current_device['mac_address'].upper()
            return any(addr == device_addr for addr, _ in discovered)
            
        except Exception as e:
            logging.error(f"Windows Bluetooth status check error: {str(e)}")
            return False

    def disconnect(self):
        # Qt's Bluetooth module doesn't provide direct disconnect functionality
        # We'll just return True as Windows handles disconnection automatically
        return True

    def get_current_device(self):
        """Return the current device information"""
        return self.current_device

    def check_all_devices(self):
        """Debug method to check status of all configured devices"""
        try:
            logging.info("Scanning for all configured devices...")
            discovered = self._discover_devices(timeout=10000)  # 10 seconds timeout
            
            for device in self.devices:
                device_addr = device['mac_address'].upper()
                found = False
                
                for addr, name in discovered:
                    if addr == device_addr:
                        found = True
                        logging.info(f"Device {device['name']}:")
                        logging.info(f"  Found in range: Yes")
                        logging.info(f"  Reported name: {name}")
                        break
                        
                if not found:
                    logging.info(f"Device {device['name']}:")
                    logging.info(f"  Found in range: No")
                    
        except Exception as e:
            logging.error(f"Error scanning for devices: {str(e)}")

class BluetoothHandler:
    """Factory class that returns the appropriate handler for the current platform"""
    def __init__(self, devices):
        self.devices = devices
        self._handler = self._create_handler()

    def _create_handler(self):
        system = platform.system().lower()
        if system == 'linux':
            return LinuxBluetoothHandler(self.devices)
        elif system == 'windows':
            return WindowsBluetoothHandler(self.devices)
        else:
            raise NotImplementedError(f"Bluetooth support not implemented for {system}")

    def connect(self):
        return self._handler.connect()

    def disconnect(self):
        return self._handler.disconnect()

    def is_connected(self):
        return self._handler.is_connected()

    def get_current_device(self):
        return self._handler.get_current_device()

    def check_all_devices(self):
        if hasattr(self._handler, 'check_all_devices'):
            return self._handler.check_all_devices() 