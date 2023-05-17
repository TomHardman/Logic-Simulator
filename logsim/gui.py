import wx


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
        side_sizer_main = wx.BoxSizer(wx.VERTICAL)

        # Set up panels for side sizer
        panel_test = wx.Panel(self)

        panel_run = RoundedPanel(self)
        run_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_run.SetSizer(run_sizer)

        panel_switch = wx.ScrolledWindow(self)
        panel_switch.SetScrollRate(10, 10)
        panel_switch.SetBackgroundColour(wx.WHITE)
        switch_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_switch.SetSizer(switch_sizer)

        panel_monitors = wx.ScrolledWindow(self)
        panel_monitors.SetScrollRate(10, 10)
        panel_monitors.SetBackgroundColour(wx.WHITE)
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

        # Add panels to side sizer
        side_sizer_main.Add(panel_run, 1, wx.EXPAND | wx.ALL, 10)
        side_sizer_main.Add(panel_switch, 2, wx.EXPAND | wx.ALL, 10)
        side_sizer_main.Add(panel_monitors, 2, wx.EXPAND | wx.ALL, 10)

        # Configure main sizer layout
        main_sizer.Add(panel_test, 2, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(side_sizer_main, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(main_sizer)