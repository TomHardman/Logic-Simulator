import wx
from wx.lib.agw.genericmessagedialog import GenericMessageDialog as GMD
from canvas_copy import MyGLCanvas


class RoundedScrollWindow(wx.ScrolledWindow):
    """ Class that inherits from the wx.ScrolledWindow class to be used as a scrollable panel,
    however the OnPaint method has been rewritten to paint a rounded rectangular panel and
    hence display the panel as such. This needs the initial background colour of the panel
    to be set to that of its parent panel which can be done externally in the main GUI
    class

    Also contains method to set a border on the panel, however this is not very compatible
    with windows OS when resizing"""
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Panel_Border = False

    def set_border(self, border):
        if type(border) == bool:
            self.Panel_Border = border
        else:
            raise AttributeError(f"'border' must be type bool but got type {type(border)}")

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        rect = self.GetClientRect()
        x, y, width, height = rect

        w = 2
        x += w/2
        y += w/2
        width -= w
        height -= w

        # Draw filled rounded background
        radius = 10  # Adjust the radius for desired roundness
        background_color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        brush = wx.Brush(background_color)
        dc.SetBrush(brush)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRoundedRectangle(x, y, width, height, radius)

        if self.Panel_Border:  # Draw rounded border if set_border(True) has been called
            border_color = wx.Colour(72, 50, 168)  # Adjust the border colour as needed
            pen = wx.Pen(border_color, width=w)  # Adjust the border width as needed
            dc.SetPen(pen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRoundedRectangle(x, y, width, height, radius)

        event.Skip()


class Gui_linux(wx.Frame):

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Initialise instance variables
        self.devices = devices
        self.names = names
        self.monitors = monitors
        self.network = network

        self.first_run = True
        self.cycles = 10
        self.cycles_completed = 0

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        fileMenu.Append(wx.ID_ABOUT, "&About")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Configure sizers for top level layout structure
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        monitor_ui_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Set up panels to split window into main content window and adjustable sidebar
        splitter = wx.SplitterWindow(self)

        sidebar = wx.Panel(splitter)
        sidebar.SetBackgroundColour(wx.Colour(200, 200, 200))
        sidebar.SetSizer(sidebar_sizer)
        sidebar.SetMaxSize((100, -1))

        monitor_ui = wx.Panel(splitter)
        monitor_ui.SetBackgroundColour(wx.Colour(255, 255, 255))
        monitor_ui.SetSizer(monitor_ui_sizer)

        splitter.SplitVertically(monitor_ui, sidebar)
        splitter.SetSashGravity(0.7)
        splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.on_sash_position_change)

        # Set up panels for sidebar
        # bg colour is set to that of parent panel so only the painted on rounded panel shape is visible
        panel_control = RoundedScrollWindow(sidebar)
        panel_control.SetScrollRate(10, 0)
        panel_control.SetBackgroundColour(panel_control.GetParent().GetBackgroundColour())
        control_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_control.SetSizer(control_sizer)

        panel_switch = RoundedScrollWindow(sidebar)
        panel_switch.SetBackgroundColour(panel_switch.GetParent().GetBackgroundColour())
        panel_switch.SetScrollRate(0, 10)
        switch_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_switch.SetSizer(switch_sizer)

        panel_monitors = RoundedScrollWindow(sidebar)
        panel_monitors.SetBackgroundColour(panel_monitors.GetParent().GetBackgroundColour())
        panel_monitors.SetScrollRate(0, 10)
        monitor_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_monitors.SetSizer(monitor_sizer)

        # Widgets and sizers for control panel
        cycle_text = wx.StaticText(panel_control, wx.ID_ANY, "Cycles:")
        font_ct = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        cycle_text.SetFont(font_ct)

        cycle_spin = wx.SpinCtrl(panel_control, wx.ID_ANY, str(self.cycles))
        font_cs = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        cycle_spin.SetFont(font_cs)

        run_button = wx.Button(panel_control, wx.ID_ANY, "Run")
        font_rb = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        run_button.SetFont(font_rb)

        cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycle_sizer.Add(cycle_text, 1, wx.ALL, 5)
        cycle_sizer.Add(cycle_spin, 1, wx.ALL, 5)

        run_sizer = wx.BoxSizer(wx.HORIZONTAL)
        run_sizer.Add(run_button, 1, wx.ALL, 5)
        self.run_sizer = run_sizer  # creates sizer as instance variable so it can be accessed by methods

        control_sizer.Add(cycle_sizer, 1, wx.ALL, 5)
        control_sizer.Add(run_sizer, 1, wx.ALL, 5)

        # Set some panels and sizers as instance variables to make them accessible to on_run_button method
        self.panel_control = panel_control
        self.run_sizer = run_sizer

        # Bind control panel widgets
        run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        cycle_spin.Bind(wx.EVT_SPINCTRL, self.on_cycle_spin)

        # Widgets and sizers for monitor panel
        monitor_title = wx.StaticText(panel_monitors, wx.ID_ANY, "Monitor Configuration:")
        font_st = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        monitor_title.SetFont(font_st)
        monitor_sizer.Add(monitor_title, 1, wx.ALL, 10)

        add_button = wx.Button(panel_monitors, wx.ID_ANY, "Add Monitor")
        font_ab = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        add_button.SetFont(font_ab)

        zap_button = wx.Button(panel_monitors, wx.ID_ANY, "Zap Monitor")
        font_zb = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        zap_button.SetFont(font_zb)

        add_zap_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_zap_sizer.Add(add_button, 1, wx.ALL, 5)
        add_zap_sizer.Add(zap_button, 1, wx.ALL, 5)
        monitor_sizer.Add(add_zap_sizer)

        # Widgets and sizers for switch panel
        switch_title = wx.StaticText(panel_switch, wx.ID_ANY, "Switch Configuration:")
        font_st = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        switch_title.SetFont(font_st)
        switch_sizer.Add(switch_title, 1, wx.ALL, 10)

        switches = devices.find_devices(device_kind=devices.SWITCH)  # create array of switch IDs

        for id in switches:  # Add list of switch names with corresponding toggle buttons to panel
            name = names.get_name_string(id)
            switch_config_sizer = wx.BoxSizer(wx.HORIZONTAL)

            switch_dev = self.devices.get_device(id)
            state = switch_dev.switch_state  # Read state of current switch

            switch_txt = wx.StaticText(panel_switch, wx.ID_ANY, f'Switch {name}:')   # Text to go left of button
            font_sw_txt = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
            switch_txt.SetFont(font_sw_txt)

            # Set up toggle button for each switch depending on current state
            if state == 0:
                switch_button = wx.ToggleButton(panel_switch, id, label='Off')
            else:
                switch_button = wx.ToggleButton(panel_switch, id, label='On')
                switch_button.SetValue(True)

            switch_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_switch)
            switch_config_sizer.Add(switch_txt, 1, wx.ALL, 5)
            switch_config_sizer.Add(switch_button, 1, wx.ALL, 2)

            switch_sizer.Add(switch_config_sizer, 1, wx.ALL, 5)

        # Add panels to sidebar sizer
        sidebar_sizer.Add(panel_control, 1, wx.EXPAND | wx.ALL, 10)
        sidebar_sizer.Add(panel_switch, 2, wx.EXPAND | wx.ALL, 10)
        sidebar_sizer.Add(panel_monitors, 2, wx.EXPAND | wx.ALL, 10)

        # Define canvas widget for monitor UI
        self.trace_canvas = MyGLCanvas(monitor_ui, devices, monitors)

        # Add widgets for monitor UI
        monitor_ui_sizer.Add(self.trace_canvas, 2, wx.EXPAND | wx.ALL, 10)

        # Configure main sizer layout
        main_sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.Centre()

        # Event handling:

    def on_size(self, event):
        """Handle resize events"""
        # Ensure the splitter adjusts to the frame size
        self.GetSizer().Layout()
        event.Skip()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by bd432, al2008, th624\n2023",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_toggle_switch(self, event):
        """Handle the event when the user toggles a switch button"""
        Id = event.GetId()
        toggle_button = self.FindWindowById(Id)
        button_state = toggle_button.GetValue()  # Gets button state: True means button is currently toggled on

        if button_state:
            switch_state = 1  # Button toggled on means new switch state is to be set as 1
        else:
            switch_state = 0

        if self.devices.set_switch(Id, switch_state):  # Attempts to set switches to new state
            if button_state:
                toggle_button.SetLabel("On")

            if not button_state:
                toggle_button.SetLabel("Off")

        else:  # unfinished but should display error message on window
            pass

    def on_run_button(self, event):
        """Handles the event when the user presses the run button - on first run it causes the continue
        button to appear in the GUI - on all runs it runs the simulation from scratch for the specified
        number of cycles"""

        if self.cycles is not None and self.cycles > 0:  # if the number of cycles provided is valid
            if self.first_run:  # adds continue button to GUI after first run has been executed
                self.first_run = False
                run_sizer = self.run_sizer
                panel_control = self.panel_control

                cont_button = wx.Button(panel_control, wx.ID_ANY, "Continue")
                font_cb = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
                cont_button.SetFont(font_cb)
                cont_button.Bind(wx.EVT_BUTTON, self.on_continue_button)

                run_sizer.Add(cont_button, 1, wx.ALL, 5)
                panel_control.Layout()

            self.cycles_completed = 0
            self.monitors.reset_monitors()
            self.devices.cold_startup()

            for i in range(self.cycles):  # executes run for specified no. cycles
                if self.network.execute_network():
                    self.monitors.record_signals()
                    self.cycles_completed += 1

            self.trace_canvas.pan_x = 0
            self.trace_canvas.init = False
            self.trace_canvas.Refresh()  # call plotting even and pan axes back to zero

        else:  # show error dialogue box if cycle no. is not valid
            dlg = GMD(None, "Please select valid number of cycles greater than zero ",
                      "Error", wx.OK | wx.ICON_ERROR | 0x40)
            dlg.SetIcon(wx.ArtProvider.GetIcon(wx.ART_WARNING))
            dlg.ShowModal()
            dlg.Destroy()

    def on_sash_position_change(self, event):
        """Handles the event where the sash position of the window changes - this
        is used to implement an upper size limit on the sidebar"""
        Id = event.GetId()
        window = self.FindWindowById(Id)
        current_width = self.GetSize().GetWidth()
        current_position = window.GetSashPosition()

        min_sash_pos = current_width - 280
        max_sash_pos = current_width - 10

        if current_position < min_sash_pos:  # places max size on sidebar
            window.SetSashPosition(min_sash_pos)

        if current_position > max_sash_pos or current_position == 2:  # places min size on sidebar
            window.SetSashPosition(max_sash_pos)

    def on_cycle_spin(self, event):
        """Handle the event when the user changes the no. cycles"""
        Id = event.GetId()
        widget = self.FindWindowById(Id)
        self.cycles = widget.GetValue()
        event.Skip()

    def on_continue_button(self, event):
        """Handle the event when the user presses the continue button"""
        if self.cycles_completed == 0: # provide dialogue box error message
            pass

        if self.cycles > 0:  # if the number of cycles provided is valid
            for i in range(self.cycles):  # executes run for specified no. cycles
                if self.network.execute_network():
                    self.monitors.record_signals()
                    self.cycles_completed += 1
                    self.trace_canvas.Refresh()  # call plotting event

        else:  # show error dialogue box if cycle no. is not valid
            dlg = GMD(None, "Please select valid number of cycles greater than zero ",
                      "Error", wx.OK | wx.ICON_ERROR | 0x40)
            dlg.SetIcon(wx.ArtProvider.GetIcon(wx.ART_WARNING))
            dlg.ShowModal()
            dlg.Destroy()
