 #!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage 
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import sys
import tempfile

import wx

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
#from gui_mac import Gui_mac
from gui_linux import Gui_linux
from gui_interactive import Gui_interactive
from network_fixture import create_network_fixture


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.
    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface: logsim.py <file path>")
    try:
        options, arguments = getopt.getopt(arg_list, "hcmtl:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    for option, path in options:
        print(arguments)
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()

        elif option == "-c":  # use the command line user interface
            scanner = Scanner(arguments[0], names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()
            print(parser.error_count)
            sys.exit()

        elif option == '-m':  # start up Mac GUI
            scanner = Scanner(arguments[0], names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the gui.Gui() class
                app = wx.App()
                gui = Gui_linux("Logic Simulator", path, names, devices, network,
                                monitors)
                gui.Show(True)
                app.MainLoop()

        elif option == '-l':  # start up linux GUI
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the gui.Gui() class
                app = wx.App()
                gui = Gui_linux("Logic Simulator", path, names, devices, network,
                                monitors)
                gui.Show(True)
                app.MainLoop()

        elif option == '-t':  # Run simulation of Drag and drop

            text ='SWITCH 1 SW1, 0 SW2; AND 2 G1; CONNECT SW1 > G1.I1, SW2 > G1.I2; MONITOR G1;'
 
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            # Write the string content to the temporary file
                temp_file.write(text)
                # Get the path of the temporary file
                path_2 = temp_file.name
            
            scanner = Scanner(path_2, names)
            parser = Parser(names, devices, network, monitors, scanner)

            # Initialise an instance of the gui.Gui() class
            if parser.parse_network():
                app = wx.App()  
                gui = Gui_interactive("Logic Simulator", path, names, devices, network,
                                    monitors)
                gui.Show(True)
                app.MainLoop()
            sys.exit()

        if len(arguments) != 1:  # wrong number of arguments
            print("Error: one file path required\n")
            print(usage_message)
            sys.exit()

        [path] = arguments
        scanner = Scanner(path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        if parser.parse_network():
            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui_linux("Logic Simulator", path, names, devices, network,
                      monitors)
            gui.Show(True)
            app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
