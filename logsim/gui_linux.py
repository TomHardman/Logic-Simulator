from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

import wx
import os
import builtins

from gui_plotting_canvas import TraceCanvas
from gui_interactive_canvas import InteractiveCanvas
from gui_components import error_pop_up, DeviceMenu, RoundedScrollWindow, \
    CustomDialog


class GuiLinux(wx.Frame):
    """
    Class that contains the framework for the Gui

    Parameters
    ----------
    title: the title of the Gui
    names: Names object to pass the names to the Gui
    devices: Devices object to pass the devices to the Gui
    network: Network object to pass the network to the Gui
    monitors: Monitors object to pass the monitors to the Gui

    Public Methods
    -----------
    on_size: Handles resize events

    on_menu: Handles the event when the user selects a menu item

    on_change_monitor_colour:
        Handles the event when the user presses the change trace colours
        button by clearing the dictionary of colours in trace_canvas
        so they are reallocated

    on_run_button:
        Handles the event when the user presses the run button - on
        first run it causes the continue button to appear in the GUI -
        on all runs it runs the simulation from scratch for the
        specified number of cycles

    on_animate:
        Handles the event where the animate button is pressed begins
        animation of plotting and circuit display until button, which
        will now display stop, is pressed again

    on_tick:
        While animation is occurring, this function is called every time
        there is a tick to animate the logic circuit display and
        plotting of the monitor traces cycle by cycle.

    on_sash_position_change_side:
        Handles the event where the sash position of the window changes
        - this is used to constrain the sidebar to either appear
        displayed to an ideal size or completely retracted.
        Due to rendering issues with the rounded panels on
        linux this sidebar is designed to only take these two positions
        and is not fully adjustable

    on_sash_position_change_canvas:
        Function that is redundant in nature but is bound to the sash
        position change event for the canvas UI window in order to avoid
        interference between the sash position change events for the two
        separate splitter windows

    on_continue_button: Handles the event when the user presses
                         the continue button

    on_add_zap_button:
        Handle the event when the user presses the add monitor
        button - allows monitors to be added/zapped on the circuit
        canvas until the button, which will read 'Stop' after being
        pressed initially, is pressed again.

    on_add_device_button:
        Handle the event when the user presses the add device button -
        will generate a device menu pop up that allows the user to
        select the device type, characteristics and name

    on_add_connection_button:
        Handles the event when the user presses the add connection
        button and allows connections to be made between devices on the
        circuit canvas

    """

    def __init__(self, title, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Initialise instance variables
        self.devices = devices
        self.names = names
        self.monitors = monitors
        self.network = network
        self.dark_mode = False
        self.first_run = True
        self.cycles = 10
        self.cycles_completed = 0
        self.font_buttons = wx.Font(
            14, wx.FONTFAMILY_DEFAULT,    # font to be used for all buttons
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.retracted_sidebar = False
        self.resizing = False

        # Booleans used to stop other events being triggered
        # during certain processes
        self.connection_constraint = False
        self.monitor_constraint = False
        self.animation_constraint = False

        # Configure the file menu
        fileMenu = wx.Menu()
        themeMenu = wx.Menu()
        menuBar = wx.MenuBar()

        # set up locale for language options
        self.locale = wx.Locale(wx.LANGUAGE_CHINESE_SIMPLIFIED)
        self.locale.AddCatalog('translate')
        builtins.__dict__['_'] = wx.GetTranslation
        print(self.locale.GetCanonicalName())

        # sub-menu for choosing colour theme
        themeMenu.Append(wx.ID_ANY, _("Light"))
        themeMenu.Append(wx.ID_ANY, _("Dark"))

        fileMenu.Append(wx.ID_EXIT, _("&Exit"))
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.AppendSubMenu(themeMenu, _("&Theme"))
        fileMenu.Append(wx.ID_ANY, _("&Save Circuit"))
        fileMenu.Append(wx.ID_ANY, _("&Load Circuit"))
        menuBar.Append(fileMenu, _("&Menu"))
        self.SetMenuBar(menuBar)
        self.SetMinSize((900, 766))
        self.Maximize()

        # store Ids as instance variables for method access
        self.light_id = themeMenu.FindItemByPosition(0).GetId()
        self.dark_id = themeMenu.FindItemByPosition(1).GetId()
        self.save_id = fileMenu.FindItemByPosition(3).GetId()
        self.load_id = fileMenu.FindItemByPosition(4).GetId()

        # Set up panels to split window into
        # canvas UI window and adjustable sidebar
        main_splitter = wx.SplitterWindow(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        sidebar = wx.Panel(main_splitter)  # set up sidebar
        sidebar.SetBackgroundColour(wx.Colour(200, 200, 200))
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        sidebar.SetSizer(sidebar_sizer)
        sidebar.SetMaxSize((100, -1))
        self.sidebar = sidebar

        # set up canvas window and make sure side bar displays properly
        # when gui is first opened
        canvas_window = wx.SplitterWindow(main_splitter)
        main_splitter.SplitVertically(canvas_window, sidebar)
        main_splitter.SetSashGravity(0.6)
        main_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED,
                           self.on_sash_position_change_side)
        self.main_splitter = main_splitter

        # Set up panels for splitting canvas UI into circuit display and 
        # monitor trace display and make instance variables for access
        plotting_ui = wx.Panel(canvas_window)  # panel for plotting traces
        plotting_ui.SetBackgroundColour(wx.Colour(200, 200, 200))
        plotting_sizer = wx.BoxSizer(wx.VERTICAL)
        plotting_ui.SetSizer(plotting_sizer)
        self.plotting_ui = plotting_ui
        self.plotting_sizer = plotting_sizer

        circuit_ui = wx.Panel(canvas_window)  # panel for displaying circuit
        circuit_ui.SetBackgroundColour(wx.Colour(200, 200, 200))
        circuit_sizer = wx.BoxSizer(wx.VERTICAL)
        circuit_ui.SetSizer(circuit_sizer)
        self.circuit_ui = circuit_ui
        self.circuit_sizer = circuit_sizer

        canvas_window.SplitHorizontally(circuit_ui, plotting_ui)
        canvas_window.SetSashGravity(0.65)
        canvas_window.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED,
                           self.on_sash_position_change_canvas)
        self.canvas_window = canvas_window

        # Set up panels for sidebar - bg colour is set to that of parent panel
        # so only the painted on rounded panel shape is visible
        panel_control = RoundedScrollWindow(sidebar, self)
        panel_control.SetBackgroundColour(
            panel_control.GetParent().GetBackgroundColour())
        control_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_control.SetSizer(control_sizer)

        panel_devices = RoundedScrollWindow(sidebar, self)
        panel_devices.SetBackgroundColour(
            panel_devices.GetParent().GetBackgroundColour())
        device_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_devices.SetSizer(device_sizer)

        panel_monitors = RoundedScrollWindow(sidebar, self)
        panel_monitors.SetBackgroundColour(
            panel_monitors.GetParent().GetBackgroundColour())
        monitor_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_monitors.SetSizer(monitor_sizer)

        # Widgets and sizers for control panel
        cycle_text = wx.StaticText(panel_control, wx.ID_ANY, _("Cycles:"))
        cycle_text.SetFont(self.font_buttons)

        cycle_spin = wx.SpinCtrl(panel_control, wx.ID_ANY, str(self.cycles))
        font_cs = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                          wx.FONTWEIGHT_LIGHT)
        cycle_spin.SetFont(font_cs)

        run_button = wx.Button(panel_control, wx.ID_ANY, label=_("Run"))
        run_button.SetFont(self.font_buttons)

        cycles_comp_text = wx.StaticText(
            panel_control, wx.ID_ANY,
            f"Cycles Completed: {self.cycles_completed}")
        cycles_comp_text.SetFont(self.font_buttons)

        animate_button = wx.Button(panel_control, wx.ID_ANY,
                                   _("Animate"), size=(120, 40))
        animate_button.SetFont(self.font_buttons)
        self.animate_button = animate_button
        self.timer = wx.Timer(self)  # timer object to be used for animation

        # set up four horizontal sizers to be stacked vertically
        cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycle_sizer.Add(cycle_text, 1, wx.ALL, 5)
        cycle_sizer.Add(cycle_spin, 1, wx.ALL, 5)

        cycles_comp_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycles_comp_sizer.Add(cycles_comp_text, 1, wx.ALL | wx.ALIGN_CENTER, 5)

        animate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        animate_sizer.Add(animate_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        run_sizer = wx.BoxSizer(wx.HORIZONTAL)
        run_sizer.Add(run_button, 1, wx.ALL, 5)

        control_sizer.Add(cycle_sizer, 1, wx.ALL, 5)
        control_sizer.Add(run_sizer, 1, wx.ALL | wx.ALIGN_CENTRE, 5)
        control_sizer.Add(animate_sizer, 1, wx.ALL | wx.ALIGN_CENTRE, 5)
        control_sizer.Add(cycles_comp_sizer, 1, wx.ALL | wx.ALIGN_CENTRE, 5)

        # Set some panels and sizers as instance variables to
        # make them accessible to on_run_button method
        self.panel_control = panel_control
        self.run_sizer = run_sizer
        self.cycles_comp_text = cycles_comp_text

        # Event bindings for control panel widgets
        run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        cycle_spin.Bind(wx.EVT_SPINCTRL, self.on_cycle_spin)
        animate_button.Bind(wx.EVT_BUTTON, self.on_animate)
        self.Bind(wx.EVT_TIMER, self.on_tick, self.timer)

        # Widgets and sizers for monitor panel
        monitor_title = wx.StaticText(panel_monitors, wx.ID_ANY,
                                      _("Monitor Configuration:"))
        monitor_title.SetFont(self.font_buttons)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer.Add(monitor_title, 1, wx.ALL, 10)

        add_zap_button = wx.Button(panel_monitors, wx.ID_ANY,
                                   _("Add/Zap\nMonitors"))
        colour_button = wx.Button(panel_monitors, wx.ID_ANY,
                                  _("Change\nTrace Colours"))
        add_zap_button.SetFont(self.font_buttons)
        colour_button.SetFont(self.font_buttons)

        add_zap_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_zap_sizer.Add(add_zap_button, 1, wx.ALL | wx.ALIGN_CENTRE, 10)
        add_zap_sizer.Add(colour_button, 1, wx.ALL | wx.ALIGN_CENTRE, 10)

        monitor_sizer.Add(title_sizer, 1, wx.ALL, 5)
        monitor_sizer.Add(add_zap_sizer, 1, wx.ALL | wx.ALIGN_CENTRE, 5)

        add_zap_button.Bind(wx.EVT_BUTTON, self.on_add_zap_button)
        colour_button.Bind(wx.EVT_BUTTON, self.on_change_monitor_colours)

        self.panel_monitors = panel_monitors

        # Widgets and sizers for device panel
        device_title = wx.StaticText(panel_devices, wx.ID_ANY,
                                     _("Device Configuration:"))
        device_title.SetFont(self.font_buttons)
        device_sizer.Add(device_title, 1, wx.ALL, 10)

        add_button_d = wx.Button(panel_devices, wx.ID_ANY, _("Add\nDevice"))
        add_button_d.SetFont(self.font_buttons)
        add_button_d.SetInitialSize(wx.Size(150, 60))

        add_button_c = wx.Button(panel_devices, wx.ID_ANY, _("Add\nConnections"))
        add_button_c.SetFont(self.font_buttons)
        add_button_c.SetInitialSize(wx.Size(150, 60))

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)  # sizer for buttons
        button_sizer.Add(add_button_d, 0, wx.ALL, 10)
        button_sizer.Add(add_button_c, 0, wx.ALL, 10)
        device_sizer.Add(button_sizer, 1, wx.ALL | wx.ALIGN_CENTRE, 5)

        # event bindings for widgets for device panel
        add_button_c.Bind(wx.EVT_BUTTON, self.on_add_connection_button)
        add_button_d.Bind(wx.EVT_BUTTON, self.on_add_device_button)

        # set certain objects as class variables to allow method access
        self.panel_devices = panel_devices
        self.device_sizer = device_sizer
        self.add_button_d = add_button_d
        self.add_button_c = add_button_c

        # Add panels to sidebar sizer
        sidebar_sizer.Add(panel_control, 1, wx.EXPAND | wx.ALL, 10)
        sidebar_sizer.Add(panel_devices, 1, wx.EXPAND | wx.ALL, 10)
        sidebar_sizer.Add(panel_monitors, 1, wx.EXPAND | wx.ALL, 10)

        # Add canvas widgets - include as instance variables for method access
        self.trace_canvas = TraceCanvas(self.plotting_ui, devices, monitors)
        self.circuit_canvas = InteractiveCanvas(self.circuit_ui, self, devices,
                                                monitors, names, network)

        # Add canvases to respective panels
        self.plotting_sizer.Add(self.trace_canvas, 1, wx.EXPAND, 5)
        self.circuit_sizer.Add(self.circuit_canvas, 1, wx.EXPAND, 5)

        # Configure main sizer layout
        main_sizer.Add(main_splitter, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MENU, self.on_menu)

        self.Layout()
        self.Centre()

        # Event handling:
    def on_size(self, event):
        """Handle resize events"""
        self.GetSizer().Layout()  # Ensure splitter adjusts to the frame size
        size = self.GetSize()
        self.resizing = True

        event.Skip()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()

        if Id == wx.ID_EXIT:
            self.Close(True)

        if Id == wx.ID_ABOUT:
            # Display pop up giving information about Logsim
            icon = wx.Bitmap("doge.png", wx.BITMAP_TYPE_PNG)
            mb = CustomDialog(
                None, _("Logic Simulator \nCreated by bd432, al2008, th624\n2023"),
                _("About Logsim"), icon)
            mb.ShowModal()
            mb.Destroy()

        if Id == self.save_id:
            circuit_string = self.circuit_canvas.create_file_string()
            dialog = wx.FileDialog(self, message=_("Choose a file location"),
                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            
            if dialog.ShowModal() == wx.ID_OK:
                file_path = dialog.GetPath()
                text_file = open(file_path, 'w')
                text_file.write(circuit_string)
            
            dialog.Destroy()
            

        if Id == self.load_id:
            circuit_string = self.circuit_canvas.create_file_string()
            dialog = wx.FileDialog(self, message=_("Choose a file to load"),
                    style=wx.FD_OPEN)
            
            if dialog.ShowModal() == wx.ID_OK:
                file_path = dialog.GetPath()
                _, file_extension = os.path.splitext(file_path)
                if file_extension.lower() != ".txt":
                    error_pop_up(_('Circuit file must be .txt'))
                    return
                text_file = open(file_path)

                names = Names()
                devices = Devices(names)
                network = Network(names, devices)
                monitors = Monitors(names, devices, network)
                scanner = Scanner(file_path, names)
                parser = Parser(names, devices, network, monitors, scanner)
                
                if parser.parse_network():
                    self.load_circuit(names, devices, network, monitors)
                else:
                    error_pop_up(_('Circuit could not be loaded from file'))
            
            dialog.Destroy()
        
        # if light mode or dark mode selected
        if Id == self.light_id or Id == self.dark_id:
            if Id == self.light_id:
                self.circuit_canvas.dark_mode = False
                self.trace_canvas.dark_mode = False
                self.dark_mode = False
                self.sidebar.SetBackgroundColour(wx.Colour(200, 200, 200))

                # iterate through panels in sidebar set bg colour to grey
                # and then iterate through widgets and set to light mode design
                for panel in self.sidebar.GetChildren():
                    panel.SetBackgroundColour(wx.Colour(200, 200, 200))
                    for widget in panel.GetChildren():
                        if str(type(widget)).split('.')[-1].split("'")[0] \
                                == 'StaticText':
                            widget.SetForegroundColour(wx.BLACK)
                        if str(type(widget)).split('.')[-1].split("'")[0] \
                                == 'SpinCtrl':
                            widget.SetForegroundColour(wx.BLACK)
                        if str(type(widget)).split('.')[-1].split("'")[0] \
                                == 'Button':
                            widget.SetForegroundColour(wx.BLACK)

            if Id == self.dark_id:
                self.circuit_canvas.dark_mode = True
                self.trace_canvas.dark_mode = True
                self.dark_mode = True
                self.sidebar.SetBackgroundColour(wx.Colour(100, 80, 100))

                # iterate through panels in sidebar set bg colour to dark pink
                # and then iterate through widgets and set to dark mode design
                for panel in self.sidebar.GetChildren():
                    panel.SetBackgroundColour(wx.Colour(100, 80, 100))
                    for widget in panel.GetChildren():
                        if str(type(widget)).split('.')[-1].split("'")[0] \
                                == 'StaticText':
                            widget.\
                                SetForegroundColour(wx.Colour(179, 179, 179))
                        if str(type(widget)).split('.')[-1].split("'")[0] \
                                == 'SpinCtrl':
                            widget.\
                                SetForegroundColour(wx.Colour(165, 105, 179))
                        if str(type(widget)).split('.')[-1].split("'")[0] \
                                == 'Button':
                            widget.\
                                SetForegroundColour(wx.Colour(100, 80, 100))

            # refresh canvases and self to update display
            self.circuit_canvas.init = False
            self.circuit_canvas.Refresh()
            self.trace_canvas.init = False
            self.trace_canvas.monitor_colours.clear()
            self.trace_canvas.Refresh()
            self.Refresh()

    def on_change_monitor_colours(self, event):
        """Handles the event when the user presses the change trace
        colours button - clears the dictionary of colours in
        trace_canvas so they are reallocated"""
        self.trace_canvas.monitor_colours.clear()
        self.trace_canvas.Refresh()

    def on_run_button(self, event):
        """Handles the event when the user presses the run button -
        on first run it causes the continue button to appear in the GUI
        - on all runs it runs the simulation from scratch for the
        specified number of cycles"""
        if self.connection_constraint:
            error_pop_up(_('Finish adding connections'
                         'before trying to execute another action'))
            return
        if self.monitor_constraint:
            error_pop_up(_('Finish adding/zapping monitors '
                         'before trying to execute another action'))
            return
        if self.animation_constraint:
            error_pop_up(_('End animation before '
                         'trying to execute another action'))
            return

        # if the number of cycles provided is valid
        if self.cycles is not None and self.cycles > 0:
            self.cycles_completed = 0
            self.monitors.reset_monitors()
            self.devices.cold_startup()

            # execute run for specified no. cycles
            for i in range(self.cycles):
                if self.network.execute_network() == self.network.NO_ERROR:
                    self.monitors.record_signals()
                    self.cycles_completed += 1

                # show error messages if run fails
                elif self.network.execute_network() == \
                        self.network.OSCILLATING:
                    error_pop_up(_('Run failed to execute - network oscillating'))
                    return
                elif self.network.execute_network() == \
                        self.network.INPUTS_NOT_CONNECTED:
                    error_pop_up(_('Run failed to execute - make sure all '
                                 'devices are connected'))
                    return

            # adds continue button to GUI after first run has been executed
            if self.first_run:
                self.first_run = False
                run_sizer = self.run_sizer
                panel_control = self.panel_control

                cont_button = wx.Button(panel_control, wx.ID_ANY, _("Continue"))
                cont_button.SetFont(self.font_buttons)
                cont_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
                self.cont_button = cont_button  # to allow deletion of button

                if self.dark_mode:
                    cont_button.SetForegroundColour(wx.Colour(100, 80, 100))

                run_sizer.Add(cont_button, 1, wx.ALL, 5)
                panel_control.Layout()

            self.cycles_comp_text.SetLabel(
                f"{_('Cycles Completed')}: {self.cycles_completed}")
            self.trace_canvas.pan_x = 0  # autopan back to beginning of plot
            self.trace_canvas.init = False
            self.trace_canvas.Refresh()  # call plotting event for canvases
            self.circuit_canvas.Refresh()

        else:  # show error dialogue box if given cycle no. is not valid
            error_pop_up(_('Please select valid '
                         'number of cycles greater than zero'))

    def on_animate(self, event):
        """Handles the event where the animate button is pressed -
        begins animation of plotting and circuit display until button,
        which will now display stop, is pressed again"""
        if self.connection_constraint:
            error_pop_up(_('Finish adding connections '
                         'before trying to execute another action'))
            return
        if self.monitor_constraint:
            error_pop_up(_('Finish adding/zapping monitors '
                         'before trying to execute another action'))
            return

        Id = event.GetId()
        button = self.FindWindowById(Id)
        lab = button.GetLabel()

        if lab == _('Animate'):
            # perform cold startup if simulating from scratch
            if self.cycles_completed == 0:
                self.monitors.reset_monitors()
                self.devices.cold_startup()

            # start animation if network can be executed successfully
            # run network for one cycle
            error_code = self.network.execute_network()
            if error_code == self.network.NO_ERROR:
                self.monitors.record_signals()
                self.cycles_completed += 1
                self.trace_canvas.continue_pan_reset = True
                self.trace_canvas.Refresh()
                self.circuit_canvas.Refresh()
                self.cycles_comp_text.SetLabel(
                    f"{_('Cycles Completed')}: {self.cycles_completed}")
                button.SetLabel(_('Stop'))
                self.animation_constraint = True
                # create timer object that calls on_tick every 500ms
                self.timer.Start(500)

                # adds continue button to GUI if this is the first run
                if self.first_run:
                    self.first_run = False
                    run_sizer = self.run_sizer
                    panel_control = self.panel_control

                    cont_button = wx.Button(panel_control, wx.ID_ANY,
                                            _("Continue"))
                    cont_button.SetFont(self.font_buttons)
                    cont_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
                    self.cont_button = cont_button

                    # if in dark mode set button to dark mode style
                    if self.dark_mode:
                        cont_button.\
                            SetForegroundColour(wx.Colour(100, 80, 100))

                    run_sizer.Add(cont_button, 1, wx.ALL, 5)
                    panel_control.Layout()

            # show error messages if run fails
            elif error_code == self.network.OSCILLATING:
                error_pop_up(_('Run failed to execute - network oscillating'))
                return
            elif error_code == self.network.INPUTS_NOT_CONNECTED:
                error_pop_up(_('Run failed to execute - make sure all '
                             'devices are connected'))
                return

        elif lab == _('Stop'):
            button.SetLabel(_('Animate'))
            self.animation_constraint = False
            self.timer.Stop()

    def on_tick(self, event):
        """While animation is occurring, this function is called every
        time there is a tick to animate the logic circuit display and
        plotting of the monitor traces"""
        # execute network for one cycle on tick then update canvases
        # and update cycles completed text widget
        error_code = self.network.execute_network()
        if error_code == self.network.NO_ERROR:
            self.monitors.record_signals()
            self.cycles_completed += 1
            # change pan to include far right of plot if necessary
            self.trace_canvas.continue_pan_reset = True
            self.trace_canvas.Refresh()
            self.circuit_canvas.Refresh()
            self.cycles_comp_text.SetLabel(
                f"{_('Cycles Completed')}: {self.cycles_completed}")

        # show error messages if run fails
        elif error_code == self.network.OSCILLATING:
            error_pop_up(_('Run failed to execute - network oscillating'))
            self.animate_button.SetLabel(_('Animate'))
            self.animation_constraint = False
            self.timer.Stop()
            return
        elif error_code == self.network.INPUTS_NOT_CONNECTED:
            error_pop_up(_('Run failed to execute - make sure all '
                         'devices are connected'))
            self.animate_button.SetLabel(_('Animate'))
            self.animation_constraint = False
            self.timer.Stop()
            return

    def on_sash_position_change_side(self, event):
        """Handles the event where the sash position of the window
        changes - this is used to constrain the sidebar to either appear
        displayed to an ideal size or completely retracted. Due to
        rendering issues  with the rounded panels on linux this sidebar
        is designed to only take these two positions and is not fully
        adjustable"""
        Id = event.GetId()
        window = self.FindWindowById(Id)
        current_width = self.GetSize().GetWidth()
        current_position = window.GetSashPosition()

        min_sash_pos = current_width - 400  # set displayed position of sidebar
        max_sash_pos = current_width - 15   # set retracted position of sidebar

        # sidebar set back to displayed position if sash dragged out any 
        # further than displayed position or dragged to left when retracted
        if current_position < min_sash_pos or current_position<current_width-20 and self.retracted_sidebar==True:
            window.SetSashPosition(min_sash_pos)
            self.retracted_sidebar = False

        # sidebar is set to retracted position if sash is
        # dragged to the right of displayed position
        elif current_position > min_sash_pos:
            window.SetSashPosition(max_sash_pos)
            self.retracted_sidebar = True

        if self.resizing:
            window.SetSashPosition(max_sash_pos)
            self.resizing = False
        

    def on_sash_position_change_canvas(self, event):
        """Function that is redundant in nature but is bound to the sash
        position change event for the canvas UI window in order to avoid
        interference between the sash position change events for the two
        separate splitter windows"""
        pass

    def on_cycle_spin(self, event):
        """Handle the event when the user changes the no. cycles"""
        Id = event.GetId()
        widget = self.FindWindowById(Id)
        self.cycles = widget.GetValue()  # read value from widget
        event.Skip()

    def on_continue_button(self, event):
        """Handle the event when the user presses the continue button"""
        if self.connection_constraint:
            error_pop_up(_('Finish adding connections '
                         'before trying to execute another action'))
            return
        if self.monitor_constraint:
            error_pop_up(_('Finish adding/zapping monitors '
                         'before trying to execute another action'))
            return
        if self.animation_constraint:
            error_pop_up(_('End animation before '
                         'trying to execute another action'))
            return

        if self.cycles > 0:  # if the number of cycles provided is valid
            # execute network for one cycle on tick then update canvases
            # and update cycles completed text widget
            for i in range(self.cycles):
                error_code = self.network.execute_network()
                if error_code == self.network.NO_ERROR:
                    self.monitors.record_signals()
                    self.cycles_completed += 1
                    # change pan to include far right of plot if necessary
                    self.trace_canvas.continue_pan_reset = True
                    self.trace_canvas.Refresh()
                    self.circuit_canvas.Refresh()
                    self.cycles_comp_text.SetLabel(
                        f"{_('Cycles Completed')}: {self.cycles_completed}")

                # show error messages if run fails
                elif error_code == \
                        self.network.OSCILLATING:
                    error_pop_up(_('Run failed to execute - network oscillating'))
                    return
                elif error_code == \
                        self.network.INPUTS_NOT_CONNECTED:
                    error_pop_up(_('Run failed to execute - make sure all '
                                 'devices are connected'))
                    return

        else:  # show error dialogue box if cycle no. is not valid
            error_pop_up(_('Please select valid '
                         'number of cycles greater than zero'))

    def on_add_zap_button(self, event):
        """Handle the event when the user presses the add monitor
        button - allows monitors to be added/zapped on the circuit
        canvas until the button, which will read 'Stop' after being
        pressed initially, is pressed again."""
        if self.connection_constraint:
            error_pop_up(_('Finish adding connections '
                         'before trying to execute another action'))
            return
        if self.animation_constraint:
            error_pop_up(_('End animation before '
                         'trying to execute another action'))
            return

        Id = event.GetId()
        button = self.FindWindowById(Id)
        lab = button.GetLabel()

        if lab == _('Add/Zap\nMonitors'):
            button.SetLabel(_('Stop'))
            # allow monitors to be added/zapped  by clicking ports on
            # the circuit canvas
            self.circuit_canvas.choose_monitor = True
            self.monitor_constraint = True

        elif lab == _('Stop'):
            button.SetLabel(_('Add/Zap\nMonitors'))
            # stop monitors being added/zapped
            self.circuit_canvas.choose_monitor = False
            self.monitor_constraint = False

    def on_add_device_button(self, event):
        """Handle the event when the user presses the add device button
        - will generate a device menu pop up that allows the user to
        select the device type, characteristics and name"""
        if self.connection_constraint:
            error_pop_up(_('Finish adding connections '
                         'before trying to execute another action'))
            return
        if self.monitor_constraint:
            error_pop_up(_('Finish adding/zapping monitors '
                         'before trying to execute another action'))
            return
        if self.animation_constraint:
            error_pop_up(_('End animation before trying to '
                         'execute another action'))
            return

        # create device menu pop-up
        dev_menu = DeviceMenu(self, _('Device Menu'),
                              self.devices, self.circuit_canvas)
        dev_menu.ShowModal()
        dev_menu.Destroy()

    def on_add_connection_button(self, event):
        """Handle the event when the user presses the add connection
        button - allows connections to be made between devices on the
        circuit canvas until the button, which will read 'Stop' after
        being pressed initially, is pressed again."""
        if self.monitor_constraint:
            error_pop_up(_('Finish adding/zapping monitors '
                         'before trying to execute another action'))
            return
        if self.animation_constraint:
            error_pop_up(_('End animation before '
                         'trying to execute another action'))
            return

        Id = event.GetId()
        button = self.FindWindowById(Id)
        lab = button.GetLabel()

        if lab == _('Add\nConnections'):
            button.SetLabel(_('Stop'))
            # allow connections to be made on circuit canvas
            self.circuit_canvas.connection_list = [True, None, None]
            self.circuit_canvas.Refresh()
            self.connection_constraint = True

        elif lab == _('Stop'):
            button.SetLabel(_('Add\nConnections'))
            # stop connections from being made on circuit canvas
            self.circuit_canvas.connection_list = [False, None, None]
            self.circuit_canvas.temp_connection = None
            self.circuit_canvas.Refresh()
            self.connection_constraint = False

    def load_circuit(self, names, devices, network, monitors):
        '''Function that reconfigures the GUI canvases and instance variables
        when a new circuit is successfully loaded from the file menu'''
        if not self.first_run:
            self.cont_button.Destroy()

        self.devices = devices
        self.names = names
        self.monitors = monitors
        self.network = network
        self.first_run = True
        self.cycles = 10
        self.cycles_completed = 0

        self.plotting_sizer.Detach(self.trace_canvas)
        self.circuit_sizer.Detach(self.circuit_canvas)
        self.trace_canvas.Destroy()
        self.circuit_canvas.Destroy()
        
        self.trace_canvas = TraceCanvas(self.plotting_ui, devices, monitors)
        self.circuit_canvas = InteractiveCanvas(self.circuit_ui, self, devices,
                                                monitors, names, network)
        self.trace_canvas.dark_mode = self.dark_mode
        self.circuit_canvas.dark_mode = self.dark_mode

        self.plotting_sizer.Add(self.trace_canvas, 1, wx.EXPAND, 5)
        self.circuit_sizer.Add(self.circuit_canvas, 1, wx.EXPAND, 5)

        self.Layout()
        self.trace_canvas.Refresh()
        self.circuit_canvas.Refresh()
        self.SetSize(self.GetSize().GetWidth()-10, self.GetSize().GetHeight()-10)
        self.cycles_comp_text.SetLabel(f'{_("Cycles Completed")}: {self.cycles_completed}')
        self.Maximize()

    def updateLanguage(self, lang):
        '''Update the language to the requested one'''
        # if an unsupported language is requested default to English
        if lang in self.supLang:
            selLang = self.supLang[lang]
        else:
            selLang = wx.LANGUAGE_ENGLISH

        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale

        # create a locale object for this language
        self.locale = wx.Locale(selLang)
        if self.locale.IsOk():
            self.locale.AddCatalog(appC.langDomain)
        else:
            self.locale = None