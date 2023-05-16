"""Test the parse module."""
import pytest

from names import Names
from devices import Devices
from network import Network
from parse import Parser
from scanner import Scanner
from monitors import Monitors

@pytest.fixture
def network_with_devices():
    """Return a Network class instance with three devices in the network."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    [SW1_ID, SW2_ID, OR1_ID] = names.lookup(["Sw1", "Sw2", "Or1"])

    # Add devices
    devices.make_device(SW1_ID, devices.SWITCH, 0)
    devices.make_device(SW2_ID, devices.SWITCH, 0)
    devices.make_device(OR1_ID, devices.OR, 2)

    return new_network



