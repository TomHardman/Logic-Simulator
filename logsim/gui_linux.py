import wx
from gui_plotting_canvas import TraceCanvas
from gui_interactive_canvas import InteractiveCanvas
from gui_components import error_pop_up, DeviceMenu, RoundedScrollWindow, CustomDialog


class GuiLinux(wx.Frame):
    """
    Class that contains the framework for the Gui

    Parameters
    ----------
    title - the title of the Gui
    names - Names object to pass the names to the Gui
    devices - Devices object to pass the devices to the Gui
    network - Network object to pass the network to the Gui
    monitors - Monitors object to pass the monitors to the Gui

    Public Methods
    -----------
    on_size - Handles resize events

    on_menu - Handles the event when the user selects a menu item

    on_change_monitor_colour - Handles the event when the user presses the change trace colours button
                               by clearing the dictionary of colours in trace_canvas so they are reallocated

    on_run_button - Handles the event when the user presses the run button - on first run it causes the
                    continue button to appear in the GUI - on all runs it runs the simulation from scratch
                    for the specified number of cycles

    on_animate - Handles the event where the animate button is pressed

    on_tick - While animation is occurring, this function is called every time there is a tick to animate
              the logic circuit display and plotting of the monitor traces

    on_sash_position_change_side - Handles the event where the sash position of the window changes - this
                                   is used to constrain the sidebar to either appear displayed to an ideal
                                   size or completely retracted. Due to rendering issues on linux this sidebar
                                   is designed to only take these two positions and is not fully adjustable

    on_sash_position_change_canvas - Function that is redundant in nature but is bound to the sash position change
                                   event for the canvas UI window in order to avoid interference between the
                                   sash position change events for the two separate splitter windows

    on_continue_button - Handles the event when the user presses the continue button

    on_add_zap_button - Handles the event when the user presses the add/zap monitor button

    on_add_device_button - Handle the event when the user presses the add device button - will generate a
                           device menu pop up that allows the user to select the device type, characteristics
                           and name

    on_add_connection_button - Handles the event when the user presses the add connection button
                               and allows connections to be made between devices on the circuit canvas

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
        self.font_buttons = wx.Font(14, wx.FONTFAMILY_DEFAULT,   # font to be used for all buttons
                                    wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # Booleans used to stop other buttons from being executed during certain processes
        self.connection_constraint = False
        self.monitor_constraint = False
        self.animation_constraint = False

        # Configure the file menu
        fileMenu = wx.Menu()
        themeMenu = wx.Menu()
        menuBar = wx.MenuBar()

        themeMenu.Append(wx.ID_ANY, "Light")  # configure sub-menu for choosing colour theme
        themeMenu.Append(wx.ID_ANY, "Dark")
        self.light_id = themeMenu.FindItemByPosition(0).GetId()  # store Ids as instance variables for method access
        self.dark_id = themeMenu.FindItemByPosition(1).GetId()

        fileMenu.Append(wx.ID_EXIT, "&Exit")
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.AppendSubMenu(themeMenu, "&Theme")
        fileMenu.Append(wx.ID_ANY, "&Help")
        menuBar.Append(fileMenu, "&File")
        self.help_id = fileMenu.FindItemByPosition(3).GetId()
        self.SetMenuBar(menuBar)
        self.Maximize()

        # Set up panels to split window into canvas UI window and adjustable sidebar
        main_splitter = wx.SplitterWindow(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        sidebar = wx.Panel(main_splitter)  # set up sidebar
        sidebar.SetBackgroundColour(wx.Colour(200, 200, 200))
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        sidebar.SetSizer(sidebar_sizer)
        sidebar.SetMaxSize((100, -1))
        self.sidebar = sidebar

        canvas_window = wx.SplitterWindow(main_splitter)  # set up canvas window

        main_splitter.SplitVertically(canvas_window, sidebar)
        main_splitter.SetSashGravity(0.6)  # make sure sidebar displays properly when gui first opened
        main_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.on_sash_position_change_side)

        # Set up panels for splitting canvas UI into circuit display and plotting window
        plotting_ui = wx.Panel(canvas_window)  # panel for plotting traces
        plotting_ui.SetBackgroundColour(wx.Colour(200, 200, 200))
        plotting_sizer = wx.BoxSizer(wx.VERTICAL)
        plotting_ui.SetSizer(plotting_sizer)

        circuit_ui = wx.Panel(canvas_window)  # panel for displaying circuit
        circuit_ui.SetBackgroundColour(wx.Colour(200, 200, 200))
        circuit_sizer = wx.BoxSizer(wx.VERTICAL)
        circuit_ui.SetSizer(circuit_sizer)

        canvas_window.SplitHorizontally(circuit_ui, plotting_ui)
        canvas_window.SetSashGravity(0.65)
        canvas_window.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.on_sash_position_change_canvas)

        # Set up panels for sidebar
        # bg colour is set to that of parent panel so only the painted on rounded panel shape is visible
        panel_control = RoundedScrollWindow(sidebar, self)  # main control panel
        panel_control.SetScrollRate(10, 0)
        panel_control.SetBackgroundColour(panel_control.GetParent().GetBackgroundColour())
        control_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_control.SetSizer(control_sizer)

        panel_devices = RoundedScrollWindow(sidebar, self)  # panel for configuring devices
        panel_devices.SetBackgroundColour(panel_devices.GetParent().GetBackgroundColour())
        panel_devices.SetScrollRate(10, 0)
        device_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_devices.SetSizer(device_sizer)

        panel_monitors = RoundedScrollWindow(sidebar, self)  # panel for configuring monitors and traces
        panel_monitors.SetBackgroundColour(panel_monitors.GetParent().GetBackgroundColour())
        panel_monitors.SetScrollRate(10, 0)
        monitor_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_monitors.SetSizer(monitor_sizer)

        # Widgets and sizers for control panel
        cycle_text = wx.StaticText(panel_control, wx.ID_ANY, "Cycles:")
        cycle_text.SetFont(self.font_buttons)

        cycle_spin = wx.SpinCtrl(panel_control, wx.ID_ANY, str(self.cycles))
        font_cs = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        cycle_spin.SetFont(font_cs)

        run_button = wx.Button(panel_control, wx.ID_ANY, label="Run")
        run_button.SetFont(self.font_buttons)

        cycles_comp_text = wx.StaticText(panel_control, wx.ID_ANY, f"Cycles Completed: {self.cycles_completed}")
        cycles_comp_text.SetFont(self.font_buttons)

        animate_button = wx.Button(panel_control, wx.ID_ANY, "Animate", size=(120, 40))
        animate_button.SetFont(self.font_buttons)
        self.timer = wx.Timer(self)  # Create a timer object to be used for animation events

        cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)  # set up four horizontal sizers to be stacked vertically
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

        # Set some panels and sizers as instance variables to make them accessible to on_run_button method
        self.panel_control = panel_control
        self.run_sizer = run_sizer
        self.cycles_comp_text = cycles_comp_text

        # Event bindings control panel widgets
        run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        cycle_spin.Bind(wx.EVT_SPINCTRL, self.on_cycle_spin)
        animate_button.Bind(wx.EVT_BUTTON, self.on_animate)
        self.Bind(wx.EVT_TIMER, self.on_tick, self.timer)

        # Widgets and sizers for monitor panel
        monitor_title = wx.StaticText(panel_monitors, wx.ID_ANY, "Monitor Configuration:")
        monitor_title.SetFont(self.font_buttons)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer.Add(monitor_title, 1, wx.ALL, 10)

        add_zap_button = wx.Button(panel_monitors, wx.ID_ANY, "Add/Zap\nMonitors")
        colour_button = wx.Button(panel_monitors, wx.ID_ANY, "Change\nTrace Colours")
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
        device_title = wx.StaticText(panel_devices, wx.ID_ANY, "Device Configuration:")  # create title
        device_title.SetFont(self.font_buttons)
        device_sizer.Add(device_title, 1, wx.ALL, 10)

        add_button_d = wx.Button(panel_devices, wx.ID_ANY, "Add\nDevice")
        add_button_d.SetFont(self.font_buttons)
        add_button_d.SetInitialSize(wx.Size(150, 60))

        add_button_c = wx.Button(panel_devices, wx.ID_ANY, "Add\nConnections")
        add_button_c.SetFont(self.font_buttons)
        add_button_c.SetInitialSize(wx.Size(150, 60))

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)  # sizer for buttons
        button_sizer.Add(add_button_d, 0, wx.ALL, 10)
        button_sizer.Add(add_button_c, 0, wx.ALL, 10)
        device_sizer.Add(button_sizer, 1, wx.ALL | wx.ALIGN_CENTRE, 5)

        # event handling for widgets for device panel
        add_button_c.Bind(wx.EVT_BUTTON, self.on_add_connection_button)
        add_button_d.Bind(wx.EVT_BUTTON, self.on_add_device_button)

        # set certain objects as instance variables to allow method access
        self.panel_devices = panel_devices
        self.device_sizer = device_sizer
        self.add_button_d = add_button_d
        self.add_button_c = add_button_c

        # Add panels to sidebar sizer
        sidebar_sizer.Add(panel_control, 1, wx.EXPAND | wx.ALL, 10)
        sidebar_sizer.Add(panel_devices, 1, wx.EXPAND | wx.ALL, 10)
        sidebar_sizer.Add(panel_monitors, 1, wx.EXPAND | wx.ALL, 10)

        # Add canvas widgets - include as instance objects to allow method access
        self.trace_canvas = TraceCanvas(plotting_ui, devices, monitors)
        self.circuit_canvas = InteractiveCanvas(circuit_ui, self, devices, monitors, names, network)

        # Add canvases to respective panels
        plotting_sizer.Add(self.trace_canvas, 1, wx.EXPAND, 5)
        circuit_sizer.Add(self.circuit_canvas, 1, wx.EXPAND, 5)

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
        self.GetSizer().Layout()  # Ensure the splitter adjusts to the frame size
        event.Skip()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()

        if Id == wx.ID_EXIT:
            self.Close(True)

        if Id == wx.ID_ABOUT:
            # Display pop up giving information about Logsim
            icon = wx.Bitmap("/homes/th624/Documents/Logic-Simulator/logsim/doge.png", wx.BITMAP_TYPE_PNG)
            mb = CustomDialog(None, "Logic Simulator\nCreated by bd432, al2008, th624\n2023",
                              "About Logsim", icon)
            mb.ShowModal()
            mb.Destroy()

        if Id == self.light_id or Id == self.dark_id:  # if light mode or dark mode selected
            if Id == self.light_id:
                self.circuit_canvas.dark_mode = False
                self.trace_canvas.dark_mode = False
                self.dark_mode = False
                self.sidebar.SetBackgroundColour(wx.Colour(200, 200, 200))

                for panel in self.sidebar.GetChildren():  # iterate through panels
                    panel.SetBackgroundColour(wx.Colour(200, 200, 200))  # set background to grey
                    for widget in panel.GetChildren():  # iterate through widgets and set to light mode designs
                        if str(type(widget)).split('.')[-1].split("'")[0] == 'StaticText':
                            widget.SetForegroundColour(wx.BLACK)
                        if str(type(widget)).split('.')[-1].split("'")[0] == 'SpinCtrl':
                            widget.SetForegroundColour(wx.BLACK)
                        if str(type(widget)).split('.')[-1].split("'")[0] == 'Button':
                            widget.SetForegroundColour(wx.BLACK)

            if Id == self.dark_id:
                self.circuit_canvas.dark_mode = True
                self.trace_canvas.dark_mode = True
                self.dark_mode = True
                self.sidebar.SetBackgroundColour(wx.Colour(100, 80, 100))

                for panel in self.sidebar.GetChildren():  # iterate through panels
                    panel.SetBackgroundColour(wx.Colour(100, 80, 100))  # set background to grey
                    for widget in panel.GetChildren():  # iterate through widgets and set to dark mode designs
                        if str(type(widget)).split('.')[-1].split("'")[0] == 'StaticText':
                            widget.SetForegroundColour(wx.Colour(179, 179, 179))
                        if str(type(widget)).split('.')[-1].split("'")[0] == 'SpinCtrl':
                            widget.SetForegroundColour(wx.Colour(165, 105, 179))
                        if str(type(widget)).split('.')[-1].split("'")[0] == 'Button':
                            widget.SetForegroundColour(wx.Colour(100, 80, 100))

            self.circuit_canvas.init = False  # refresh canvases and self to change display
            self.circuit_canvas.Refresh()
            self.trace_canvas.init = False
            self.trace_canvas.monitor_colours.clear()
            self.trace_canvas.Refresh()
            self.Refresh()

    def on_change_monitor_colours(self, event):
        """Handles the event when the user presses the change trace colours button - clears the
        dictionary of colours in trace_canvas so they are reallocated"""
        self.trace_canvas.monitor_colours.clear()
        self.trace_canvas.Refresh()

    def on_run_button(self, event):
        """Handles the event when the user presses the run button - on first run it causes the continue
        button to appear in the GUI - on all runs it runs the simulation from scratch for the specified
        number of cycles"""
        if self.connection_constraint:
            error_pop_up('Finish adding connections before trying to execute another action')
            return
        if self.monitor_constraint:
            error_pop_up('Finish adding/zapping monitors before trying to execute another action')
            return
        if self.animation_constraint:
            error_pop_up('End animation before trying to execute another action')
            return

        if self.cycles is not None and self.cycles > 0:  # if the number of cycles provided is valid
            self.cycles_completed = 0
            self.monitors.reset_monitors()
            self.devices.cold_startup()

            for i in range(self.cycles):  # executes run for specified no. cycles
                if self.network.execute_network():
                    self.monitors.record_signals()
                    self.cycles_completed += 1

                else:  # raise error if there are unconnected devices
                    error_pop_up('Run failed to execute - please make sure all devices are connected')
                    return

            if self.first_run:  # adds continue button to GUI after first run has been executed
                self.first_run = False
                run_sizer = self.run_sizer
                panel_control = self.panel_control

                cont_button = wx.Button(panel_control, wx.ID_ANY, "Continue")
                cont_button.SetFont(self.font_buttons)
                cont_button.Bind(wx.EVT_BUTTON, self.on_continue_button)

                if self.dark_mode:
                    cont_button.SetForegroundColour(wx.Colour(100, 80, 100))

                run_sizer.Add(cont_button, 1, wx.ALL, 5)
                panel_control.Layout()

            self.cycles_comp_text.SetLabel(f"Cycles Completed: {self.cycles_completed}")
            self.trace_canvas.pan_x = 0  # autopan back to the beginning of the plot
            self.trace_canvas.init = False
            self.trace_canvas.Refresh()  # call plotting event for trace and circuit canvas
            self.circuit_canvas.Refresh()

        else:  # show error dialogue box if given cycle no. is not valid
            error_pop_up('Please select valid number of cycles greater than zero')

    def on_animate(self, event):
        """Handles the event where the animate button is pressed"""
        if self.connection_constraint:
            error_pop_up('Finish adding connections before trying to execute another action')
            return
        if self.monitor_constraint:
            error_pop_up('Finish adding/zapping monitors before trying to execute another action')
            return

        Id = event.GetId()
        button = self.FindWindowById(Id)
        lab = button.GetLabel()

        if lab == 'Animate':
            if self.cycles_completed == 0:  # perform cold startup if simulation is being run from scratch
                self.monitors.reset_monitors()
                self.devices.cold_startup()

            if self.network.execute_network():  # start animation if network can be executed successfully
                self.monitors.record_signals()
                self.cycles_completed += 1
                self.trace_canvas.continue_pan_reset = True  # changes pan to include far right of plot if necessary
                self.trace_canvas.Refresh()  # call plotting event for trace and circuit canvas
                self.circuit_canvas.Refresh()
                self.cycles_comp_text.SetLabel(f"Cycles Completed: {self.cycles_completed}")
                button.SetLabel('Stop')
                self.animation_constraint = True
                self.timer.Start(500)  # create timer object that calls on_tick function every 500ms

                if self.first_run:  # adds continue button to GUI after first run has been executed
                    self.first_run = False
                    run_sizer = self.run_sizer
                    panel_control = self.panel_control

                    cont_button = wx.Button(panel_control, wx.ID_ANY, "Continue")
                    cont_button.SetFont(self.font_buttons)
                    cont_button.Bind(wx.EVT_BUTTON, self.on_continue_button)

                    if self.dark_mode:
                        cont_button.SetForegroundColour(wx.Colour(100, 80, 100))

                    run_sizer.Add(cont_button, 1, wx.ALL, 5)
                    panel_control.Layout()

            else:
                error_pop_up('Run failed to execute - please make sure all devices are connected')

        elif lab == 'Stop':
            button.SetLabel('Animate')
            self.animation_constraint = False
            self.timer.Stop()

    def on_tick(self, event):
        """While animation is occurring, this function is called every time there is a tick to animate the logic
        circuit display and plotting of the monitor traces"""
        if self.network.execute_network():
            self.monitors.record_signals()
            self.cycles_completed += 1
            self.trace_canvas.continue_pan_reset = True # changes pan to include far right of plot if necessary
            self.trace_canvas.Refresh()  # call plotting event for trace and circuit canvas
            self.circuit_canvas.Refresh()
            self.cycles_comp_text.SetLabel(f"Cycles Completed: {self.cycles_completed}")

    def on_sash_position_change_side(self, event):
        """Handles the event where the sash position of the window changes - this
        is used to constrain the sidebar to either appear displayed to an ideal size
        or completely retracted. Due to rendering issues on linux this sidebar is
        designed to only take these two positions and is not fully adjustable"""
        Id = event.GetId()
        window = self.FindWindowById(Id)
        current_width = self.GetSize().GetWidth()
        current_position = window.GetSashPosition()

        min_sash_pos = current_width - 400  # set displayed position of sidebar
        max_sash_pos = current_width - 20   # set retracted position of sidebar

        # sidebar set back to displayed position if sash dragged out any further than this
        if current_position < min_sash_pos:
            window.SetSashPosition(min_sash_pos)

        # sidebar is set to retracted position if sash is dragged to the right of displayed position
        if current_position > min_sash_pos or current_position == 2:
            window.SetSashPosition(max_sash_pos)

    def on_sash_position_change_canvas(self, event):
        """Function that is redundant in nature but is bound to the sash position change event for
        the canvas UI window in order to avoid interference between the sash position change events
        for the two separate splitter windows"""
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
            error_pop_up('Finish adding connections before trying to execute another action')
            return
        if self.monitor_constraint:
            error_pop_up('Finish adding/zapping monitors before trying to execute another action')
            return
        if self.animation_constraint:
            error_pop_up('End animation before trying to execute another action')
            return

        if self.cycles > 0:  # if the number of cycles provided is valid
            for i in range(self.cycles):  # executes run for specified no. cycles
                if self.network.execute_network():
                    self.monitors.record_signals()
                    self.cycles_completed += 1
                    self.trace_canvas.continue_pan_reset = True  # changes pan to include far right of plot if necessary
                    self.trace_canvas.Refresh()  # call plotting event for trace and circuit canvas
                    self.circuit_canvas.Refresh()
                    self.cycles_comp_text.SetLabel(
                        f"Cycles Completed: {self.cycles_completed}")

        else:  # show error dialogue box if cycle no. is not valid
            error_pop_up('Please select valid number of cycles greater than zero')

    def on_add_zap_button(self, event):
        """Handle the event when the user presses the add monitor button"""
        if self.connection_constraint:
            error_pop_up('Finish adding connections before trying to execute another action')
            return
        if self.animation_constraint:
            error_pop_up('End animation before trying to execute another action')
            return

        Id = event.GetId()
        button = self.FindWindowById(Id)
        lab = button.GetLabel()

        if lab == 'Add/Zap\nMonitors':
            button.SetLabel('Stop')
            self.circuit_canvas.choose_monitor = True
            self.monitor_constraint = True

        elif lab == 'Stop':
            button.SetLabel('Add/Zap\nMonitors')
            self.circuit_canvas.choose_monitor = False
            self.monitor_constraint = False

    def on_add_device_button(self, event):
        """Handle the event when the user presses the add device button - will generate a device
        menu pop up that allows the user to select the device type, characteristics and name"""
        if self.connection_constraint:
            error_pop_up('Finish adding connections before trying to execute another action')
            return
        if self.monitor_constraint:
            error_pop_up('Finish adding/zapping monitors before trying to execute another action')
            return
        if self.animation_constraint:
            error_pop_up('End animation before trying to execute another action')
            return

        dev_menu = DeviceMenu(self, 'Device Menu', self.devices, self.circuit_canvas)  # create device menu pop-up
        dev_menu.ShowModal()
        dev_menu.Destroy()

    def on_add_connection_button(self, event):
        """Handle the event when the user presses the add connection button - allows connections
        to be made between devices on the circuit canvas until the button, which will read 'Stop'
        after being pressed initially, is pressed again."""
        if self.monitor_constraint:
            error_pop_up('Finish adding/zapping monitors before trying to execute another action')
            return
        if self.animation_constraint:
            error_pop_up('End animation before trying to execute another action')
            return

        Id = event.GetId()
        button = self.FindWindowById(Id)
        lab = button.GetLabel()

        if lab == 'Add\nConnections':
            button.SetLabel('Stop')
            self.circuit_canvas.connection_list = [True, None, None]  # allow connections to be made on circuit canvas
            self.circuit_canvas.Refresh()
            self.connection_constraint = True

        elif lab == 'Stop':
            button.SetLabel('Add\nConnections')
            self.circuit_canvas.connection_list = [False, None, None]
            self.circuit_canvas.temp_connection = None
            self.circuit_canvas.Refresh()
            self.connection_constraint = False
