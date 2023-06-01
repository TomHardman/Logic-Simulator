import wx
from wx.lib.agw.genericmessagedialog import GenericMessageDialog as GMD


def error_pop_up(string):
    """Function used for creating error pop up windows in the Gui when an error is raised -
    takes one argument which is the string to be displayed in the pop up"""
    dlg = GMD(None, string, "Error", wx.OK | wx.ICON_ERROR | 0x40)
    dlg.SetIcon(wx.ArtProvider.GetIcon(wx.ART_WARNING))
    dlg.ShowModal()
    dlg.Destroy()


class CustomDialog(wx.Dialog):
    """Class that inherits  from the wx.Dialog class but creates a pop up box that
    supports the setting of custom bitmaps"""
    def __init__(self, parent, message, caption, bitmap):
        super().__init__(parent, title=caption)

        # Create the bitmap control to display the icon
        icon_bitmap = wx.StaticBitmap(self, wx.ID_ANY, bitmap)

        # Create the message text control
        message_text = wx.StaticText(self, wx.ID_ANY, message)

        # Create the OK button
        ok_button = wx.Button(self, wx.ID_OK, "OK")

        # Create a vertical box sizer to arrange the controls
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(icon_bitmap, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(message_text, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(ok_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Fit()


class RoundedScrollWindow(wx.ScrolledWindow):
    """
    Class that inherits from the wx.ScrolledWindow class to be used as a scrollable panel,
    however the OnPaint method has been rewritten to paint a rounded rectangular panel and
    hence display the panel as such. This needs the initial background colour of the panel
    to be set to that of its parent panel which can be done externally in the main GUI
    class

    Also contains method set_border set/remove a border on the panel, however this is not very compatible
    with windows OS or Linux OS when resizing
    """

    def __init__(self, parent, mother):
        super().__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Panel_Border = True
        self.mother = mother
        self.dark_mode = self.mother.dark_mode

    def set_border(self, border):
        """Function that is used to set a panel border by changing the value of the boolean"""
        if type(border) == bool:
            self.Panel_Border = border
        else:
            raise AttributeError(
                f"'border' must be type bool but got type {type(border)}")

    def OnPaint(self, event):
        """Handles paint events - when paint event is called it paints a panel with rounded corners
        and (if self.Panel_Border = True) a border on top of the original panel background"""
        self.dark_mode = self.mother.dark_mode
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        rect = self.GetClientRect()
        x, y, width, height = rect

        w = 3
        x += w/2
        y += w/2
        width -= w
        height -= w

        # Draw filled rounded background
        radius = 10  # Adjust the radius for desired roundness
        if not self.dark_mode:
            background_color = wx.WHITE
        else:
            background_color = wx.Colour(51, 51, 51)
        brush = wx.Brush(background_color)
        dc.SetBrush(brush)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRoundedRectangle(x, y, width, height, radius)

        # Draw rounded border if set_border(True) has been called
        if self.Panel_Border:
            # Adjust the border colour as needed
            if self.dark_mode:
                border_color = wx.Colour(165, 105, 179)
            else:
                border_color = wx.Colour(20, 50, 180)
            
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
        self.devices_dict = {'CLOCK': self.devices.CLOCK,
                             'NAND': self.devices.NAND,
                             'SWITCH': self.devices.SWITCH,
                             'AND': self.devices.AND, 'NOR': self.devices.NOR,
                             'OR': self.devices.OR,
                             'XOR': self.devices.XOR,
                             'DTYPE': self.devices.D_TYPE}

        overall_sizer = wx.BoxSizer(wx.VERTICAL)  # Create main sizer
        self.SetSizer(overall_sizer)

        self.main_panel = wx.Panel(self)  # Create main panel and its sizer
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(self.panel_sizer)
        overall_sizer.Add(self.main_panel, 1, wx.ALL, 5)

        # Take the user initially to the choose device state
        self.choose_device()

    def choose_device(self):
        """Function that creates the pop up window to choose the
        device type"""

        choices = ['AND', 'NAND', 'SWITCH', 'OR',  # choices for drop down
                   'NOR', 'XOR', 'CLOCK', 'DTYPE']
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
            choose_txt = wx.StaticText(self.main_panel, wx.ID_ANY,
                                       'Enter half period:')
            self.choose_ctrl = wx.SpinCtrl(self.main_panel, wx.ID_ANY,
                                           style=wx.SP_ARROW_KEYS, min=1,
                                           max=20)
        elif self.device_chosen == 'SWITCH':
            choose_txt = wx.StaticText(self.main_panel, wx.ID_ANY,
                                       'Enter initial switch state:')
            self.choose_ctrl = wx.SpinCtrl(self.main_panel, wx.ID_ANY,
                                           style=wx.SP_ARROW_KEYS, min=0,
                                           max=1)
        else:
            choose_txt = wx.StaticText(self.main_panel, wx.ID_ANY,
                                       'Enter number of inputs:')
            self.choose_ctrl = wx.SpinCtrl(self.main_panel, wx.ID_ANY,
                                           style=wx.SP_ARROW_KEYS, min=2,
                                           max=16)

        chosen_txt = wx.StaticText(self.main_panel, wx.ID_ANY,
                                   f' Device chosen: {self.device_chosen}')
        chosen_txt.SetFont(self.font)
        confirm_button_qual = wx.Button(self.main_panel, wx.ID_ANY, "Confirm")
        back_button_qual = wx.Button(self.main_panel, wx.ID_ANY, "Back")
        confirm_button_qual.Bind(wx.EVT_BUTTON, self.on_confirm_qual)
        back_button_qual.Bind(wx.EVT_BUTTON, self.on_back_qual)

        self.choose_qual_sizer = wx.BoxSizer(wx.VERTICAL)
        self.choose_qual_sizer.Add(chosen_txt, 0,
                                   wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_qual_sizer.Add(choose_txt, 0,
                                   wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_qual_sizer.Add(self.choose_ctrl, 0,
                                   wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_qual_sizer.Add(confirm_button_qual, 0,
                                   wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_qual_sizer.Add(back_button_qual, 0,
                                   wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.panel_sizer.Add(self.choose_qual_sizer, 0, wx.ALL, 5)
        self.Layout()
        self.Fit()

    def choose_name(self):
        """Function that creates the pop up window for entering the device name"""

        phrases = {'CLOCK': 'Half Period: ', 'NAND': 'Number of inputs: ',
                   'AND': 'Number of inputs: ', 'NOR': 'Number of inputs: ',
                   'OR': 'Number of inputs: ', 'SWITCH': 'Initial State: '}

        chosen_txt_dev = wx.StaticText(self.main_panel, wx.ID_ANY,
                                       f' Device chosen: {self.device_chosen}')
        chosen_txt_dev.SetFont(self.font)

        # add text to state chosen qualifier if relevant
        if self.device_chosen != 'XOR' and self.device_chosen != 'DTYPE':
            chosen_txt_qual = wx.StaticText(
                self.main_panel, wx.ID_ANY,
                f' {phrases.get(self.device_chosen)}{self.qualifier}')
            chosen_txt_qual.SetFont(self.font)

        name_prompt = wx.StaticText(self.main_panel, wx.ID_ANY,
                                    'Enter device name:')
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
            self.choose_name_sizer.Add(chosen_txt_qual, 0,
                                       wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_name_sizer.Add(name_prompt, 0,
                                   wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_name_sizer.Add(name_input, 0,
                                   wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_name_sizer.Add(confirm_button_name, 0,
                                   wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.choose_name_sizer.Add(back_button_name, 0,
                                   wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
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
        """Function that handles interaction with the drop down menu"""
        Id = event.GetId()
        widget = self.FindWindowById(Id)

        self.device_chosen = widget.GetStringSelection()

        if self.first_selection and self.device_chosen:
            confirm_button_dev = wx.Button(self.main_panel, wx.ID_ANY,
                                           "Confirm")
            self.choose_dev_sizer.Add(confirm_button_dev, 1,
                                      wx.ALL | wx.ALIGN_LEFT, 5)
            confirm_button_dev.Bind(wx.EVT_BUTTON, self.on_confirm_dev)
            self.Layout()
            self.first_selection = False
        self.Fit()  # fit layout to widgets

    def on_confirm_dev(self, event):
        """Handles the event when the confirm button is clicked in the choose device stage"""
        self.destroy_widgets_in_sizer(self.choose_dev_sizer)
        self.panel_sizer.Detach(self.choose_dev_sizer)

        if self.device_chosen == 'DTYPE' or self.device_chosen == 'XOR':
            self.choose_name()

        else:
            self.choose_qualifier()

    def on_confirm_qual(self, event):
        """Handles the event when the confirm button is clicked in the choose qualifier stage"""
        self.qualifier = self.choose_ctrl.GetValue()
        self.destroy_widgets_in_sizer(self.choose_qual_sizer)
        self.panel_sizer.Detach(self.choose_qual_sizer)
        self.choose_name()

    def on_confirm_name(self, event):
        """Handles the event when the confirm button is clicked in the choose name stage"""
        if self.device_name[0].isalpha() and self.device_name.isalnum():
            if self.canvas.create_device(self.device_name,
                                         self.devices_dict[self.device_chosen],
                                         self.qualifier):
                self.EndModal(wx.ID_OK)

        else:
            error_pop_up('Please enter a valid name')

    def on_back_qual(self, event):
        """Handles the event when the back button is clicked in the choose qualifier stage"""
        self.destroy_widgets_in_sizer(self.choose_qual_sizer)
        self.panel_sizer.Detach(self.choose_qual_sizer)
        self.device_chosen = None
        self.first_selection = True
        self.choose_device()

    def on_back_name(self, event):
        """Handles the event when the back button is clicked in the choose name stage"""
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
        """Handles the event when text is entered into the name input text box"""
        Id = event.GetId()
        widget = self.FindWindowById(Id)
        self.device_name = widget.GetValue()