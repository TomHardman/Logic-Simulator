import wx
from canvas import MyGLCanvas
from wx.lib.agw.genericmessagedialog import GenericMessageDialog as GMD


class Gui_linux(wx.Frame):
    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))