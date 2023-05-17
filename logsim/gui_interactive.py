import wx


class MyFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.panel = wx.Panel(self)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.panel.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)

        self.dragging = False
        self.offset = wx.Point(0, 0)
        self.rect_pos = wx.Point(50, 50)
        self.rect_size = wx.Size(100, 100)

    def on_left_down(self, event):
        if self.rect_pos.x <= event.GetX() <= self.rect_pos.x + self.rect_size.width and \
           self.rect_pos.y <= event.GetY() <= self.rect_pos.y + self.rect_size.height:
            self.dragging = True
            self.offset = self.rect_pos - event.GetPosition()

    def on_left_up(self, event):
        if self.dragging:
            self.dragging = False

    def on_mouse_move(self, event):
        if self.dragging:
            new_pos = event.GetPosition() + self.offset
            self.rect_pos = wx.Point(new_pos.x, new_pos.y)
            self.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.SetBrush(wx.Brush(wx.Colour(0, 128, 255)))
        dc.DrawRectangle(self.rect_pos.x, self.rect_pos.y,
                         self.rect_size.width, self.rect_size.height)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None)
        frame.Show()
        return True


app = MyApp()
app.MainLoop()
