# tests for scanner functions

import pytest
from names import Names
from scanner import Scanner, Symbol


@pytest.fixture
def new_scanner():
    names = Names()
    newscanner = Scanner('logsim\scan_test_input.txt', names)
    return newscanner


def test_new_scanner(new_scanner):

    assert type(new_scanner.symbol_type_list) == range
    assert all(isinstance(keyword, str)
               for keyword in new_scanner.keywords_list)
    assert new_scanner.keywords_list == ["CONNECT", "SWITCH",
                                         "AND", "NAND", "NOR", "DTYPE", "XOR"]
    assert len(new_scanner.symbol_type_list) == 7
    assert new_scanner.current_character == 'N'


def test_get_position(new_scanner):
    arrows_list = []
    sym = new_scanner.get_symbol()
    counter = 1
    while sym.type != new_scanner.EOF:
        sym = new_scanner.get_symbol()
        print(sym.type)
        counter += 1
        if sym.type == 2:
            new_scanner.get_position(sym)
            arrows_list.append([sym.linenum, sym.linepos])

    print(counter)

    assert new_scanner.names.name_list == [
        'CONNECT', 'SWITCH', 'AND', 'NAND', 'NOR', 'DTYPE', 'XOR', 'G1', 'SW1', 'SW2', 'O', 'I1', 'I2']
    assert arrows_list == [[4, 15], [5, 15]]
