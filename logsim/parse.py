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
        self.error = False

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        
        # Currently only checks for connect
        '''while self.symbol != self.scanner.EOF:
            self.error = False
            self.symbol = self.scanner.get_symbol()
            self.connect()'''
        return True

    def connect(self):
        """Checks for the CONNECT keyword and a valid connection label and attatches the 2 nodes"""
        if (self.symbol.type == self.scanner.KEYWORD and self.symbol_ID == self.scanner.CONNECT_ID):
            self.symbol = self.scanner.get_symbol()
            connection = self.connection()
            # Create connection
            if not self.error:
                self.network.make_connection(*connection[0], *connection[1])
        else:
            self.error()
        return True

    def connection(self):
        """Checks the symbol for a valid connection and returns the 2 node points for a connection"""
        node1 = self.node()
        node2 = None
        if not self.error:
            self.symbol = self.scanner.get_symbol()
            self.arrow()
        if not self.error:
            self.symbol = self.scanner.get_symbol()
            node2 = self.node()
        return [node1, node2]

    def node(self):
        """Returns the device_id and port_id or calls error() if incorrect"""
        device, device_id = self.device()
        node_id = None
        if not self.error:
            self.symbol = self.scanner.get_symbol()
            self.dot()
        if not self.error:
            self.symbol = self.scanner.get_symbol()
            node_id = self.device_node(device)
        return [device_id, node_id]

    def device(self):
        """Returns the device and device_id"""
        # Add if clause to check device exists
        if (self.symbol.type == self.scanner.NAME and self.symbol.id is not None and self.devies.get_device(self.symbol.id)):
            return [self.devies.get_device(self.symbol.id), self.symbol.id]
        else:
            self.error()

    def device_node(self, device):
        """Takes a device as an input and returns port_id"""
        if (device is not None and self.symbol == self.scanner.NAME and self.symbol.id):
            if (self.symbol.id in device.inputs or self.symbol.id in device.outputs):
                return self.symbol.id
        self.error()

    def arrow(self):
        """Checks if a symbol is an arrow"""
        if self.symbol == self.scanner.ARROW:
            return
        else:
            self.error()

    def dot(self):
        """Checks if a symbol is a dot"""
        if self.symbol == self.scanner.DOT:
            return
        else:
            self.error()

    def error(self):
        """Adds error to count and skips to next semicolon/EOF"""
        self.error = True
        while (self.symbol != self.scanner.SEMICOLON and self.symbol != self.scanner.EOF):
            self.symbol = self.scanner.get_symbol()
