import logging
import pexpect
import time

class BluetoothHandler:
    """Linux implementation using bluetoothctl"""
    
    def __init__(self, devices):
        self.devices = devices if isinstance(devices, list) else [devices]
        self.timeout = 10
        self.max_retries = 3
        self.retry_delay = 2
        self.logger = logging.getLogger(__name__)

    def execute_command(self, command, expect_patterns, timeout=None):
        """Execute bluetoothctl command and return output"""
        if timeout is None:
            timeout = self.timeout
            
        try:
            bluetoothctl = pexpect.spawn('bluetoothctl', timeout=timeout)
            bluetoothctl.sendline(command)
            index = bluetoothctl.expect(expect_patterns)
            output = bluetoothctl.before.decode()
            bluetoothctl.sendline('quit')
            return index, output
        except pexpect.TIMEOUT:
            self.logger.error(f"Command timed out: {command}")
            return -1, ""
        except Exception as e:
            self.logger.error(f"Error executing command '{command}': {str(e)}")
            return -1, ""

    def is_paired(self, mac_address):
        """Check if device is paired"""
        _, output = self.execute_command('paired-devices', ['#'])
        return mac_address.upper() in output.upper()

    def is_connected(self, mac_address):
        """Check if device is connected"""
        _, output = self.execute_command(f'info {mac_address}', 
                                       ['Connected: yes', 'Connected: no', 'not available'])
        return 'Connected: yes' in output

    def connect(self):
        """Try to connect to any of the configured devices"""
        for device in self.devices:
            # Handle both dictionary and string inputs
            if isinstance(device, dict):
                mac = device['mac_address'].upper()
                name = device.get('name', 'Unknown Device')
            else:
                mac = device.upper()
                name = 'Unknown Device'
            
            self.logger.info(f"Attempting to connect to {name} ({mac})")
            
            # Check if already connected
            if self.is_connected(mac):
                self.logger.info(f"Device {name} ({mac}) is already connected")
                return True

            # Try to connect with retries
            for attempt in range(self.max_retries):
                try:
                    # If not paired, try pairing first
                    if not self.is_paired(mac):
                        self.logger.info(f"Device {mac} not paired, attempting to pair...")
                        index, _ = self.execute_command(
                            f'pair {mac}',
                            ['Pairing successful', 'Failed to pair', 'Already paired'],
                            timeout=30
                        )
                        if index not in [0, 2]:  # Not successful or already paired
                            continue

                        # Trust the device
                        index, _ = self.execute_command(
                            f'trust {mac}',
                            ['trust succeeded', 'trust failed']
                        )
                        if index != 0:
                            continue

                    # Try to connect
                    self.logger.info(f"Attempting connection to {mac}...")
                    index, _ = self.execute_command(
                        f'connect {mac}',
                        ['Connection successful', 'Failed to connect', 'Device is already connected'],
                        timeout=15
                    )

                    if index in [0, 2]:  # Success or already connected
                        self.logger.info(f"Successfully connected to {name} ({mac})")
                        return True

                except Exception as e:
                    self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")

                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)

            self.logger.error(f"Failed to connect to {name} ({mac}) after {self.max_retries} attempts")

        self.logger.error("Failed to connect to any configured Bluetooth devices")
        return False

    def disconnect(self):
        """Disconnect from any connected device"""
        for device in self.devices:
            if isinstance(device, dict):
                mac = device['mac_address'].upper()
            else:
                mac = device.upper()

            if self.is_connected(mac):
                index, _ = self.execute_command(
                    f'disconnect {mac}',
                    ['Successful disconnected', 'Failed to disconnect']
                )
                if index == 0:
                    self.logger.info(f"Successfully disconnected from {mac}")
                    return True
                else:
                    self.logger.error(f"Failed to disconnect from {mac}")
        return False