
from names import Names
from scanner import Scanner, Symbol



def test_get_position(new_scanner):
    arrows_list = []
    sym = new_scanner.get_symbol()
    sym.type = new_scanner.KEYWORD

    counter = 0
    while sym.type != new_scanner.EOF:
        sym = new_scanner.get_symbol()
        print(sym.type)
        print(new_scanner.current_character)
        counter+=1
        print(counter)
        if sym.type == 2:
            arrows_list.append([sym.linenum, sym.linepos])

        print(new_scanner.names.name_list)

    print(counter)
    print(arrows_list)

def new_scanner():
    names = Names()
    newscanner = Scanner('logsim\scan_testinput.txt', names)
    return newscanner

new_scannertest = new_scanner()

print(test_get_position(new_scannertest))
print(new_scannertest.input_file.read())