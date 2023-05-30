import wx
from wx.lib.agw.genericmessagedialog import GenericMessageDialog as GMD
from plotting_canvas import TraceCanvas
from gui_interactive import InteractiveCanvas
from wx.lib.buttons import GenButton


def error_pop_up(string):
    """Function used for creating error pop up windows in the Gui when an error is raised -
    takes one argument which is the string to be displayed in the pop up"""
    dlg = GMD(None, string, "Error", wx.OK | wx.ICON_ERROR | 0x40)
    dlg.SetIcon(wx.ArtProvider.GetIcon(wx.ART_WARNING))
    dlg.ShowModal()
    dlg.Destroy()


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
            raise AttributeError(
                f"'border' must be type bool but got type {type(border)}")

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

        # Draw rounded border if set_border(True) has been called
        if self.Panel_Border:
            # Adjust the border colour as needed
            border_color = wx.Colour(72, 50, 168)
            # Adjust the border width as needed
            pen = wx.Pen(border_color, width=w)
            dc.SetPen(pen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRoundedRectangle(x, y, width, height, radius)

        event.Skip()


class DeviceMenu(wx.Dialog):
    def __init__(self, parent, title, devices, canvas):
        wx.Dialog.__init__(self, parent, title=title)
        self.devices = devices
        self.device_chosen = None
        self.qualifier = None
        self.device_name = None
        self.font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.first_selection = True
        self.canvas = canvas
        self.devices_dict = {'CLOCK': self.devices.CLOCK, 'NAND': self.devices.NAND, 'SWITCH': self.devices.SWITCH,
                             'AND': self.devices.AND, 'NOR': self.devices.NOR, 'OR': self.devices.OR,
                             'XOR': self.devices.XOR, 'DTYPE': self.devices.D_TYPE}

        overall_sizer = wx.BoxSizer(wx.VERTICAL)  # Create main sizer
        self.SetSizer(overall_sizer)

        self.main_panel = wx.Panel(self)
        # Create main panel and relevant sizer
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(self.panel_sizer)
        overall_sizer.Add(self.main_panel, 1, wx.ALL, 5)

        self.choose_device()  # This takes the user initially to the choose device state

    def choose_device(self):
        """Function that creates the pop up window to choose the device type"""
        choices = ['AND', 'NAND', 'SWITCH', 'OR',
                   'NOR', 'XOR', 'CLOCK', 'DTYPE']  # choices for drop down menu
        device_txt = wx.StaticText(
            self.main_panel, wx.ID_ANY, 'Choose Device:')
        device_txt.SetFont(self.font)
        drop_down = wx.Choice(self.main_panel, wx.ID_ANY, choices=choices)
        drop_down.Bind(wx.EVT_CHOICE, self.on_drop_down)

        self.choose_dev_sizer = wx.BoxSizer(wx.VERTICAL)
        self.choose_dev_sizer.Add(device_txt, 1, wx.ALL | wx.ALIGN_LEFT, 5)
        self.choose_dev_sizer.Add(drop_down, 1, wx.ALL | wx.ALIGN_LEFT, 5)
        self.panel_sizer.Add(self.choose_dev_sizer, 1,
                             wx.ALL | wx.ALIGN_LEFT, 5)
        self.Layout()
        self.Fit()

    def choose_qualifier(self):
        """Function that creates the pop up window to choose the device qualifier - this
        function is not called if the device is an XOR or DTYPE"""
        if self.device_chosen == 'CLOCK':
            choose_txt = wx.StaticText(
                self.main_panel, wx.ID_ANY, 'Enter half period:')
            self.choose_ctrl = wx.SpinCtrl(
                self.main_panel, wx.ID_ANY, style=wx.SP_ARROW_KEYS, min=1, max=20)

        elif self.device_chosen == 'SWITCH':
            choose_txt = wx.StaticText(
                self.main_panel, wx.ID_ANY, 'Enter initial switch state:')
            self.choose_ctrl = wx.SpinCtrl(
                self.main_panel, wx.ID_ANY, style=wx.SP_ARROW_KEYS, min=0, max=1)
        else:
            choose_txt = wx.StaticText(
                self.main_panel, wx.ID_ANY, 'Enter number of inputs:')
            self.choose_ctrl = wx.SpinCtrl(
                self.main_panel, wx.ID_ANY, style=wx.SP_ARROW_KEYS, min=2, max=16)

        chosen_txt = wx.StaticText(
            self.main_panel, wx.ID_ANY, f' Device chosen: {self.device_chosen}')
        chosen_txt.SetFont(self.font)
        confirm_button_qual = wx.Button(self.main_panel, wx.ID_ANY, "Confirm")
        back_button_qual = wx.Button(self.main_panel, wx.ID_ANY, "Back")
        confirm_button_qual.Bind(wx.EVT_BUTTON, self.on_confirm_qual)
        back_button_qual.Bind(wx.EVT_BUTTON, self.on_back_qual)

        self.choose_qual_sizer = wx.BoxSizer(wx.VERTICAL)
        self.choose_qual_sizer.Add(
            chosen_txt, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_qual_sizer.Add(
            choose_txt, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_qual_sizer.Add(
            self.choose_ctrl, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_qual_sizer.Add(
            confirm_button_qual, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_qual_sizer.Add(
            back_button_qual, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.panel_sizer.Add(self.choose_qual_sizer, 0, wx.ALL, 5)
        self.Layout()
        self.Fit()

    def choose_name(self):
        """Function that creates the pop up window for entering the device name"""

        phrases = {'CLOCK': 'Half Period: ', 'NAND': 'Number of inputs: ', 'AND': 'Number of inputs: ',
                   'NOR': 'Number of inputs: ', 'OR': 'Number of inputs: ', 'SWITCH': 'Initial State: '}

        chosen_txt_dev = wx.StaticText(
            self.main_panel, wx.ID_ANY, f' Device chosen: {self.device_chosen}')
        chosen_txt_dev.SetFont(self.font)

        if self.device_chosen != 'XOR' and self.device_chosen != 'DTYPE':  # adds text to state qualifier if relevant
            chosen_txt_qual = wx.StaticText(self.main_panel, wx.ID_ANY,
                                            f' {phrases.get(self.device_chosen)}{self.qualifier}')
            chosen_txt_qual.SetFont(self.font)

        name_prompt = wx.StaticText(
            self.main_panel, wx.ID_ANY, 'Enter device name:')
        name_input = wx.TextCtrl(self.main_panel, wx.ID_ANY, size=(100, 40))
        confirm_button_name = wx.Button(self.main_panel, wx.ID_ANY, "Confirm")
        back_button_name = wx.Button(self.main_panel, wx.ID_ANY, "Back")
        confirm_button_name.Bind(wx.EVT_BUTTON, self.on_confirm_name)
        back_button_name.Bind(wx.EVT_BUTTON, self.on_back_name)
        name_input.Bind(wx.EVT_TEXT, self.on_name_entry)

        self.choose_name_sizer = wx.BoxSizer(wx.VERTICAL)
        self.choose_name_sizer.Add(
            chosen_txt_dev, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        if self.device_chosen != 'XOR' and self.device_chosen != 'DTYPE':
            self.choose_name_sizer.Add(
                chosen_txt_qual, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_name_sizer.Add(
            name_prompt, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_name_sizer.Add(
            name_input, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_name_sizer.Add(
            confirm_button_name, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_name_sizer.Add(
            back_button_name, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.panel_sizer.Add(self.choose_name_sizer, 0, wx.ALL, 5)
        self.Layout()
        self.Fit()

    def destroy_widgets_in_sizer(self, sizer):
        """Function to destroy all the widgets in a given sizer"""
        for child in sizer.GetChildren():
            widget = child.GetWindow()
            if widget is not None:
                widget.Destroy()

    def on_drop_down(self, event):
        Id = event.GetId()
        widget = self.FindWindowById(Id)

        self.device_chosen = widget.GetStringSelection()

        if self.first_selection and self.device_chosen:
            confirm_button_dev = wx.Button(
                self.main_panel, wx.ID_ANY, "Confirm")
            self.choose_dev_sizer.Add(
                confirm_button_dev, 1, wx.ALL | wx.ALIGN_LEFT, 5)
            confirm_button_dev.Bind(wx.EVT_BUTTON, self.on_confirm_dev)
            self.Layout()
            self.first_selection = False
        self.Fit()  # fit layout to widgets

    def on_confirm_dev(self, event):
        self.destroy_widgets_in_sizer(self.choose_dev_sizer)
        self.panel_sizer.Detach(self.choose_dev_sizer)

        if self.device_chosen == 'DTYPE' or self.device_chosen == 'XOR':
            self.choose_name()

        else:
            self.choose_qualifier()

    def on_confirm_qual(self, event):
        self.qualifier = self.choose_ctrl.GetValue()
        self.destroy_widgets_in_sizer(self.choose_qual_sizer)
        self.panel_sizer.Detach(self.choose_qual_sizer)
        self.choose_name()

    def on_confirm_name(self, event):
        if self.device_name[0].isalpha() and self.device_name.isalnum():
            if self.canvas.create_device(self.device_name, self.devices_dict[self.device_chosen], self.qualifier):
                self.EndModal(wx.ID_OK)

        else:
            error_pop_up('Please enter a valid name')

    def on_back_qual(self, event):
        self.destroy_widgets_in_sizer(self.choose_qual_sizer)
        self.panel_sizer.Detach(self.choose_qual_sizer)
        self.device_chosen = None
        self.first_selection = True
        self.choose_device()

    def on_back_name(self, event):
        self.destroy_widgets_in_sizer(self.choose_name_sizer)
        self.panel_sizer.Detach(self.choose_name_sizer)
        self.qualifier = None

        if self.device_chosen == 'DTYPE' or self.device_chosen == 'XOR':
            self.device_chosen = None
            self.first_selection = True
            self.choose_device()
        else:
            self.choose_qualifier()

    def on_name_entry(self, event):
        Id = event.GetId()
        widget = self.FindWindowById(Id)
        self.device_name = widget.GetValue()


class Gui_linux(wx.Frame):

    def __init__(self, title, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Initialise instance variables
        self.devices = devices
        self.names = names
        self.monitors = monitors
        self.network = network
        # these two booleans are used to stop other actions during adding of monitors/connections
        self.connection_constraint = False
        self.monitor_constraint = False
        self.first_run = True
        self.cycles = 10
        self.cycles_completed = 0

        self.font_buttons = wx.Font(
            14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # Configure the file menu
        fileMenu = wx.Menu()
        themeMenu = wx.Menu()
        menuBar = wx.MenuBar()

        themeMenu.Append(wx.ID_ANY, "Light")
        themeMenu.Append(wx.ID_ANY, "Dark")
        self.light_id = themeMenu.FindItemByPosition(0).GetId()
        self.dark_id = themeMenu.FindItemByPosition(1).GetId()

        fileMenu.Append(wx.ID_EXIT, "&Exit")
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.AppendSubMenu(themeMenu, "&Theme")
        fileMenu.Append(wx.ID_ANY, "&Help")
        menuBar.Append(fileMenu, "&File")
        self.help_id = fileMenu.FindItemByPosition(3).GetId()
        self.SetMenuBar(menuBar)
        self.Maximize()

        # Set up panels to split window into main UI window and adjustable sidebar
        main_splitter = wx.SplitterWindow(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        sidebar = wx.Panel(main_splitter)  # set up sidebar
        sidebar.SetBackgroundColour(wx.Colour(200, 200, 200))
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        sidebar.SetSizer(sidebar_sizer)
        sidebar.SetMaxSize((100, -1))

        canvas_window = wx.SplitterWindow(
            main_splitter)  # set up canvas window

        main_splitter.SplitVertically(canvas_window, sidebar)
        main_splitter.SetSashGravity(0.7)
        # main_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.on_sash_position_change)

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
        canvas_window.SetSashGravity(0.5)
        # canvas_window.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.on_sash_position_change)

        # Set up panels for sidebar
        # bg colour is set to that of parent panel so only the painted on rounded panel shape is visible
        panel_control = RoundedScrollWindow(sidebar)
        panel_control.SetScrollRate(10, 0)
        panel_control.SetBackgroundColour(
            panel_control.GetParent().GetBackgroundColour())
        control_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_control.SetSizer(control_sizer)

        panel_devices = RoundedScrollWindow(sidebar)
        panel_devices.SetBackgroundColour(
            panel_devices.GetParent().GetBackgroundColour())
        panel_devices.SetScrollRate(0, 10)
        device_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_devices.SetSizer(device_sizer)

        panel_monitors = RoundedScrollWindow(sidebar)
        panel_monitors.SetBackgroundColour(
            panel_monitors.GetParent().GetBackgroundColour())
        panel_monitors.SetScrollRate(0, 10)
        monitor_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_monitors.SetSizer(monitor_sizer)

        # Widgets and sizers for control panel
        cycle_text = wx.StaticText(panel_control, wx.ID_ANY, "Cycles:")
        cycle_text.SetFont(self.font_buttons)

        cycle_spin = wx.SpinCtrl(panel_control, wx.ID_ANY, str(self.cycles))
        font_cs = wx.Font(12, wx.FONTFAMILY_MODERN,
                          wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        cycle_spin.SetFont(font_cs)

        run_button = wx.Button(panel_control, wx.ID_ANY, "Run")
        run_button.SetFont(self.font_buttons)

        cycles_comp_text = wx.StaticText(
            panel_control, wx.ID_ANY, f"Cycles Completed: {self.cycles_completed}")
        cycles_comp_text.SetFont(self.font_buttons)

        cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycle_sizer.Add(cycle_text, 1, wx.ALL, 5)
        cycle_sizer.Add(cycle_spin, 1, wx.ALL, 5)

        cycles_comp_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycles_comp_sizer.Add(cycles_comp_text, 1, wx.ALL | wx.ALIGN_CENTER, 5)

        run_sizer = wx.BoxSizer(wx.HORIZONTAL)
        run_sizer.Add(run_button, 1, wx.ALL, 5)
        # creates sizer as instance variable so it can be accessed by methods
        self.run_sizer = run_sizer

        control_sizer.Add(cycle_sizer, 1, wx.ALL, 5)
        control_sizer.Add(run_sizer, 1, wx.ALL | wx.ALIGN_CENTRE, 5)
        control_sizer.Add(cycles_comp_sizer, 1, wx.ALL | wx.ALIGN_CENTRE, 5)

        # Set some panels and sizers as instance variables to make them accessible to on_run_button method
        self.panel_control = panel_control
        self.run_sizer = run_sizer
        self.cycles_comp_text = cycles_comp_text

        # Bind control panel widgets
        run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        cycle_spin.Bind(wx.EVT_SPINCTRL, self.on_cycle_spin)

        # Widgets and sizers for monitor panel
        monitor_title = wx.StaticText(
            panel_monitors, wx.ID_ANY, "Monitor Configuration:")
        font_st = wx.Font(14, wx.FONTFAMILY_DEFAULT,
                          wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        monitor_title.SetFont(font_st)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer.Add(monitor_title, 1, wx.ALL, 10)

        add_zap_button = wx.Button(
            panel_monitors, wx.ID_ANY, "Add/Zap\nMonitors")
        add_zap_button.SetFont(self.font_buttons)

        add_zap_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_zap_sizer.Add(add_zap_button, 1, wx.ALL | wx.ALIGN_CENTRE, 10)

        monitor_sizer.Add(title_sizer, 1, wx.ALL, 5)
        monitor_sizer.Add(add_zap_sizer, 1, wx.ALL | wx.ALIGN_CENTRE, 5)

        add_zap_button.Bind(wx.EVT_BUTTON, self.on_add_zap_button)

        # Widgets and sizers for device panel
        device_title = wx.StaticText(
            panel_devices, wx.ID_ANY, "Device Configuration:")  # create title
        device_title.SetFont(font_st)
        device_sizer.Add(device_title, 1, wx.ALL, 5)

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

        # set as instance variables to allow method access
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
        self.circuit_canvas = InteractiveCanvas(
            circuit_ui, self, devices, monitors, names, network)

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
        if Id == self.light_id:
            self.circuit_canvas.dark_mode = False
            self.circuit_canvas.init = False
            self.circuit_canvas.Refresh()
        if Id == self.dark_id:
            self.circuit_canvas.dark_mode = True
            self.circuit_canvas.init = False
            self.circuit_canvas.Refresh()

    def on_run_button(self, event):
        """Handles the event when the user presses the run button - on first run it causes the continue
        button to appear in the GUI - on all runs it runs the simulation from scratch for the specified
        number of cycles"""
        if self.connection_constraint:
            error_pop_up(
                'Finish adding connections before trying to execute another action')
            return

        if self.monitor_constraint:
            error_pop_up(
                'Finish adding/zapping monitors before trying to execute another action')
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
                    error_pop_up(
                        'Run failed to execute - please make sure all devices are connected')
                    return

            if self.first_run:  # adds continue button to GUI after first run has been executed
                self.first_run = False
                run_sizer = self.run_sizer
                panel_control = self.panel_control

                cont_button = wx.Button(panel_control, wx.ID_ANY, "Continue")
                cont_button.SetFont(self.font_buttons)
                cont_button.Bind(wx.EVT_BUTTON, self.on_continue_button)

                run_sizer.Add(cont_button, 1, wx.ALL, 5)
                panel_control.Layout()

            self.cycles_comp_text.SetLabel(
                f"Cycles Completed: {self.cycles_completed}")
            self.trace_canvas.pan_x = 0  # autopan back to the beginning
            self.trace_canvas.init = False
            self.trace_canvas.Refresh()  # call plotting event for trace and circuit canvas
            self.circuit_canvas.Refresh()

        else:  # show error dialogue box if cycle no. is not valid
            error_pop_up(
                'Please select valid number of cycles greater than zero')

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
        if self.connection_constraint:
            error_pop_up(
                'Finish adding connections before trying to execute another action')
            return

        if self.monitor_constraint:
            error_pop_up(
                'Finish adding/zapping monitors before trying to execute another action')
            return

        Id = event.GetId()
        widget = self.FindWindowById(Id)
        self.cycles = widget.GetValue()
        event.Skip()

    def on_continue_button(self, event):
        """Handle the event when the user presses the continue button"""
        if self.connection_constraint:
            error_pop_up(
                'Finish adding connections before trying to execute another action')
            return

        if self.monitor_constraint:
            error_pop_up(
                'Finish adding/zapping monitors before trying to execute another action')
            return

        if self.cycles > 0:  # if the number of cycles provided is valid
            for i in range(self.cycles):  # executes run for specified no. cycles
                if self.network.execute_network():
                    self.monitors.record_signals()
                    self.cycles_completed += 1
                    # changes pan to include far right of plot if necessary
                    self.trace_canvas.continue_pan_reset = True
                    self.trace_canvas.Refresh()  # call plotting event for trace and circuit canvas
                    self.circuit_canvas.Refresh()
                    self.cycles_comp_text.SetLabel(
                        f"Cycles Completed: {self.cycles_completed}")

        else:  # show error dialogue box if cycle no. is not valid
            error_pop_up(
                'Please select valid number of cycles greater than zero')

    def on_add_zap_button(self, event):
        """Handle the event when the user presses the add monitor button"""
        if self.connection_constraint:
            error_pop_up(
                'Finish adding connections before trying to execute another action')
            return

        Id = event.GetId()
        button = self.FindWindowById(Id)
        lab = button.GetLabel()

        if lab == 'Add/Zap\nMonitors':
            button.SetLabel('Stop')
            button.SetBackgroundColour(wx.Colour(157, 0, 0))
            self.circuit_canvas.choose_monitor = True
            self.monitor_constraint = True

        elif lab == 'Stop':
            button.SetLabel('Add/Zap\nMonitors')
            button.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.circuit_canvas.choose_monitor = False
            self.monitor_constraint = False

    def on_add_device_button(self, event):
        """Handle the event when the user presses the add device button"""
        if self.connection_constraint:
            error_pop_up(
                'Finish adding connections before trying to execute another action')
            return

        if self.monitor_constraint:
            error_pop_up(
                'Finish adding/zapping monitors before trying to execute another action')
            return

        dev_menu = DeviceMenu(self, 'Device Menu',
                              self.devices, self.circuit_canvas)
        dev_menu.ShowModal()
        dev_menu.Destroy()

    def on_add_connection_button(self, event):
        """Handle the event when the user presses the add connection button"""
        if self.monitor_constraint:
            error_pop_up(
                'Finish adding/zapping monitors before trying to execute another action')
            return

        Id = event.GetId()
        button = self.FindWindowById(Id)
        lab = button.GetLabel()

        if lab == 'Add\nConnections':
            button.SetLabel('Stop')
            button.SetBackgroundColour(wx.Colour(157, 0, 0))
            self.circuit_canvas.connection_list = [True, None, None]
            self.connection_constraint = True

        elif lab == 'Stop':
            button.SetLabel('Add\nConnections')
            button.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.circuit_canvas.connection_list = [False, None, None]
            self.circuit_canvas.temp_connection = None
            self.circuit_canvas.Refresh()
            self.connection_constraint = False
