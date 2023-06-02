"""Testing the scanner module"""

import pytest
import tempfile
from names import Names
from scanner import Scanner


@pytest.fixture
def new_scanner():
    """Return a Scanner with input -> scan_test_input.txt"""
    names = Names()
    newscanner = Scanner('scan_test_input.txt', names)
    return newscanner


@pytest.fixture
def new_scanner2():
    """Return a Scanner with input -> scan_test_input2.txt"""
    names = Names()
    newscanner = Scanner('scan_test_input2.txt', names)
    return newscanner


@pytest.fixture
def scan_invalidchar():
    """Return a Scanner with input given by the tempfile below"""
    names = Names()
    text = 'NAND G!;\nSWITCH 0 SW@\nCONNECT SW1 > G1.I1;'

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        """Write the string content to the temporary file"""
        temp_file.write(text)
        """Get the path of the temporary file"""
        path = temp_file.name

    scanner = Scanner(path, names)
    return scanner


def test_new_scanner(new_scanner):
    """Test scanner gives correct output"""
    sym = new_scanner.get_symbol()
    while sym.type != new_scanner.EOF:
        sym = new_scanner.get_symbol()

    assert type(new_scanner.symbol_type_list) == range
    assert all(isinstance(keyword, str)
               for keyword in new_scanner.keywords_list)
    assert new_scanner.keywords_list == ["CONNECT", "SWITCH", "MONITOR",
                                         "CLOCK", "AND", "NAND", "OR", "NOR",
                                         "DTYPE", "XOR"]
    assert len(new_scanner.symbol_type_list) == 8
    assert new_scanner.current_character == ''


def test_get_position(new_scanner):
    """Test scanner returns the correct symbol position"""
    arrows_list = []
    sym = new_scanner.get_symbol()
    while sym.type != new_scanner.EOF:
        sym = new_scanner.get_symbol()
        if sym.type == 2:
            arrows_list.append([sym.linenum, sym.linepos])
    new_scanner.input_file.close()

    assert new_scanner.names.name_list == ["CONNECT", "SWITCH", "MONITOR",
                                           "CLOCK", "AND", "NAND", "OR", "NOR",
                                           "DTYPE", "XOR", 'G1', 'SW1', 'SW2',
                                           'I1', 'I2']
    assert arrows_list == [[3, [13, 13]], [4, [13, 13]]]


def testquery(new_scanner):
    """Testing the Scanner module query function"""

    seen = {}
    sym = new_scanner.get_symbol()
    verdict = True
    while sym.type != new_scanner.EOF:
        sym = new_scanner.get_symbol()

        if new_scanner.current_character.isalpha():

            symname = new_scanner.get_name()
            if symname not in new_scanner.keywords_list:
                sym.type = new_scanner.NAME
                [sym.id] = new_scanner.names.lookup([symname])
            if sym.type == new_scanner.NAME:
                if symname not in seen:
                    seen[symname] = sym.id

                elif symname in seen:
                    if seen[symname] != new_scanner.names.query(symname):
                        verdict = False

    assert verdict


def test_invalidchar(scan_invalidchar):
    """Testing that invalid characters are assigned a NoneType"""
    sym = scan_invalidchar.get_symbol()
    poslist = []
    while sym.type != scan_invalidchar.EOF:
        sym = scan_invalidchar.get_symbol()
        if sym.type is None:
            poslist.append([sym.linenum, sym.linepos])

    assert poslist == [[0, [7, 7]], [1, [12, 12]]]
    assert type(scan_invalidchar.symbol_type_list) == range
    assert all(isinstance(keyword, str)
               for keyword in scan_invalidchar.keywords_list)
    assert scan_invalidchar.keywords_list == ["CONNECT", "SWITCH",
                                              "MONITOR", "CLOCK",
                                              "AND", "NAND", "OR", "NOR",
                                              "DTYPE", "XOR"]
    assert len(scan_invalidchar.symbol_type_list) == 8
    assert scan_invalidchar.current_character == ''
