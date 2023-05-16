"""Test the parse module."""
import pytest

from names import Names
from devices import Devices
from network import Network
from parse import Parser
from scanner import Scanner
from monitors import Monitors


@pytest.fixture
def system_with_test_data():
    """Return a Network class instance with three devices in the network."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    path = "logsim\parse_test_input.txt"

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


# @pytest.mark.timeout(5)
def test_parse(system_with_test_data):
    names, devices, network, monitors, scanner, parser = system_with_test_data
    parser.parse_network()
    assert len(devices.devices_list) == 6
    assert parser.error_count == 0
