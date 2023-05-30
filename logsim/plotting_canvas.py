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
import random
import numpy as np
from gui_interactive import line_with_thickness

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


def plot_trace(vertices, t, colour):
    """Function for plotting trace of a specified thickness given a list of vertices"""
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
        except IndexError: 
            x_next = x + 40  # extend final vertex horizontally
            GL.glVertex2f(x_next, y)
            
    GL.glEnd()

def choose_viable_colour(colours, tol):
    """Randomly generate colour for a trace and return if its euclidean distance
    to other trace colours is large enough that colours will be distinguishable"""
    colour = (random.random(), random.random(), random.random())
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

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
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
        self.continue_pan_reset = False
        self.x_max = 0
        self.y_min = 0

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
        GL.glScaled(self.zoom, 1.0, 1.0)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = False

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        #self.render_text(text, 10, 10)

        # Draw monitor traces
        trace_count = 0
        offset = -100
        y_0 = self.GetSize()[1] - 100
        height = 80

        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            vertices = []

            if monitor_name not in self.monitor_colours:  # randomly choose colour for each monitor
                if self.monitor_colours:
                    colour = choose_viable_colour(self.monitor_colours.values(), 0.1/len(self.monitor_colours))
                else:
                    colour = (random.random(), random.random(), random.random())
                
                self.monitor_colours[monitor_name] = colour

            for i in range(len(signal_list)):
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
            self.render_text('HIGH', 10/self.zoom, y_0 + height + offset*trace_count, 
                                font=GLUT.GLUT_BITMAP_HELVETICA_12)
            self.render_text(text, 10/self.zoom, y_0 + height/2 + offset*trace_count)
            GL.glTranslated(self.pan_x * 1/self.zoom, 0.0, 0.0)

            trace_count += 1

        for i in range(len(signal_list)):
            GL.glTranslate(0.0, -self.pan_y, 0.0) # generate axes labels that are invariant to translation in the y-direction
            self.render_text(str(i+1), (i+1)*40-5, 20)
            GL.glTranslated(0.0, self.pan_y, 0.0)
            
        if len(signal_list) > 0:
            self.x_max = len(signal_list)*40
            self.y_min = offset * trace_count - 20

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

        if self.continue_pan_reset and self.x_max*self.zoom> self.GetSize()[0]:  # if continue event occurs and far edge is off screen
            self.pan_x = -(self.x_max*self.zoom - self.GetSize()[0])
            self.init = False  # pan to bring far edge on screen
            self.Refresh()
            self.continue_pan_reset = False

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
    
    def on_enter_window(self, event):
        self.SetFocus()

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
    
        if event.Dragging():  # dragging only has effects in the x-direction
            self.pan_x += event.GetX() - self.last_mouse_x
            self.last_mouse_x = event.GetX()
            if self.pan_x > 0: # limit panning to the bounds of the trace
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
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            if self.pan_x > 0: # limit panning to the bounds of the trace
                self.pan_x = 0
            self.init = False
       
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            if self.pan_x < -(self.x_max*self.zoom - self.GetSize()[0]):
                self.pan_x = min(0, -(self.x_max*self.zoom - self.GetSize()[0]))
            self.init = False
   
        if text:
            self.render(text)
        
        else:
            self.Refresh()  # triggers the paint event

    def on_key_down(self, event):
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
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))