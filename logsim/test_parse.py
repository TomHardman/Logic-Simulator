"""Test the parse module."""
import pytest
import tempfile
from names import Names
from devices import Devices
from network import Network
from parse import Parser
from scanner import Scanner
from monitors import Monitors


@pytest.fixture
def system_with_test_data():
    """Return a System with text input specified below"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = '''AND 2 G1;\n
           OR 2 G1;\n
           NAND 2 G3;\n
           NOR 2 G4;\n
           SWITCH 1 S1;\n
           SWITCH 0 S2;\n
           CONNECT S1 > G1.I1;\n
           CONNECT S2 > G1.I2;\n
           CONNECT G1  > G3.I1, G1> G3.I2;'''

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]

@pytest.fixture
def system_with_invalid_keywords():
    """Return a System with text input specified below"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = 'INVALID G1;\nNOTHING G2;\nINVALID G3'

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


@pytest.fixture
def system_with_name_keyword():
    """Return a System with input where keyword and names are swapped"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = 'G1 NAND;\nG2 NAND;\nG3 NAND'

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


@pytest.fixture
def system_with_miss_semi():
    """Return a System with input where has missed semicolons"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = 'SWITCH 0 SW1;\n0 SW2 SWITCH\nSWITCH 0 SW3'

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


@pytest.fixture
def system_with_overinput():
    """Return a System with input where connections are made to
       inputs which are already connected"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = """SWITCH 0 SW1;\nSWITCH 0 SW2;\nSWITCH 0 SW3;\n
             NAND 3 G1;\nCONNECT SW1 > G1.I1;\nCONNECT SW2 > G1.I2;\n
             CONNECT SW3 > G1.I1;\n"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


@pytest.fixture
def system_with_wrong_switch_input():
    """Return a System with input where switch is in invalid state"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = 'SWITCH 1 SW1, 0 SW2, 2 SW3;'

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


@pytest.fixture
def system_with_keyword_name():
    """Return a System with input where names are keywords"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = 'NAND 2 NAND;\nXOR 2 XOR;\n SWITCH 0 SW1, 1 SWITCH;'

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


@pytest.fixture
def system_with_output_to_output():
    """Return a System with input where output is connected to output"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = """SWITCH 0 SW1, 0 SW2;\nNAND 2 G1;\nCONNECT SW1 > G1.I1,
              SW2 > G1.I2, G1> G1.I3;"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


@pytest.fixture
def system_with_input_to_input():
    """Return a System with input connected to input"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = """SWITCH 0 SW1, 0 SW2;\nNAND 2 G1;\nCONNECT SW1 > G1.I1,
              SW2 > G1.I2, G1.I1 > G1.I3;"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


@pytest.fixture
def system_with_excess_inputs():
    """Return a System with input where inputs ports are greater
       than the maximum"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = 'NAND 17 G1;'

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


@pytest.fixture
def system_with_no_connect():
    """Return a System with input where gates have empty inputs"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = 'SWITCH 1 SW1, 1 SW2;\nAND 2 G1;\nCONNECT SW1 G1.I1, SW2 > G1.I2;'

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]

@pytest.fixture
def system_with_siggen_invalid():
    """Return a System with invalid SIGGEN inputs"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = """SIGGEN 2 S1, onoffon S2, 1010 SIGGEN, S2, 1001 S1;\n
              AND 2 G1;\n
              CONNECT G1 > S1;"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]

@pytest.fixture
def system_with_RC_invalid():
    """Return a System with invalid RC inputs"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    text = """RC 2 R1, three R2, R3, 1.1 R4;\n
              AND 2 G1;\n
              CONNECT G1 > R1;"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)

    return [names, devices, network, monitors, scanner, parser]


"""Testing the Parser on the inputs given above"""


def test_parse(system_with_test_data):
    """Test a sytm using data string provided"""
    _, devices, _, _, _, parser = system_with_test_data
    parser.parse_network()
    assert len(devices.devices_list) == 5
    assert parser.error_count == 1


def test_invalid_keywords(system_with_invalid_keywords):
    """Test input with invalid keyword"""
    _, devices, _, _, _, parser = system_with_invalid_keywords
    parser.parse_network()
    assert len(devices.devices_list) == 0
    assert parser.error_count == 3


def test_invalid_order(system_with_name_keyword):
    """Test input where order of keyword and name are switched"""
    _, devices, _, _, _, parser = system_with_name_keyword
    parser.parse_network()
    assert len(devices.devices_list) == 0
    assert parser.error_count == 3


def test_miss_semi(system_with_miss_semi):
    """Test input with a missed semicolon"""
    _, devices, _, _, _, parser = system_with_miss_semi
    parser.parse_network()
    assert len(devices.devices_list) == 1
    assert parser.error_count == 1


def test_overinput(system_with_overinput):
    """Test input with more inputs to inputs ports"""
    _, devices, _, _, _, parser = system_with_overinput
    parser.parse_network()
    assert len(devices.devices_list) == 4
    assert parser.error_count == 1


def test_wrong_switch_input(system_with_wrong_switch_input):
    """Test input where switch has invalid starting state"""
    _, devices, _, _, _, parser = system_with_wrong_switch_input
    parser.parse_network()
    assert len(devices.devices_list) == 2
    assert parser.error_count == 1


def test_keyword_name(system_with_keyword_name):
    """Test input with keyword used as a name"""
    _, devices, _, _, _, parser = system_with_keyword_name
    parser.parse_network()
    assert len(devices.devices_list) == 1
    assert parser.error_count == 3


def test_output_to_output(system_with_output_to_output):
    """Test input where output port connected to output port"""
    _, devices, _, _, _, parser = system_with_output_to_output
    parser.parse_network()
    assert len(devices.devices_list) == 3
    assert parser.error_count == 1


def test_input_to_input(system_with_input_to_input):
    """Test input where input port connected to input port"""
    _, devices, _, _, _, parser = system_with_input_to_input
    parser.parse_network()
    assert len(devices.devices_list) == 3
    assert parser.error_count == 1


def test_excess_inputs(system_with_excess_inputs):
    """Test input where excess input ports specified"""
    _, devices, _, _, _, parser = system_with_excess_inputs
    parser.parse_network()
    assert len(devices.devices_list) == 0
    assert parser.error_count == 1


def test_no_connect(system_with_no_connect):
    """Test input where network is not fully connected"""
    _, devices, _, _, _, parser = system_with_no_connect
    parser.parse_network()
    assert len(devices.devices_list) == 3
    assert parser.error_count == 1


def test_invalid_siggen(system_with_siggen_invalid):
    """Test input where SIGGEN has invaid  inputs"""
    _, devices, _, _, _, parser = system_with_siggen_invalid
    parser.parse_network()
    assert len(devices.devices_list) == 2
    assert parser.error_count == 5


def test_invalid_RC(system_with_RC_invalid):
    """Test input where RC has invaid  inputs"""
    _, devices, _, _, _, parser = system_with_RC_invalid
    parser.parse_network()
    assert len(devices.devices_list) == 2
    assert parser.error_count == 4