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
        options, arguments = getopt.getopt(arg_list, "hcumtl:")
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
        print(options)
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()

        elif option == "-c":  # use the command line user interface
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()
            sys.exit()

        elif option == '-m':  # run simulation of GUI with artificial network
            names, devices, network, monitors = create_network_fixture()

            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui_mac("Logic Simulator", path, names, devices, network,
                      monitors)
            gui.Show(True)
            app.MainLoop()

        elif option == '-l':  # run simulation of GUI with artificial network
            names, devices, network, monitors = create_network_fixture()

            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui_linux("Logic Simulator", path, names, devices, network,
                      monitors)
            gui.Show(True)
            app.MainLoop()

        elif option == '-t':  # Run simulation of Drag and drop
            names, devices, network, monitors = create_network_fixture()

            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui_interactive("Logic Simulator", path, names, devices, network,
                                  monitors) 
                                  
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
            gui = Gui_mac("Logic Simulator", path, names, devices, network,
                      monitors)
            gui.Show(True)
            app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
