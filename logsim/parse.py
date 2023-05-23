"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.

Format - Underlines parts of text to show general location of error
"""
class Format:
    def __init__(self):
        self.end = '\033[0m'
        self.red = '\033[91m'
        self.underline = '\033[4m'

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
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.error_bool = False
        self.error_count = 0

        [self.NAME_EXPECTED, self.SEMICOLON_EXPECTED, self.KEYWORD_EXPECTED,
            self.NUMBER_EXPECTED, self.ARROW_EXPECTED] = self.names.unique_error_codes(5)

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.

        self.symbol = self.scanner.get_symbol()
        while self.symbol.type != self.scanner.EOF:
            self.error_bool = False

            if self.symbol.id == self.scanner.CONNECT_ID:
                self.connect_keyword()
            elif self.symbol.id == self.scanner.AND_ID:
                self.and_keyword()
            elif self.symbol.id == self.scanner.NAND_ID:
                self.nand_keyword()
            elif self.symbol.id == self.scanner.OR_ID:
                self.or_keyword()
            elif self.symbol.id == self.scanner.NOR_ID:
                self.nor_keyword()
            elif self.symbol.id == self.scanner.SWITCH_ID:
                self.switch_keyword()
            elif self.symbol.id == self.scanner.XOR_ID:
                self.xor_keyword()
            elif self.symbol.id == self.scanner.DTYPE_ID:
                self.dtype_keyword()
            elif self.symbol.id == self.scanner.MONITOR_ID:
                self.monitor_keyword()
            elif self.symbol.id == self.scanner.CLOCK_ID:
                self.clock_keyword()
            else:
                self.error(self.KEYWORD_EXPECTED)

        if self.error_count == 0:
            return True
        else:
            return False

    def connection(self):
        """Checks the symbol for a valid connection and returns the 2 node points for a connection"""
        node1 = self.node()
        node2 = None
        if not self.error_bool:
            self.arrow()
        if not self.error_bool:
            node2 = self.node()
        return [node1, node2]

    def node(self):
        """Returns the device_id and port_id or calls error() if incorrect"""
        device, device_id = self.device()
        port_id = None
        if not self.error_bool and self.symbol.type == self.scanner.DOT:
            self.symbol = self.scanner.get_symbol()
            port_id = self.device_port(device)
        elif not self.error_bool and not None in device.outputs:
            self.error(self.network.PORT_ABSENT)
        return [device_id, port_id]

    def device(self):
        """Returns the device and device_id"""
        # Add if clause to check device exists
        if (self.symbol.type == self.scanner.NAME and self.devices.get_device(self.symbol.id)):
            device_id = self.symbol.id
            device = self.devices.get_device(device_id)
            self.symbol = self.scanner.get_symbol()
            return [device, device_id]
        else:
            if self.symbol.type == self.scanner.NAME:
                self.error(self.network.DEVICE_ABSENT)
            else:
                self.error(self.NAME_EXPECTED)
            return [None, None]

    def device_port(self, device):
        """Takes a device as an input and returns port_id"""
        if (device is not None and self.symbol.type == self.scanner.NAME):
            if (self.symbol.id in device.inputs or self.symbol.id in device.outputs):
                port_id = self.symbol.id
                self.symbol = self.scanner.get_symbol()
                return port_id
            else:
                self.error(self.network.PORT_ABSENT)
        elif device is None:
            self.error(self.network.DEVICE_ABSENT)
        else:
            self.error(self.NAME_EXPECTED)
        return [None, None]

    def arrow(self):
        """Checks if a symbol is an arrow"""
        if self.symbol.type == self.scanner.ARROW:
            self.symbol = self.scanner.get_symbol()
            return
        else:
            self.error(self.ARROW_EXPECTED)

    def semicolon(self):
        """Checks if a symbol is a dot"""
        if self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()
            self.scanner.temp_queue = []
            return
        else:
            self.error(self.SEMICOLON_EXPECTED)

    def number(self):
        """Checks and returns if a symbol is a number"""
        if (self.symbol.type == self.scanner.NUMBER):
            number_val = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            return number_val
        else:
            self.error(self.NUMBER_EXPECTED)

    def unnamed_device(self):
        """Checks name symbol does not correspond to named device and returns id"""
        if (self.symbol.type == self.scanner.NAME and not self.devices.get_device(self.symbol.id)):
            name_id = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            return name_id
        elif self.devices.get_device(self.symbol.id):
            self.error(self.devices.DEVICE_PRESENT)
        else:
            self.error(self.NAME_EXPECTED)

    def number_unnamed(self):
        """Check for a number/unnamed device and returns value and ID"""
        device_id = None
        number = self.number()
        if not self.error_bool:
            device_id = self.unnamed_device()
        return number, device_id

    def connect_keyword(self):
        """Checks for the CONNECT keyword and a valid connection label and attatches the 2 nodes"""
        self.scanner.temp_queue.append(self.symbol)
        self.symbol = self.scanner.get_symbol()
        connection = self.connection()
        if not self.error_bool:
            error_type = self.network.make_connection(
                *connection[0], *connection[1])
            if error_type != self.network.NO_ERROR:
                self.error(error_type)

        while not self.error_bool and self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            connection = self.connection()
            if not self.error_bool:
                error_type = self.network.make_connection(
                    *connection[0], *connection[1])
                if error_type != self.network.NO_ERROR:
                    self.error(error_type)

        if not self.error_bool:
            self.semicolon()
        return True

    def and_keyword(self):
        """Checks for the AND keyword and creates and gate"""
        self.scanner.temp_queue.append(self.symbol)
        self.symbol = self.scanner.get_symbol()
        no_inputs, device_id = self.number_unnamed()
        if not self.error_bool:
            error_type = self.devices.make_device(
                device_id, self.devices.AND, no_inputs)
            if error_type != self.devices.NO_ERROR:
                self.error(error_type)

        while not self.error_bool and self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            no_inputs, device_id = self.number_unnamed()
            if not self.error_bool:
                error_type = self.devices.make_device(
                    device_id, self.devices.AND, no_inputs)
                if error_type != self.devices.NO_ERROR:
                    self.error(error_type)
        if not self.error_bool:
            self.semicolon()
        return True

    def nand_keyword(self):
        """Checks for the NAND keyword and creates nand gate"""
        self.scanner.temp_queue.append(self.symbol)
        self.symbol = self.scanner.get_symbol()
        no_inputs, device_id = self.number_unnamed()
        if not self.error_bool:
            error_type = self.devices.make_device(
                device_id, self.devices.NAND, no_inputs)
            if error_type != self.devices.NO_ERROR:
                self.error(error_type)

        while not self.error_bool and self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            no_inputs, device_id = self.number_unnamed()
            if not self.error_bool:
                error_type = self.devices.make_device(
                    device_id, self.devices.NAND, no_inputs)
                if error_type != self.devices.NO_ERROR:
                    self.error(error_type)
        if not self.error_bool:
            self.semicolon()
        return True

    def or_keyword(self):
        """Checks for the OR keyword and creates or gate"""
        self.scanner.temp_queue.append(self.symbol)
        self.symbol = self.scanner.get_symbol()
        no_inputs, device_id = self.number_unnamed()
        if not self.error_bool:
            error_type = self.devices.make_device(
                device_id, self.devices.OR, no_inputs)
            if error_type != self.devices.NO_ERROR:
                self.error(error_type)

        while not self.error_bool and self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            no_inputs, device_id = self.number_unnamed()
            if not self.error_bool:
                error_type = self.devices.make_device(
                    device_id, self.devices.OR, no_inputs)
                if error_type != self.devices.NO_ERROR:
                    self.error(error_type)
        if not self.error_bool:
            self.semicolon()

        return True

    def nor_keyword(self):
        """Checks for the NOR keyword and creates nor gate"""
        self.scanner.temp_queue.append(self.symbol)
        self.symbol = self.scanner.get_symbol()
        no_inputs, device_id = self.number_unnamed()
        if not self.error_bool:
            error_type = self.devices.make_device(
                device_id, self.devices.NOR, no_inputs)
            if error_type != self.devices.NO_ERROR:
                self.error(error_type)

        while not self.error_bool and self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            no_inputs, device_id = self.number_unnamed()
            if not self.error_bool:
                error_type = self.devices.make_device(
                    device_id, self.devices.NOR, no_inputs)
                if error_type != self.devices.NO_ERROR:
                    self.error(error_type)
        if not self.error_bool:
            self.semicolon()
        return True

    def switch_keyword(self):
        """Checks for the SWITCH keyword and creates switch"""
        self.scanner.temp_queue.append(self.symbol)
        self.symbol = self.scanner.get_symbol()
        state, device_id = self.number_unnamed()
        if not self.error_bool:
            # Default switch is at 0
            error_type = self.devices.make_device(
                device_id, self.devices.SWITCH, state)
            if error_type != self.devices.NO_ERROR:
                self.error(error_type)

        while not self.error_bool and self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            state, device_id = self.number_unnamed()
            if not self.error_bool:
                # Default switch is at 0
                error_type = self.devices.make_device(
                    device_id, self.devices.SWITCH, state)
                if error_type != self.devices.NO_ERROR:
                    self.error(error_type)
        if not self.error_bool:
            self.semicolon()

        return True

    def xor_keyword(self):
        """Checks for the XOR keyword and creates xor gate"""
        self.scanner.temp_queue.append(self.symbol)
        self.symbol = self.scanner.get_symbol()
        device_id = self.unnamed_device()
        if not self.error_bool:
            # Default switch is at 0
            error_type = self.devices.make_device(device_id, self.devices.XOR)
            if error_type != self.devices.NO_ERROR:
                self.error(error_type)

        while not self.error_bool and self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            device_id = self.unnamed_device()
            if not self.error_bool:
                # Default switch is at 0
                error_type = self.devices.make_device(
                    device_id, self.devices.XOR)
                if error_type != self.devices.NO_ERROR:
                    self.error(error_type)
        if not self.error_bool:
            self.semicolon()

        return True

    def dtype_keyword(self):
        """Checks for the XOR keyword and creates xor gate"""
        self.scanner.temp_queue.append(self.symbol)
        self.symbol = self.scanner.get_symbol()
        device_id = self.unnamed_device()
        if not self.error_bool:
            # Default switch is at 0
            error_type = self.devices.make_device(
                device_id, self.devices.D_TYPE)
            if error_type != self.devices.NO_ERROR:
                self.error(error_type)

        while not self.error_bool and self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            device_id = self.unnamed_device()
            if not self.error_bool:
                # Default switch is at 0
                error_type = self.devices.make_device(
                    device_id, self.devices.DTYPE)
                if error_type != self.devices.NO_ERROR:
                    self.error(error_type)

        if not self.error_bool:
            self.semicolon()
        return True

    def monitor_keyword(self):
        """Checks for MONITOR keyword and creates monitor"""
        self.scanner.temp_queue.append(self.symbol)
        self.symbol = self.scanner.get_symbol()
        device_id, port_id = self.node()
        if not self.error_bool:
            error_type = self.monitors.make_monitor(device_id, port_id)
            if error_type != self.monitors.NO_ERROR:
                self.error(error_type)

        while not self.error_bool and self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            device_id, port_id = self.node()
            if not self.error_bool:
                error_type = self.monitors.make_monitor(device_id, port_id)
                if error_type != self.monitors.NO_ERROR:
                    self.error(error_type)

        if not self.error_bool:
            self.semicolon()
        return True

    def clock_keyword(self):
        """Checks for the CLOCK keyword and creates clock with specified half period"""
        self.scanner.temp_queue.append(self.symbol)
        self.symbol = self.scanner.get_symbol()
        half_period, device_id = self.number_unnamed()
        if not self.error_bool:
            self.devices.make_device(
                device_id, self.devices.CLOCK, half_period)

        while not self.error_bool and self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            half_period, device_id = self.number_unnamed()
            if not self.error_bool:
                self.devices.make_device(
                    device_id, self.devices.CLOCK, half_period)
        if not self.error_bool:
            self.semicolon()
        return True

    def error(self, error_code):
        """Adds error to count and skips to next semicolon/EOF"""
        stopping_symbol = self.scanner.COMMA
        self.error_bool = True
        self.error_count += 1
        self.display_error(error_code)
        while (self.symbol.type != self.scanner.SEMICOLON and self.symbol.type != self.scanner.EOF and self.symbol.type != stopping_symbol):
            self.symbol = self.scanner.get_symbol()
        if self.symbol.type == stopping_symbol:
            # Add held symbols to stack
            self.scanner.priority_queue = [i for i in self.scanner.temp_queue]
            self.scanner.temp_queue = []

        if self.symbol.type != self.scanner.EOF:
            self.symbol = self.scanner.get_symbol()

    def display_error(self, error_code):
        
        def underline_text(text, index):
            underline = ''
            for i, char in enumerate(text):
                if i == index:
                    underline += '\033[31;4m{}\033[0m'.format(char)
                else:
                    underline += char
            return (underline)

        def highlight_error(symbol):
            if symbol.linenum and symbol.linepos:
                print(symbol.linenum,len(self.scanner.input_file.readlines()))
                position = self.scanner.input_file.tell()
                self.scanner.input_file.seek(0)
                lines = self.scanner.input_file.readlines()
                line = lines[symbol.linenum]
                self.scanner.input_file.seek(position)
                return underline_text(line, symbol.linepos)
            else:
                return None

        return highlight_error(self.symbol)
        
        if error_code == self.NAME_EXPECTED:
            print('Error: Expected a Name')
        
        if error_code == self.SEMICOLON_EXPECTED:
            print('Error: Expected a Semicolon')

        if error_code == self.KEYWORD_EXPECTED:
            print('Error: Expected a Keyword')

        if error_code == self.NUMBER_EXPECTED:
            print('Error: Expected a Number')

        if error_code == self.ARROW_EXPECTED:
            print('Error: Expected a Arrow')

        if error_code == self.devices.INVALID_QUALIFIER:
            print('Error: Invalid Qualifer')

        if error_code == self.devices.NO_QUALIFIER:
            print('Error: No Qualifer')

        if error_code == self.devices.BAD_DEVICE:
            print('Error: Bad Device')

        if error_code == self.devices.QUALIFIER_PRESENT:
            print('Error: Qualifier Present')

        if error_code == self.devices.DEVICE_PRESENT:
            print('Error: Device Present')

        if error_code == self.monitors.NOT_OUTPUT:
            print('Error: Not an output')

        if error_code == self.monitors.MONITOR_PRESENT:
            print('Error: Monitor Present')

        if error_code == self.network.INPUT_TO_INPUT:
            print('Error: Connecting an input to input')

        if error_code == self.network.OUTPUT_TO_OUTPUT:
            print('Error: Connecting an output to output')

        if error_code == self.network.INPUT_CONNECTED:
            print('Error: Input connected')

        if error_code == self.network.PORT_ABSENT:
            print('Error: Port Absent')

        if error_code == self.network.DEVICE_ABSENT:
            print('Error: Device Absent')

        


            

