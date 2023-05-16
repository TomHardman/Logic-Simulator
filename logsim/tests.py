
from names import Names
from scanner import Scanner, Symbol



def test_get_position(new_scanner):
    arrows_list = []
    sym = new_scanner.get_symbol()
    sym.type = new_scanner.KEYWORD

    counter = 0
    while sym.type != new_scanner.EOF:
        sym = new_scanner.get_symbol()
        counter+=1
        if sym.type == 2:
            new_scanner.get_position(sym)
            arrows_list.append([sym.linenum, sym.linepos])

       
    print(counter)
    print(arrows_list)

def new_scanner():
    names = Names()
    newscanner = Scanner('/Users/andrew/Documents/IIA Easter term projects/GF2 Software/Logic-Simulator/logsim/scan_testinput.txt', names)
    return newscanner

new_scannertest = new_scanner()

print(test_get_position(new_scannertest))
#print(new_scannertest.input_file.read())


def get_position(self, symbol):
    """Gets position of symbol which file object is currently pointing at"""
    position = self.input_file.tell()
    self.input_file.seek(0)

    contents = self.input_file.read(position)
    linenum = contents.count('\n') + 1
    linepos = position - contents.rfind('\n') - 1
    
    symbol.linenum = linenum
    symbol.linepos = linepos