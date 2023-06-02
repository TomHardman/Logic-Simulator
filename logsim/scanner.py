import os
import sys
"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.linenum = 0
        self.linepos = 0


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    open_file(self, path): Open and returns specified file.

    blank_symbol(self): Returns a blank symbol.

    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.

    skip_spaces(self): Skips tto next point in file which is not a blank space.

    get_name(self): Translate next sequence of letters into a name
                    and returns the name.

    get_number(self): Translates next sequence of digits into a number and
                      returns the number.

    advance(self): Skips forward in the file by one space.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.names = names
        self.symbol_type_list = [self.DOT, self.SEMICOLON,
                                 self.ARROW, self.COMMA,
                                 self.KEYWORD, self.NUMBER,
                                 self.NAME, self.EOF] = range(8)
        self.keywords_list = ["CONNECT", "SWITCH", "MONITOR", "CLOCK",
                              "AND", "NAND", "OR", "NOR", "DTYPE", "XOR"]
        [self.CONNECT_ID, self.SWITCH_ID, self.MONITOR_ID, self.CLOCK_ID,
         self.AND_ID, self.NAND_ID, self.OR_ID, self.NOR_ID,
            self.DTYPE_ID, self.XOR_ID] = self.names.lookup(self.keywords_list)
        self.current_character = ""
        self.input_file = self.open_file(path)
        self.current_character = self.input_file.read(1)

        self.temp_queue = []
        self.priority_queue = []
        self.linecount = 0
        self.poscount = 0
        self.countcarry = 0

        # SYMBOLS
        #   0   .   - DOT
        #   1   ;   - SEMICOLON
        #   2   >  - ARROW
        #   3   KEYWORD
        #   4   NUMBER
        #   5   NAME
        #   6   EOF

    def open_file(self, path):
        """Open and return the file specified by path."""

        try:
            f = open(path, 'r')
        except FileNotFoundError:
            print('Error: File not found - Check the given path is valid')
            sys.exit()

        return f

    def blank_symbol(self):
        return Symbol()

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""

        if self.priority_queue:
            return self.priority_queue.pop(0)

        symbol = Symbol()
        self.skip_spaces()

        if self.current_character.isalpha():
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit():
            symbol.id = self.get_number()
            symbol.type = self.NUMBER
            self.advance()

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == ">":
            symbol.type = self.ARROW
            self.advance()

        elif self.current_character == ".":
            symbol.type = self.DOT
            self.advance()
        elif self.current_character == ",":
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == "":
            symbol.type = self.EOF

        else:
            self.advance()
        if symbol.type != self.EOF:
            if symbol.type != self.KEYWORD and symbol.type != self.NAME:
                symbol.linenum = self.linecount
                symbol.linepos = [self.poscount, self.poscount]
                self.poscount += self.countcarry
                self.countcarry = 0
            else:
                symbol.linenum = self.linecount
                symbol.linepos = [self.poscount, self.poscount+self.countcarry]
                self.poscount += self.countcarry
                self.countcarry = 0
        return symbol

    def skip_spaces(self):
        """Skips ahead in the file until a non-blank space charcter"""
        while self.current_character.isspace():
            self.poscount += 1
            self.countcarry = 0
            if self.current_character == '\n':
                self.linecount += 1
                self.poscount = 0
                self.countcarry = 0
            self.current_character = self.input_file.read(1)

    def get_name(self):
        """Returns the name following on from current character"""
        if not self.current_character.isalpha():
            raise ValueError("Charcter is not a letter")

        name_string = ""
        while self.current_character.isalnum():
            name_string += self.current_character
            self.current_character = self.input_file.read(1)
            self.countcarry += 1

        return name_string

    def get_number(self):
        """Returns number following on from current charcter"""
        if not self.current_character.isdigit():
            raise ValueError("Character is not a digit")

        num_string = ""
        while self.current_character.isdigit():
            num_string += self.current_character
            self.current_character = self.input_file.read(1)
            self.countcarry += 1

        return int(num_string)

    def advance(self):
        """Skips by 1 charcter"""
        self.current_character = self.input_file.read(1)
        self.poscount += 1
