# Logic-Simulator
Logic simulator for GF2 software project

Navigate to the command directory logsim. Run logsim.py to launch with a text file input. The text file can also be loaded from within the GUI.

File description

names.py                - Contains the names class that stores and can retrieve IDs for all strings used.    
scanner.py              - Contains the scanner class that reads a txt input file and outputs symbols as dictated by the EBNF syntax.  
parse.py                - Contains the parser file which takes symbols from the scanner and creates the devices and network.  
devices.py              - Contains the devices class which creates and stores devices.  
network.py              - Contains the network class which has operations to make connections and execute the network.  
monitors.py             - Contains the monitors class which can add/remove and read monitors points.  
userint.py              - Command line interface (untouched).  
gui_components.py       - Contains four classes that are used for custom windows in the GUI and a function for raising error pop up messages.  
gui_interactive_canvas.py - Implements the interactive graphical user interface for the Logic Simulator.  
gui_linux.py            - Contains the framework for the GUI.  
gui_plotting_canvas.py  - contains the TraceCanvas class which is used for plotting monitor traces in the GUI.  
locales                 - Folder which contains the .po translation files for the chosen language options  
circuit_files           -Folder containing a number of text files which were used for testing the GUI.   
                         This folder is also designed for the user to be able to save their built circuits into.  
