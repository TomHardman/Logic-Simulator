"""Test the parse module."""
import pytest
import tempfile

from io import StringIO,BytesIO
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

    path = 'logsim/parse_test_input.txt'

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]

@pytest.fixture
def system_with_invalid_keywords():
    """Return a Network class instance with three devices in the network."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text ='INVALID G1;\nNOTHING G2;\nINVALID G3'
    

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
    # Write the string content to the temporary file
        temp_file.write(text)
        # Get the path of the temporary file
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]

@pytest.fixture
def system_with_name_keyword():
    """Return a Network class instance with three devices in the network."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text ='G1 NAND;\nG2 NAND;\nG3 NAND'
    

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
    # Write the string content to the temporary file
        temp_file.write(text)
        # Get the path of the temporary file
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]

@pytest.fixture
def system_with_miss_semi():
    """Return a Network class instance with three devices in the network."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text ='SWITCH SW1;\nSW2 SWITCH\nSWITCH SW3'
    

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
    # Write the string content to the temporary file
        temp_file.write(text)
        # Get the path of the temporary file
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]

@pytest.fixture
def system_with_overinput():
    """Return a Network class instance with three devices in the network."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text ="""SWITCH SW1;\nSWITCH SW2;\nSWITCH SW3;\n
             NAND 3 G1;\nCONNECT SW1 > G1.I1;\nCONNECT SW2 > G1.I2;\n
             CONNECT SW3 > G1.I1;\n"""
    

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
    # Write the string content to the temporary file
        temp_file.write(text)
        # Get the path of the temporary file
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


# @pytest.mark.timeout(5)
def test_parse(system_with_test_data):
    names, devices, network, monitors, scanner, parser = system_with_test_data
    parser.parse_network()
    assert len(devices.devices_list) == 5
    assert parser.error_count == 2

def test_invalid_keywords(system_with_invalid_keywords):
    names, devices, network, monitors, scanner, parser = system_with_invalid_keywords
    parser.parse_network()
    assert len(devices.devices_list) == 0
    assert parser.error_count == 3

def test_invalid_order(system_with_name_keyword):
    names, devices, network, monitors, scanner, parser = system_with_name_keyword
    parser.parse_network()
    assert len(devices.devices_list) == 0
    assert parser.error_count == 3

def test_miss_semi(system_with_miss_semi):
    names, devices, network, monitors, scanner, parser = system_with_miss_semi
    parser.parse_network()
    assert len(devices.devices_list) == 1
    assert parser.error_count == 1

def test_overinput(system_with_overinput):
    names, devices, network, monitors, scanner, parser = system_with_overinput
    parser.parse_network()
    assert len(devices.devices_list) == 4
    assert parser.error_count == 1







