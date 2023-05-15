"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.scanner = scanner
        self.names = names
        self.device = devices
        self.network = network
        self.monitors = monitors

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.

        return True

    def connect(self):
        """Checks for the CONNECT keyword and a valid connection label and attatches the 2 nodes"""
        if (self.symbol.type == self.scanner.KEYWORD and self.symbol_ID == self.scanner.CONNECT_ID):
            self.symbol = self.scanner.get_symbol()
            connection = self.connection()
            # Create connection
        else:
            self.error()
        return True

    def connection(self):
        """Checks the symbosl for a valid connection and returns the 2 node points for a connection"""
        node1 = self.node()
        self.symbol = self.scanner.get_symbol()
        self.arrow()
        self.symbol = self.scanner.get_symbol()
        node2 = self.node()
        return [node1, node2]

    def node(self):
        """Returns the parsed node or calls error() if incorrect"""
        device = self.device()
        self.symbol = self.scanner.get_symbol()
        self.dot()
        self.symbol = self.scanner.get_symbol()
        node = self.device_node(device)
        return node

    def device(self):
        """Checks to see if the symbol corresponds to a valid device and returns a pointer to the device"""
        # Add if clause to check device exists
        if (self.symbol.type == self.scanner.NAME):
            # Bugs assosiated with same name as keyword?
            # Return the device pointer
            return
        else:
            self.error()

    def device_node(self, device):
        """Takes a device as an input and checks if the next symbol corresponds to valid node"""
        return

    def arrow(self):
        """Checks if a symbol is an arrow"""
        if self.symbol == self.scanner.ARROW_ID:
            return
        else:
            self.error()

    def dot(self):
        """Checks if a symbol is a dot"""
        if self.symbol == self.scanner.DOT_ID:
            return
        else:
            self.error()

    def error(self):
        return
