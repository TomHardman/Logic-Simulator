
"""
This module contains the TraceCanvas class which is used for plotting
monitor traces in the Gui. The plot_trace and choose_viable_colour
functions are defined outside the Class but are used by the TraceCanvas
for plotting
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
import random


def plot_trace(vertices, t, colour):
    """Function for plotting trace of a specified thickness given a list
    of vertices"""
    if not vertices:
        return

    GL.glLineWidth(t)
    GL.glColor3f(*colour)
    GL.glBegin(GL.GL_LINE_STRIP)

    for i in range(len(vertices)):
        x, y = vertices[i][0], vertices[i][1]
        GL.glVertex2f(x, y)
        try:
            x_next = vertices[i+1][0]
            GL.glVertex2f(x_next, y)
        except IndexError:  # if end of list has been reached
            x_next = x + 40  # extend final vertex horizontally so that trace is required length
            GL.glVertex2f(x_next, y)
            
    GL.glEnd()


def choose_viable_colour(colours, tol, dark_mode):
    """Randomly generates a colour for a trace and returns the colour if
    its euclidean distance to other trace colours is less than a
    specified tolerance - can be used to generate random trace colours
    that are distinguishable from one another"""
    if not dark_mode:
        colour = (random.random(), random.random(), random.random())
    else:
        colour = (random.uniform(0.5, 1), random.uniform(0.5, 1), random.uniform(0.5, 1))
    while True:
        dist = True
        for col in colours:
            d = sum([(colour[i] - col[i])**2 for i in range(3)])
            if d < tol:
                colour = (random.random(), random.random(), random.random())
                dist = False
                break
        if dist:
            break
    return colour


class TraceCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent - parent window.
    devices - instance of the devices.Devices() class.
    monitors - instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self) - Configures the OpenGL context.

    render(self, text) - Handles all drawing operations.

    on_paint(self, event) - Handles the paint event.

    on_size(self, event) - Handles the canvas resize event.

    on_mouse(self, event) - Handles mouse events.

    render_text(self, text, x_pos, y_pos) - Handles text drawing
                                           operations.

    on_key_down(self, event) -
        Handles events where the up key and down key are pressed -
        used for scrolling in the canvas window

    on_enter_window(self, event):
        Handles events where the mouse enters the canvas window - used
        to avoid event handling conflicts between the two separate
        canvas windows that make up the Gui
    """

    def __init__(self, parent, devices, monitors):
        """Initialises canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)
        self.SetSize(1000, 1000)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position
        self.continue_pan_reset = False  # this is set to true when a continue event is generated in the gui
        self.x_max = 0  # used to determine panning limit in the x-direction
        self.y_min = 0  # used to determine panning limit in the y-direction

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_ENTER_WINDOW, self. on_enter_window)

        # Initialise monitors and devices
        self.monitors = monitors
        self.devices = devices
        self.monitor_colours = dict()
        self.dark_mode = False

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        if self.dark_mode:
            GL.glClearColor(0.2, 0.2, 0.2, 0.0)
        else:
            GL.glClearColor(1, 1, 1, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, 1.0, 1.0)

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:    # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = False

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Initialise variables for drawing monitor traces
        trace_count = 0
        offset = -100
        y_0 = self.GetSize()[1] - 100 
        height = 80
        signal_list = []

        #  Iterate through monitors and plot trace for each one
        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            vertices = []

            # randomly choose viable trace colour if not already chosen
            if monitor_name not in self.monitor_colours:
                if self.monitor_colours:
                    colour = choose_viable_colour(self.monitor_colours.values(), 0.1/len(self.monitor_colours),
                                                  self.dark_mode)
                elif self.dark_mode:  # if dark mode only bright traces should be generated
                    colour = (random.uniform(0.5, 1), random.uniform(0.5, 1), random.uniform(0.5, 1))
                else:
                    colour = (random.random(), random.random(), random.random())
                self.monitor_colours[monitor_name] = colour

            for i in range(len(signal_list)):  # create list of vertices to be used by the plot_trace function
                x = i * 40
                if signal_list[i] == 1:
                    y = y_0 + offset*trace_count + height
                elif signal_list[i] == 0:
                    y = y_0 + offset*trace_count
                elif signal_list[i] == 4:
                    plot_trace(vertices, 4, self.monitor_colours.get(monitor_name))
                    continue
                vertices.append((x, y))

            plot_trace(vertices, 4, self.monitor_colours.get(monitor_name))

            text = monitor_name  # label trace with name of monitor and make it invariant to zoom and pan
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glTranslate(-self.pan_x * 1/self.zoom, 0.0, 0.0)
            self.render_text('H', 10/self.zoom, y_0 + height + offset*trace_count - 5,  # add high label
                             font=GLUT.GLUT_BITMAP_HELVETICA_12)
            self.render_text(text, 10/self.zoom, y_0 + height/2 + offset*trace_count - 7)
            self.render_text('L', 10/self.zoom, y_0 + offset*trace_count - 5,  # add low label
                             font=GLUT.GLUT_BITMAP_HELVETICA_12)
            GL.glTranslated(self.pan_x * 1/self.zoom, 0.0, 0.0)

            trace_count += 1

        for i in range(len(signal_list)):  # generate axes labels that are invariant to panning in the y-direction
            if self.zoom > 0.7:
                GL.glTranslate(0.0, -self.pan_y, 0.0) 
                self.render_text(str(i+1), (i+1)*40-(5*len(str(i+1)))/self.zoom, 20)
                GL.glTranslated(0.0, self.pan_y, 0.0)
            elif i % 2:  # if zoomed out only generate every even cycle number labels to avoid clutter
                GL.glTranslate(0.0, -self.pan_y, 0.0) 
                self.render_text(str(i+1), (i+1)*40-(5*len(str(i+1)))/self.zoom, 20)
                GL.glTranslated(0.0, self.pan_y, 0.0)
            
        if len(signal_list) > 0:
            self.x_max = len(signal_list)*40 + 20/self.zoom  # set x_max to maximum + add some whitespace
            self.y_min = offset * trace_count - 20

        # We have been drawing to the back buffer, flush the graphics pipeline and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

        # if continue event occurs and far edge is off screen auto pan to bring right edge of trace to
        # the right hand edge of the screen
        if self.continue_pan_reset and self.x_max*self.zoom > self.GetSize()[0]:
            self.pan_x = -(self.x_max*self.zoom - self.GetSize()[0])
            self.init = False
            self.Refresh()
            self.continue_pan_reset = False

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        self.render()  # render the canvas

    def on_enter_window(self, event):
        """Handles the event where the mouse enters the canvas window -
        this is used to avoid interference between events relating to
        the two separate canvas windows"""
        self.SetFocus()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
    
        if event.Dragging():  # dragging only has effects in the x-direction
            self.pan_x += event.GetX() - self.last_mouse_x
            self.last_mouse_x = event.GetX()
            if self.pan_x > 0:  # limit panning to the bounds of the trace
                self.pan_x = 0
                self.last_mouse_x = event.GetX()
            if self.pan_x < -(self.x_max*self.zoom - self.GetSize()[0]):
                self.pan_x = min(0, -(self.x_max*self.zoom - self.GetSize()[0]))
                self.last_mouse_x = event.GetX()
            self.init = False

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            if self.zoom < 0.4:  # set limit on zooming out
                self.zoom = 0.4
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox # zoom only occurs in the x-direction
            if self.pan_x > 0:  # limit panning to the bounds of the trace
                self.pan_x = 0
            self.init = False
       
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            if self.zoom > 8:  # set limit on zooming in
                self.zoom = 8
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox  # zoom only occurs in the x-direction
            if self.pan_x < -(self.x_max*self.zoom - self.GetSize()[0]):  # limit panning to the bounds of the trace
                self.pan_x = min(0, -(self.x_max*self.zoom - self.GetSize()[0]))
            self.init = False
        
        else:
            self.Refresh()  # triggers the paint event

    def on_key_down(self, event):
        """Handles events where the up or down key is pressed when in
        the canvas window - these keys are used to scroll up and down
        respectively"""
        keycode = event.GetKeyCode()

        if keycode == wx.WXK_DOWN:
            self.pan_y += 10
            if self.pan_y > -self.y_min - self.GetSize()[1]:
                self.pan_y = max(0, -self.y_min - self.GetSize()[1])
            self.init = False
            self.Refresh()
        elif keycode == wx.WXK_UP:
            self.pan_y -= 10
            if self.pan_y < 0:
                self.pan_y = 0
            self.init = False
            self.Refresh()

    def render_text(self, text, x_pos, y_pos, font=GLUT.GLUT_BITMAP_HELVETICA_18):
        """Handles text drawing operations."""
        if self.dark_mode:
            GL.glColor3f(0.7, 0.7, 0.7)
        else:
            GL.glColor3f(0.0, 0.0, 0.0)
        GL.glRasterPos2f(x_pos, y_pos)
        
        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))