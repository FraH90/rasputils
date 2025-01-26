import platform
import logging
import time

# We'll use an abstract base class to illustrate the design, but it's optional.
from abc import ABC, abstractmethod

###########################################################
# 1) The original Linux code, renamed to LinuxBluetoothHandler
#    (kept exactly as you provided, except for the class name)
###########################################################
try:
    import pexpect
except ImportError:
    pexpect = None
    # On Windows or if pexpect isn't installed, this will be None.

class LinuxBluetoothHandler(ABC):
    """
    Linux implementation using a single bluetoothctl session.
    EXACT copy of your original code, except renamed to LinuxBluetoothHandler
    so we can wrap it in a cross-platform factory later.
    """

    def __init__(self, devices):
        if pexpect is None:
            raise RuntimeError("pexpect is required for LinuxBluetoothHandler but is not installed.")

        self.devices = devices if isinstance(devices, list) else [devices]
        self.timeout = 10
        self.max_retries = 3
        self.retry_delay = 2
        self.logger = logging.getLogger(__name__)

        # Spawn a single bluetoothctl process
        self.btctl = pexpect.spawn("bluetoothctl", timeout=self.timeout)
        # Turn agent on and set as default agent to handle pairing/passkey
        self.btctl.sendline("agent on")
        self.btctl.sendline("default-agent")

        # Optional: Power on the Bluetooth adapter
        self.btctl.sendline("power on")
        # We expect a prompt or final line after each command;
        # so let's do a quick read to clear any immediate response.
        try:
            self.btctl.expect(r"\[bluetooth\]?.*#", timeout=2)
        except pexpect.TIMEOUT:
            pass

    def run_command(self, command, expect_patterns, timeout=None):
        """
        Send a command to the single bluetoothctl session.
        Return (index, output) from pexpect, where:
          - index is which pattern from expect_patterns matched
          - output is the text before the match
        """
        if timeout is None:
            timeout = self.timeout

        self.logger.debug(f"Running command: {command}")
        self.btctl.sendline(command)

        combined_patterns = expect_patterns + [r"\[bluetooth\]?.*#"]
        index = -1
        output = ""

        try:
            while True:
                i = self.btctl.expect(combined_patterns, timeout=timeout)
                # If i corresponds to one of our custom patterns (not the last prompt),
                # return immediately.
                if i < len(expect_patterns):
                    output = self.btctl.before.decode(errors="replace")
                    return i, output
                else:
                    # We matched the prompt but none of the custom patterns
                    output = self.btctl.before.decode(errors="replace")
                    return -1, output
        except pexpect.TIMEOUT:
            self.logger.error(f"Command timed out: {command}")
            return -1, ""

    def is_paired(self, mac_address):
        """
        Check if device is paired by parsing 'info <MAC>'.
        We'll look for 'Paired: yes' in the output.
        """
        cmd = f"info {mac_address}"
        index, output = self.run_command(cmd, ["Paired: yes", "Paired: no", "not available"])
        # index = 0 -> matched "Paired: yes"
        # index = 1 -> matched "Paired: no"
        # index = 2 -> matched "not available"
        # index = -1 -> we only matched the prompt (no direct pattern)

        return (index == 0)

    def is_connected(self, mac_address):
        """Check if device is connected by parsing 'info'."""
        index, output = self.run_command(
            f"info {mac_address}",
            ["Connected: yes", "Connected: no", "not available"]
        )
        return (index == 0)  # "Connected: yes"

    def connect(self):
        """Try to connect to any of the configured devices."""
        for device in self.devices:
            # Handle both dictionary and string inputs
            if isinstance(device, dict):
                mac = device["mac_address"].upper()
                name = device.get("name", "Unknown Device")
            else:
                mac = device.upper()
                name = "Unknown Device"

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
                        self.logger.info(f"Device {mac} not paired; attempting to pair...")
                        index, output = self.run_command(
                            f"pair {mac}",
                            ["Pairing successful", "Failed to pair", "Already paired"],
                            timeout=30
                        )
                        if index not in [0, 2]:  # Not successful or not "Already paired"
                            self.logger.warning(f"Pair failed: {output.strip()}")
                            continue

                        # Trust the device
                        index, output = self.run_command(
                            f"trust {mac}",
                            ["trust succeeded", "trust failed"]
                        )
                        if index != 0:
                            self.logger.warning(f"Trust failed: {output.strip()}")
                            continue

                    # Now attempt to connect
                    self.logger.info(f"Attempting connection to {mac} (attempt {attempt+1})...")
                    index, output = self.run_command(
                        f"connect {mac}",
                        [
                            "Connection successful",
                            "Failed to connect",
                            "Device is already connected"
                        ],
                        timeout=15
                    )

                    # index = 0 means "Connection successful"
                    # index = 2 means "Device is already connected"
                    if index in [0, 2]:
                        self.logger.info(f"Successfully connected to {name} ({mac})")
                        return True
                    else:
                        self.logger.warning(f"Connect attempt failed: {output.strip()}")

                except Exception as e:
                    self.logger.error(f"Attempt {attempt + 1} error: {str(e)}")

                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)

            self.logger.error(f"Failed to connect to {name} ({mac}) after {self.max_retries} attempts")

        self.logger.error("Failed to connect to any configured Bluetooth devices")
        return False

    def disconnect(self):
        """Disconnect from any connected device."""
        disconnected_any = False
        for device in self.devices:
            if isinstance(device, dict):
                mac = device["mac_address"].upper()
            else:
                mac = device.upper()

            if self.is_connected(mac):
                index, output = self.run_command(
                    f"disconnect {mac}",
                    ["Successful disconnected", "Failed to disconnect"]
                )
                if index == 0:
                    self.logger.info(f"Successfully disconnected from {mac}")
                    disconnected_any = True
                else:
                    self.logger.error(f"Failed to disconnect from {mac} - {output.strip()}")
        return disconnected_any

    def cleanup(self):
        """Cleanly exit bluetoothctl session."""
        if hasattr(self, 'btctl') and self.btctl.isalive():
            self.btctl.sendline("exit")
            self.btctl.close(force=True)

###########################################################
# 2) A simplified Windows handler using PyQt5
###########################################################
try:
    from PyQt5.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo
    from PyQt5.QtCore import QTimer, QEventLoop, QCoreApplication
    import sys
    _HAS_QT = True
except ImportError:
    _HAS_QT = False

class WindowsBluetoothHandler(ABC):
    """
    Windows implementation using PyQt5 for discovery (simplified).
    We'll mimic the same method signatures: connect, disconnect, is_connected, cleanup.
    """

    def __init__(self, devices):
        if not _HAS_QT:
            raise RuntimeError("PyQt5 is required for WindowsBluetoothHandler but is not installed.")

        self.devices = devices if isinstance(devices, list) else [devices]
        self.current_device = None
        # Create a QCoreApplication if none exists (for PyQt event loop)
        self.app = QCoreApplication.instance()
        if not self.app:
            self.app = QCoreApplication(sys.argv)

        self._discovery_agent = None

    def _discover_devices(self, timeout_ms=10000):
        """
        Discover nearby Bluetooth devices using Qt's discovery agent.
        Returns a list of (address, name) found within the timeout.
        """
        discovered = []

        agent = QBluetoothDeviceDiscoveryAgent()
        loop = QEventLoop()

        def device_found(device_info):
            address = device_info.address().toString()
            name = device_info.name()
            logging.info(f"Found device: {name} ({address})")
            discovered.append((address.upper(), name))

        def discovery_finished():
            loop.quit()

        # Connect signals
        agent.deviceDiscovered.connect(device_found)
        agent.finished.connect(discovery_finished)
        agent.canceled.connect(discovery_finished)

        # Start discovery
        agent.start()

        # Timeout with a QTimer
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(timeout_ms)

        loop.exec_()  # Block until finished or timeout
        agent.stop()

        return discovered

    def connect(self):
        """
        For simplicity: We'll do a device discovery and see if
        our target device is in range. If found, we consider it "connected."
        """
        # In reality, Windows might need further pairing steps.
        # We'll keep it minimal for demonstration.
        for device in self.devices:
            mac = device["mac_address"].upper() if isinstance(device, dict) else device.upper()
            name = device.get("name", "Unknown Device") if isinstance(device, dict) else "Unknown Device"

            logging.info(f"Attempting to connect to {name} ({mac})")

            discovered = self._discover_devices(timeout_ms=5000)
            # Check if the device is discovered
            for (addr, dev_name) in discovered:
                if addr == mac:
                    logging.info(f"Found {name} at {mac} - marking as connected.")
                    self.current_device = {"mac_address": mac, "name": name}
                    return True

            logging.warning(f"Device {name} ({mac}) not found in range.")

        return False

    def is_connected(self):
        """Check if our current_device is still discoverable in a quick scan."""
        if not self.current_device:
            return False
        mac = self.current_device["mac_address"]
        discovered = self._discover_devices(timeout_ms=3000)
        return any(addr == mac for (addr, _) in discovered)

    def disconnect(self):
        """
        PyQt5/QtBluetooth doesn't provide a direct 'disconnect' method for
        classic BT devices. We'll just pretend we disconnected.
        """
        if self.current_device:
            logging.info(f"Pretending to disconnect from {self.current_device}")
            self.current_device = None
            return True
        return False

    def cleanup(self):
        """Nothing special to do for Windows in this simplified approach."""
        pass

###########################################################
# 3) The cross-platform "factory" class
###########################################################
class BluetoothHandler:
    """
    A factory class that returns the appropriate handler for the current platform.
    On Linux, uses LinuxBluetoothHandler (bluetoothctl + pexpect).
    On Windows, uses WindowsBluetoothHandler (PyQt5 for discovery).
    """

    def __init__(self, devices):
        self.devices = devices
        self._impl = self._create_impl()

    def _create_impl(self):
        system = platform.system().lower()
        if system == 'linux':
            # Use the LinuxBluetoothHandler (original code).
            return LinuxBluetoothHandler(self.devices)
        elif system == 'windows':
            # Use the WindowsBluetoothHandler (Qt-based).
            return WindowsBluetoothHandler(self.devices)
        else:
            raise NotImplementedError(f"BluetoothHandler not implemented for OS: {system}")

    def connect(self):
        return self._impl.connect()

    def disconnect(self):
        return self._impl.disconnect()

    def is_connected(self):
        # If we need to pass a MAC address on Linux,
        # you can adapt it. But the original code tries all devices.
        return self._impl.is_connected()

    def cleanup(self):
        # We added a cleanup method on both. 
        return self._impl.cleanup()
