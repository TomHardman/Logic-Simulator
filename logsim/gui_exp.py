import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT


class Gui_exp1(wx.Frame):

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
        #self.SetMenuBar(menuBar)wha

        #Configure widgets
        cb2 = wx.CheckBox(self, label='juicebox')

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer_main = wx.BoxSizer(wx.VERTICAL)
        side_sizer_1 = wx.BoxSizer(wx.VERTICAL)
        side_sizer_2 = wx.BoxSizer(wx.VERTICAL)

        for i in range(1, 10):
            cb = wx.CheckBox(self, wx.ID_ANY, label=f'Switch {i} high')
            if i % 2 == 0:
                side_sizer_1.Add(cb, 0, wx.EXPAND | wx.ALL, 5)
            else:
                cb.Destroy()


        main_sizer.Add(cb2, 5, wx.ALL, 5)
        side_sizer_main.Add(side_sizer_1, 5, wx.ALL, 5)
        side_sizer_main.Add(side_sizer_2, 5, wx.ALL, 5)
        main_sizer.Add(side_sizer_main, 1, wx.ALL, 5)

        self.SetSizer(main_sizer)
        self.Layout()


class Gui_exp(wx.Frame):
    def __init__(self,  title, path, names, devices, network, monitors):
        super().__init__(parent=None, title="Frame with Panel and Scrollable Panel", size=(800, 600))

        # Create a main sizer for the frame
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create a panel
        panel = wx.Panel(self)

        # Create a sizer for the panel
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add some widgets to the panel
        label = wx.StaticText(panel, label="This is the Panel")
        panel_sizer.Add(label, 0, wx.ALL, 10)

        # Set the sizer for the panel
        panel.SetSizer(panel_sizer)

        # Create a scrollable panel
        scrollable_panel = wx.ScrolledWindow(self)
        scrollable_panel.SetScrollRate(10, 10)
        scrollable_panel.SetBackgroundColour(wx.WHITE)

        # Create a sizer for the scrollable panel
        scrollable_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add some widgets to the scrollable panel
        for i in range(50):
            label = wx.StaticText(scrollable_panel, label=f"Item {i+1}")
            scrollable_sizer.Add(label, 0, wx.ALL, 5)

        # Set the sizer for the scrollable panel
        scrollable_panel.SetSizer(scrollable_sizer)

        # Add the panel and scrollable panel to the main sizer
        main_sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(scrollable_panel, 1, wx.EXPAND | wx.ALL, 10)

        # Set the main sizer for the frame
        self.SetSizer(main_sizer)



