"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
import numpy as np

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


def draw_circle(r, x, y, color):
    num_segments = 100
    GL.glColor3f(*color)
    GL.glBegin(GL.GL_TRIANGLE_FAN)
    GL.glVertex2f(x, y)
    for angle in np.linspace(0, 2 * np.pi, num_segments):
        dx = r * np.cos(angle)
        dy = r * np.sin(angle)
        GL.glVertex2f(x + dx, y + dy)
    GL.glEnd()


class Connection_GL:
    def __init__(self, input_device_GL, output_device_GL, input_port_id, output_port_id):
        self.input_device_GL = input_device_GL
        self.output_device_GL = output_device_GL
        self.input_port_id = input_port_id
        self.output_port_id = output_port_id
    
    def render(self):
        in_x, in_y = self.input_device_GL.get_port_coor(self.input_port_id)
        out_x, out_y = self.output_device_GL.get_port_coor(self.output_port_id)

        GL.glBegin(GL.GL_LINE_STRIP)
        GL.glVertex2f(in_x, in_y)
        GL.glVertex2f(out_x, out_y)
        GL.glEnd()
    

class Device_GL:
    def __init__(self, x, y, device, names):
        self.x = x
        self.y = y
        self.clicked = False
        self.device = device
        self.inputs = len(device.inputs.keys())
        self.id = device.device_id
        self.names = names
    
    def create_connections(self, devices, GL_devices_list):
        """Creates and returns a list of Connections() """
        connection_list = []
        for input_id, o in self.device.inputs.items():
            if o is None:
                continue
            output_device_id, output_port_id = o
            if output_device_id is not None:
                [output_device_GL] = [i for i in GL_devices_list if i.id == output_device_id]
                input_device_GL = self
                connection_list.append(Connection_GL(input_device_GL, output_device_GL, input_id, output_port_id))
        return connection_list

class And_gate(Device_GL):
    """Creates an AND gate for animation"""

    def __init__(self, x, y, device, names):
        super().__init__(x, y, device, names)

        self.box_width = 45
        self.input_height = 30
        self.port_radius = 7
        self.x_CoM = self.box_width*2/3

    def render(self):

        GL.glColor3f(0.212, 0.271, 0.310)
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2f(self.x, self.y)

        GL.glVertex2f(self.x + self.box_width  - self.x_CoM, self.y - self.input_height*self.inputs/2)
        GL.glVertex2f(self.x - self.x_CoM, self.y -
                      self.input_height*self.inputs/2)
        GL.glVertex2f(self.x - self.x_CoM, self.y +
                      self.input_height*self.inputs/2)
        GL.glVertex2f(self.x + self.box_width - self.x_CoM, self.y +
                      self.input_height*self.inputs/2)

        # Draw the arc for the AND gate
        num_segments = 50
        for angle in np.linspace(np.pi*0.5, 0, num_segments):
            dx = self.input_height * np.cos(angle)
            dy = self.input_height * np.sin(angle)
            GL.glVertex2f(self.x - self.x_CoM + self.box_width + dx, self.y +
                          self.input_height * (self.inputs - 2.0)/2.0 + dy)
        for angle in np.linspace(0, -0.5*np.pi, num_segments):
            dx = self.input_height * np.cos(angle)
            dy = self.input_height * np.sin(angle)
            GL.glVertex2f(self.x +self.box_width - self.x_CoM + dx, self.y -
                          self.input_height * (self.inputs - 2.0)/2.0 + dy)
        GL.glEnd()

        draw_circle(self.port_radius, self.x +self.box_width - self.x_CoM +
                    self.input_height, self.y, (0.0, 0.0, 0.0))

        for i in range(self.inputs):
            y = self.input_height * (i + 0.5 - self.inputs*0.5) + self.y
            draw_circle(self.port_radius, self.x - self.x_CoM, y, (0.0, 0.0, 0.0))

    def is_clicked(self, mouse_x, mouse_y):
        click_radius = 30
        if (mouse_x - self.x)**2 + (mouse_y - self.y)**2 < click_radius**2:
            return True
        else:
            return False
    
    def get_port_coor(self, port_id):
        if port_id is None:
            x = self.x + self.box_width/3 + self.input_height
            y = self.y
        elif self.device.inputs:
            input_ids = self.names.lookup(["I" + str(i) for i in range(1, self.inputs + 1)])
            index = input_ids.index(port_id)
            x = self.x - self.x_CoM
            y = self.y + self.input_height* (self.inputs/2 - 0.5) - self.input_height * index
        else:
            raise IndexError("Port not in device")

        return [x,y]


class Or_gate(Device_GL):
    """Creates an AND gate for animation"""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.inputs = 2

    def render(self):

        box_width = 45
        indent_width = 10
        input_height = 30
        port_radius = 7
        no_segments = 100
        x_CoM = 10

        GL.glColor3f(0.212, 0.271, 0.310)
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2d(self.x + box_width - x_CoM, self.y)


        c = self.inputs * input_height/2

        for dy in np.linspace(c, -c, no_segments):
            dx = box_width*(1 - abs(dy / c)**1.6)
            GL.glVertex2f(self.x + dx - x_CoM, self.y + dy)
        
        for dy in np.linspace(-c, c, no_segments):
            dx = indent_width*(1 - (dy / c)**2)
            GL.glVertex2f(self.x + dx - x_CoM, self.y + dy)

        GL.glEnd()

        draw_circle(port_radius, self.x + box_width - x_CoM, self.y, (0.0, 0.0, 0.0))

        for dy in np.linspace(-c + input_height/2, c - input_height/2, self.inputs):
            dx = indent_width*(1 - (dy / c)**2)
            draw_circle(port_radius, self.x - x_CoM, self.y + dy, (0.0, 0.0, 0.0))


    def is_clicked(self, mouse_x, mouse_y):
        click_radius = 30
        if (mouse_x - self.x)**2 + (mouse_y - self.y)**2 < click_radius**2:
            return True
        else:
            return False


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors, names):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position
        self.object_clicked = False

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        self.init_objects(devices, names)

        #self.objects = [And_gate(50, 50), And_gate(300, 50), Or_gate(500, 50)]

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)
    
    def init_objects(self, devices, names):
        self.objects = []
        self.devices_GL_list = []
        self.connections = []

        and_gate_ids = devices.find_devices(devices.AND)
        x = 100
        y = 100

        for id in and_gate_ids:
            device = devices.get_device(id)
            and_gate = And_gate(x, y, device, names)
            x += 200
            self.objects.append(and_gate)
            self.devices_GL_list.append(and_gate)
        for device_GL in self.devices_GL_list:
            connections = device_GL.create_connections(devices, self.devices_GL_list)
            self.connections += connections
            self.objects += connections


    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.render_grid()

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        for ob in self.objects:
            ob.render()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])

            for ob in self.devices_GL_list:
                if ob.is_clicked(ox, oy):
                    ob.clicked = True
                    self.object_clicked = True
                    break

        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
            if self.object_clicked:
                self.object_clicked = False
                for ob in self.devices_GL_list:
                    ob.clicked = False

        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
            if self.object_clicked:
                self.object_clicked = False
                for ob in self.devices_GL_list:
                    ob.clicked = False
        if event.Dragging():
            if self.object_clicked:
                for ob in self.devices_GL_list:
                    if ob.clicked:
                        ob.x += (event.GetX() - self.last_mouse_x) / self.zoom
                        ob.y -= (event.GetY() - self.last_mouse_y) / self.zoom
            else:
                self.pan_x += event.GetX() - self.last_mouse_x
                self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def render_grid(self):

        grid_spacing = 50
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x % grid_spacing,
                        self.pan_y % grid_spacing, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

        width, height = self.GetSize()
        x = 0

        GL.glColor3f(0.7, 0.7, 0.7)
        GL.glBegin(GL.GL_LINES)
        while x < width/self.zoom:
            if abs(x - grid_spacing * self.pan_x//grid_spacing) < 8:
                GL.glColor3f(0.7, 0, 0)
            GL.glVertex2f(x, -grid_spacing)
            GL.glVertex2f(x, height/self.zoom)
            x += grid_spacing
            GL.glColor3f(0.7, 0.7, 0.7)
        GL.glEnd()

        GL.glBegin(GL.GL_LINES)
        y = 0
        while y < grid_spacing + height/self.zoom:
            GL.glVertex2f(-grid_spacing, y)
            GL.glVertex2f(width/self.zoom, y)
            y += grid_spacing
        GL.glEnd()

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)


class Gui_interactive(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

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
        self.SetMenuBar(menuBar)

        # Initial attributes
        self.first_run = False

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors, names)

        choices = ['SW1', 'SW2', 'SW3']

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.cont_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.text_box = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)

        self.text2 = wx.StaticText(self, wx.ID_ANY, "Configure Switches")
        self.switch_selector = wx.ComboBox(
            self, choices=choices, style=wx.CB_READONLY, name='Switch')  # widgets for setting switches
        self.checkbox = wx.CheckBox(
            self, label="Switch High", style=wx.CHK_UNCHECKED)
        self.checkbox.Enable(True)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.side_sizer, 1, wx.ALL, 5)

        self.side_sizer.Add(self.text, 1, wx.TOP, 10)
        self.side_sizer.Add(self.spin, 1, wx.ALL, 5)
        self.side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        # self.side_sizer.Add(self.text_box, 1, wx.ALL, 5)

        self.side_sizer.Add(self.text2, 1, wx.ALL, 5)
        self.side_sizer.Add(self.switch_selector, 1, wx.ALL, 5)
        self.side_sizer.Add(self.checkbox, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by bd432, al2008, th624\n2023",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)

        if not self.first_run:
            main_sizer = self.GetSizer()  # Get the parent sizer

            # Remove the existing side_sizer from main_sizer
            main_sizer.Remove(self.side_sizer)

            # Recreate the side_sizer with the new configuration
            side_sizer_c = wx.BoxSizer(wx.VERTICAL)
            side_sizer_c.Add(self.text, 1, wx.TOP, 10)
            side_sizer_c.Add(self.spin, 1, wx.ALL, 5)
            side_sizer_c.Add(self.run_button, 1, wx.ALL, 5)
            side_sizer_c.Add(self.cont_button, 1, wx.ALL, 5)
            side_sizer_c.Add(self.text2, 1, wx.ALL, 5)
            side_sizer_c.Add(self.switch_selector, 1, wx.ALL, 5)
            side_sizer_c.Add(self.checkbox, 1, wx.ALL, 5)

            # Add the updated side_sizer back to main_sizer
            main_sizer.Add(side_sizer_c, 1, wx.ALL, 5)

            self.Layout()

        self.first_run = True

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)
