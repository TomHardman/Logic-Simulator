import wx
from wx.lib.agw.genericmessagedialog import GenericMessageDialog as GMD
from plotting_canvas import TraceCanvas
from gui_interactive import InteractiveCanvas
from wx.lib.buttons import GenButton


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


class Gui_linux(wx.Frame):

    def __init__(self, title, path, names, devices, network, monitors):
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
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        fileMenu.Append(wx.ID_ABOUT, "&About")
        menuBar.Append(fileMenu, "&File")
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

    def on_run_button(self, event):
        """Handles the event when the user presses the run button - on first run it causes the continue
        button to appear in the GUI - on all runs it runs the simulation from scratch for the specified
        number of cycles"""
        if self.connection_constraint:
            self.error_pop_up(
                'Finish adding connections before trying to execute another action')
            return

        if self.monitor_constraint:
            self.error_pop_up(
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
                    self.error_pop_up(
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

            self.cycles_comp_text.SetLabel(f"Cycles Completed: {self.cycles_completed}")   
            self.trace_canvas.pan_x = 0  # autopan back to the beginning
            self.trace_canvas.init = False
            self.trace_canvas.Refresh()  # call plotting event for trace and circuit canvas
            self.circuit_canvas.Refresh()

        else:  # show error dialogue box if cycle no. is not valid
            self.error_pop_up(
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
            self.error_pop_up(
                'Finish adding connections before trying to execute another action')
            return

        if self.monitor_constraint:
            self.error_pop_up('Finish adding/zapping monitors before trying to execute another action')
            return

        Id = event.GetId()
        widget = self.FindWindowById(Id)
        self.cycles = widget.GetValue()
        event.Skip()

    def on_continue_button(self, event):
        """Handle the event when the user presses the continue button"""
        if self.connection_constraint:
            self.error_pop_up(
                'Finish adding connections before trying to execute another action')
            return

        if self.monitor_constraint:
            self.error_pop_up('Finish adding/zapping monitors before trying to execute another action')
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
            self.error_pop_up(
                'Please select valid number of cycles greater than zero')

    def on_add_zap_button(self, event):
        """Handle the event when the user presses the add monitor button"""
        if self.connection_constraint:
            self.error_pop_up(
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
            self.error_pop_up(
                'Finish adding connections before trying to execute another action')
            return

        if self.monitor_constraint:
            self.error_pop_up('Finish adding/zapping monitors before trying to execute another action')
            return

        Id = event.GetId()
        button = self.FindWindowById(Id)
        lab = button.GetLabel()

        if lab == 'Add\nDevice':
            button.SetLabel('Stop')
            button.SetBackgroundColour(wx.Colour(157, 0, 0))

        elif lab == 'Stop':
            button.SetLabel('Add\nDevice')
            button.SetBackgroundColour(wx.Colour(255, 255, 255))

    def on_add_connection_button(self, event):
        """Handle the event when the user presses the add connection button"""
        if self.monitor_constraint:
            self.error_pop_up('Finish adding/zapping monitors before trying to execute another action')
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

    def error_pop_up(self, string):
        dlg = GMD(None, string, "Error", wx.OK | wx.ICON_ERROR | 0x40)
        dlg.SetIcon(wx.ArtProvider.GetIcon(wx.ART_WARNING))
        dlg.ShowModal()
        dlg.Destroy()
