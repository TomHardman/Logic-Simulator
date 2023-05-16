#tests for scanner functions

import pytest
from names import Names
from scanner import Scanner

@pytest.fixture
def new_scanner():
    names = Names()
    newscanner = Scanner('scan_testinput.txt', names)
    return newscanner

def test_new_scanner(new_scanner):

    assert type(new_scanner.symbol_type_list) == list
    assert all(type(new_scanner.keywords_list)) == str
    assert new_scanner.keywords_list == ["CONNECT", "SWITCH",
                                        "AND", "NAND", "NOR", "DTYPE", "XOR"]
    assert len(new_scanner.symbol_type_list) == 7
    assert new_scanner.current_character == ''



def test_get_position(new_scanner):

    sym = new_scanner.input_file.read(1)
    while sym:
        sym = new_scanner.get_symbol()

    assert new_scanner.names == ['G1', 'SW1', 'SW2']






