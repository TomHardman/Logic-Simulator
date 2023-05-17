import wx


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

        panel_run = wx.Panel(self)
        panel_run.SetBackgroundColour(wx.WHITE)
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

        # Widgets for run panel
        run_button = wx.Button(self, wx.ID_ANY, "Run")

        #run_sizer.Add(run_button, 1, wx.ALL, 5)

        # Add panels to side sizer
        side_sizer_main.Add(panel_run, 1, wx.EXPAND | wx.ALL, 10)
        side_sizer_main.Add(panel_switch, 2, wx.EXPAND | wx.ALL, 10)
        side_sizer_main.Add(panel_monitors, 2, wx.EXPAND | wx.ALL, 10)

        # Configure main sizer layout
        main_sizer.Add(panel_test, 2, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(side_sizer_main, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(main_sizer)