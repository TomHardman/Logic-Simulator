import wx
from canvas import MyGLCanvas


class RoundedPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

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
        background_color = wx.WHITE
        brush = wx.Brush(background_color)
        dc.SetBrush(brush)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRoundedRectangle(x, y, width, height, radius)

        # Draw rounded border
        border_color = wx.Colour(72, 50, 168)  # Adjust the border colour as needed
        pen = wx.Pen(border_color, width=w)  # Adjust the border width as needed
        dc.SetPen(pen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRoundedRectangle(x, y, width, height, radius)

        event.Skip()


class RoundedScrollWindow(wx.ScrolledWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

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

        # Draw rounded border
        border_color = wx.Colour(72, 50, 168)  # Adjust the border colour as needed
        pen = wx.Pen(border_color, width=w)  # Adjust the border width as needed
        dc.SetPen(pen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRoundedRectangle(x, y, width, height, radius)

        event.Skip()


class Gui(wx.Frame):

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.Centre()

        # Configure sizers for top level layout structure
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        monitor_ui_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Set up panels to split window into main content window and adjustable sidebar
        splitter = wx.SplitterWindow(self)

        sidebar = wx.Panel(splitter)
        sidebar.SetBackgroundColour(wx.Colour(200, 200, 200))
        sidebar.SetSizer(sidebar_sizer)

        monitor_ui = wx.Panel(splitter)
        monitor_ui.SetBackgroundColour(wx.Colour(255, 255, 255))
        monitor_ui.SetSizer(monitor_ui_sizer)

        splitter.SplitVertically(monitor_ui, sidebar)
        splitter.SetSashGravity(0.2)

        # Set up panels for sidebar
        panel_run = RoundedPanel(sidebar)
        run_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_run.SetSizer(run_sizer)

        panel_switch = RoundedScrollWindow(sidebar)
        panel_switch.SetScrollRate(0, 10)
        switch_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_switch.SetSizer(switch_sizer)

        panel_monitors = RoundedScrollWindow(sidebar)
        panel_monitors.SetScrollRate(0, 10)
        monitor_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_monitors.SetSizer(monitor_sizer)

        # Widgets and sizers for run panel
        cycle_text = wx.StaticText(panel_run, wx.ID_ANY, "Cycles:")
        font_ct = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        cycle_text.SetFont(font_ct)

        cycle_spin = wx.SpinCtrl(panel_run, wx.ID_ANY, "10")
        font_cs = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        cycle_spin.SetFont(font_cs)

        run_button = wx.Button(panel_run, wx.ID_ANY, "Run")
        font_rb = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        run_button.SetFont(font_rb)

        cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycle_sizer.Add(cycle_text, 1, wx.ALL, 5)
        cycle_sizer.Add(cycle_spin, 1, wx.ALL, 5)

        run_sizer.Add(cycle_sizer, 1, wx.ALL, 5)
        run_sizer.Add(run_button, 1, wx.ALL, 5)

        # Widgets and sizers for switch panel
        switch_title = wx.StaticText(panel_switch, wx.ID_ANY, "Switch Configuration:")
        font_st = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        switch_title.SetFont(font_st)
        switch_sizer.Add(switch_title, 1, wx.ALL, 10)

        switches = devices.find_devices(device_kind = devices.SWITCH)  # create array of switch IDs

        for id in switches:  # Add list of switch names with corresponding toggle buttons to panel
            name = names.get_name_string(id)
            switch_config_sizer = wx.BoxSizer(wx.HORIZONTAL)

            switch_txt = wx.StaticText(panel_switch, wx.ID_ANY, f'Switch {name}:')
            font_sw_txt = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
            switch_txt.SetFont(font_sw_txt)

            switch_button = wx.ToggleButton(panel_switch, id, label='Off', size=(60, 20))
            switch_config_sizer.Add(switch_txt, 2, wx.ALL, 5)
            switch_config_sizer.Add(switch_button, 1, wx.ALL, 5)

            switch_sizer.Add(switch_config_sizer, 1, wx.ALL, 5)

        # Add panels to sidebar sizer
        sidebar_sizer.Add(panel_run, 1, wx.EXPAND | wx.ALL, 10)
        sidebar_sizer.Add(panel_switch, 2, wx.EXPAND | wx.ALL, 10)
        sidebar_sizer.Add(panel_monitors, 2, wx.EXPAND | wx.ALL, 10)

        # Define canvas widget for monitor UI
        canvas = MyGLCanvas(monitor_ui, devices, monitors)

        # Add widgets for monitor UI
        monitor_ui_sizer.Add(canvas, 2, wx.EXPAND | wx.ALL, 10)

        # Configure main sizer layout
        main_sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(main_sizer)