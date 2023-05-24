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
from wx.lib.agw.genericmessagedialog import GenericMessageDialog as GMD

def overline(text):
    return u'{}\u0304'.format((text))


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

def draw_text(x, y, text):
    GL.glColor3f(0.0, 0.0, 0.0)  # text is black
    GL.glRasterPos2f(x, y)
    for char in text:
        GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_18, ord(char))

def render_text(text, w, x_pos, y_pos, color):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glPushMatrix()
        GL.glTranslatef(x_pos, y_pos, 0.0)
        GL.glScalef(0.1, 0.1, 0.1)  # Scale down the text

        GL.glLineWidth(w)
        GL.glColor3f(*color) 
        for c in text:
            GLUT.glutStrokeCharacter(GLUT.GLUT_STROKE_ROMAN, ord(c))

        GL.glPopMatrix()

def render_text_scale(text, w, x_pos, y_pos, color, s):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glPushMatrix()
        GL.glTranslatef(x_pos, y_pos, 0.0)
        GL.glScalef(s, s, s)  # Scale down the text

        GL.glLineWidth(w)
        GL.glColor3f(*color) 
        for c in text:
            GLUT.glutStrokeCharacter(GLUT.GLUT_STROKE_ROMAN, ord(c))

        GL.glPopMatrix()

def line_with_thickness(vertices, t, color):
    if not vertices:
        return

    i = 0
    while i < len(vertices) - 1:
        draw_circle(t/2, *vertices[i], color)
        v1 = np.array(vertices[i])
        v2 = np.array(vertices[i+1])
        delta = v2 - v1
        dv = t/2 / np.linalg.norm(np.array([-delta[1], delta[0]]))
        dv *= np.array([-delta[1], delta[0]])
        p1 = v1 + dv
        p2 = v2 + dv
        p3 = v2 - dv
        p4 = v1 - dv
        GL.glColor3f(*color)
        GL.glBegin(GL.GL_POLYGON)
        GL.glVertex2f(*p1)
        GL.glVertex2f(*p2)
        GL.glVertex2f(*p3)
        GL.glVertex2f(*p4)
        GL.glEnd()
        i += 1
    draw_circle(t/2, *vertices[-1], color)

class Monitor():
    def __init__(self, device_GL, port_id):
        self.device_GL = device_GL
        self.port_id = port_id

        self.monitor_radius = 15

    def render(self):
        dx = 10
        dy = 10
        x, y = self.device_GL.get_port_coor(self.port_id)
        x -= 15
        y += 25
        #GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glColor(1, 1, 1)
        
        #vertices = [(x + dx, y), (x , y), (x , y + dy), (x , y), (x + dx, y + dy), (x + dx, y + dy*3)]
        #line_with_thickness(vertices, self.monitor_radius, (0.6133, 0.196, 0.659))
        draw_circle(self.monitor_radius, x, y, (0,0.3,0.87))
        GL.glColor(1, 1, 1)
        render_text('M', 2, x-5, y-5, (1,1,1))
        GL.glFlush()
        

class Connection_GL:
    def __init__(self, input_device_GL, output_device_GL, input_port_id, output_port_id):
        self.input_device_GL = input_device_GL
        self.output_device_GL = output_device_GL
        self.input_port_id = input_port_id
        self.output_port_id = output_port_id
        self.temp = False
        self.line_thickness = 3
        self.mouse_x = None
        self.mouse_y = None

    def render(self):
        if self.input_device_GL is None:
            in_x, in_y = self.mouse_x, self.mouse_y
        else:
            in_x, in_y = self.input_device_GL.get_port_coor(self.input_port_id)
        if self.output_device_GL is None:
            out_x, out_y = self.mouse_x, self.mouse_y
        else:
            out_x, out_y = self.output_device_GL.get_port_coor(
                self.output_port_id)

        color = (0.0, 0.0, 0.0)
        if self.output_device_GL is not None and self.output_device_GL.device.outputs[self.output_port_id]:
            color = (0.617, 0.0, 0.0)
        draw_circle(7, in_x, in_y, color)
        # draw_circle(7, out_x, out_y, color)

        GL.glColor3f(*color)
        GL.glBegin(GL.GL_LINE_STRIP)
        GL.glVertex2f(in_x, in_y)
        vertices = [(in_x, in_y)]
        if abs(in_x - out_x) > abs(in_y - out_y):
            if in_x > out_x:
                vertices.append(
                    (out_x - (out_x - in_x - abs(out_y - in_y))/2, in_y))
                vertices.append(
                    (in_x + (out_x - in_x - abs(out_y - in_y))/2, out_y))
                GL.glVertex2f(
                    out_x - (out_x - in_x - abs(out_y - in_y))/2, in_y)
                GL.glVertex2f(
                    in_x + (out_x - in_x - abs(out_y - in_y))/2, out_y)
            else:
                vertices.append((
                    in_x + (out_x - in_x - abs(out_y - in_y))/2, in_y))
                vertices.append((
                    out_x - (out_x - in_x - abs(out_y - in_y))/2, out_y))
                GL.glVertex2f(
                    in_x + (out_x - in_x - abs(out_y - in_y))/2, in_y)
                GL.glVertex2f(
                    out_x - (out_x - in_x - abs(out_y - in_y))/2, out_y)
        else:
            if in_y > out_y:
                vertices.append((in_x,
                                 out_y - (out_y - in_y - abs(out_x - in_x))/2))
                vertices.append((out_x,
                                 in_y + (out_y - in_y - abs(out_x - in_x))/2))
                GL.glVertex2f(in_x,
                              out_y - (out_y - in_y - abs(out_x - in_x))/2)
                GL.glVertex2f(out_x,
                              in_y + (out_y - in_y - abs(out_x - in_x))/2)
            else:
                vertices.append((in_x,
                                 in_y + (out_y - in_y - abs(out_x - in_x))/2))
                vertices.append((out_x,
                                 out_y - (out_y - in_y - abs(out_x - in_x))/2))
                GL.glVertex2f(in_x,
                              in_y + (out_y - in_y - abs(out_x - in_x))/2)
                GL.glVertex2f(out_x,
                              out_y - (out_y - in_y - abs(out_x - in_x))/2)

        GL.glVertex2f(out_x, out_y)
        GL.glEnd()
        vertices.append((out_x, out_y))
        # Use when rasterisation is fixed
        line_with_thickness(vertices, self.line_thickness, color)


class Device_GL:
    def __init__(self, x, y, device, names):
        self.x = x
        self.y = y
        self.clicked = False
        self.device = device
        self.inputs = len(device.inputs.keys())
        self.id = device.device_id
        self.names = names

        self.name_string = names.get_name_string(self.id)

    def create_connections(self, devices, GL_devices_list):
        """Creates and returns a list of Connections() """
        connection_list = []
        for input_id, o in self.device.inputs.items():
            if o is None:
                continue
            output_device_id, output_port_id = o
            if output_device_id is not None:
                [output_device_GL] = [
                    i for i in GL_devices_list if i.id == output_device_id]
                input_device_GL = self
                connection_list.append(Connection_GL(
                    input_device_GL, output_device_GL, input_id, output_port_id))
        return connection_list


class And_gate(Device_GL):
    """Creates an AND gate for animation"""

    def __init__(self, x, y, device, names, NAND):
        super().__init__(x, y, device, names)

        self.box_width = 45
        self.input_height = 30
        self.port_radius = 7
        self.x_CoM = self.box_width*2/3
        self.NAND = NAND
        self.show_text = True

    def render(self):

        GL.glColor3f(0.212, 0.271, 0.310)
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2f(self.x, self.y)

        GL.glVertex2f(self.x + self.box_width - self.x_CoM,
                      self.y - self.input_height*self.inputs/2)
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
            dx = self.input_height * np.cos(angle)
            dy = self.input_height * np.sin(angle)
            GL.glVertex2f(self.x - self.x_CoM + self.box_width + dx, self.y +
                          self.input_height * (self.inputs - 2.0)/2.0 + dy)
        for angle in np.linspace(0, -0.5*np.pi, num_segments):
            dx = self.input_height * np.cos(angle)
            dy = self.input_height * np.sin(angle)
            GL.glVertex2f(self.x + self.box_width - self.x_CoM + dx, self.y -
                          self.input_height * (self.inputs - 2.0)/2.0 + dy)
        GL.glEnd()

        if self.NAND:
            draw_circle(self.port_radius, self.x + self.box_width - self.x_CoM +
                        self.input_height, self.y, (0.0, 0.0, 0.0))

        for i in range(self.inputs):
            y = self.input_height * (i + 0.5 - self.inputs*0.5) + self.y
            draw_circle(self.port_radius, self.x -
                        self.x_CoM, y, (0.0, 0.0, 0.0))

        #render_text(self.name_string, 2, self.x, self.y)
        if self.show_text:

            draw_text(self.x-5, self.y - self.input_height*self.inputs/2 - 19, self.name_string)


    def is_clicked(self, mouse_x, mouse_y):
        x_low = self.x - self.x_CoM
        x_high = self.x - self.x_CoM + self.box_width + self.input_height
        if x_low < mouse_x < x_high and self.y - self.input_height * self.inputs/2 < mouse_y < self.y + self.input_height * self.inputs/2:
            return True
        else:
            return False

    def is_port_clicked(self, mouse_x, mouse_y):
        device_id = None
        port_id = None
        for i in range(self.inputs):
            if (self.x - self.x_CoM - mouse_x)**2 + (self.y + self.input_height * (self.inputs/2 - i - 0.5) - mouse_y)**2 < self.port_radius**2:
                port_id = self.names.query("I" + str(i+1))
                device_id = self.device.device_id
                return (device_id, port_id)
        if (self.x - self.x_CoM + self.box_width + self.input_height - mouse_x)**2 + (self.y - mouse_y)**2 < self.port_radius**2:
            device_id = self.device.device_id
        return (device_id, port_id)

    def get_port_coor(self, port_id):
        if port_id is None:
            x = self.x - self.x_CoM + self.box_width + self.input_height
            y = self.y
        elif self.device.inputs:
            input_ids = self.names.lookup(
                ["I" + str(i) for i in range(1, self.inputs + 1)])
            index = input_ids.index(port_id)
            x = self.x - self.x_CoM
            y = self.y + self.input_height * \
                (self.inputs/2 - 0.5) - self.input_height * index
        else:
            raise IndexError("Port not in device")

        return [x, y]


class Or_gate(Device_GL):
    """Creates an OR gate for animation"""

    def __init__(self, x, y, device, names, NOR):
        super().__init__(x, y, device, names)

        self.box_width = 45
        self.indent_width = 15
        self.input_height = 30
        self.port_radius = 7
        self.no_segments = 100
        self.x_CoM = 10
        self.straight_box_width = 15
        self.NOR = NOR
        self.show_text = True

    def render(self):

        GL.glColor3f(0.212, 0.271, 0.310)
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2d(self.x + self.box_width - self.x_CoM, self.y)

        c = self.inputs * self.input_height/2

        for dy in np.linspace(c, -c, self.no_segments):
            dx = self.box_width*(1 - abs(dy / c)**1.6) + \
                self.straight_box_width
            GL.glVertex2f(self.x + dx - self.x_CoM, self.y + dy)

        for dy in np.linspace(-c, c, self.no_segments):
            dx = self.indent_width*(1 - (dy / c)**2)
            GL.glVertex2f(self.x + dx - self.x_CoM, self.y + dy)

        dx = self.straight_box_width
        GL.glVertex2f(self.x + dx - self.x_CoM, self.y + dy)

        GL.glEnd()

        if self.NOR:
            draw_circle(self.port_radius, self.x + self.box_width + self.straight_box_width -
                        self.x_CoM, self.y, (0.0, 0.0, 0.0))

        for dy in np.linspace(-c + self.input_height/2, c - self.input_height/2, self.inputs):
            dx = self.indent_width*(1 - (dy / c)**2)
            draw_circle(self.port_radius, self.x - self.x_CoM,
                        self.y + dy, (0.0, 0.0, 0.0))
            vertices = [(self.x - self.x_CoM, self.y + dy),
                        (self.x - self.x_CoM + dx, self.y + dy)]
            line_with_thickness(vertices, 3, (0.0, 0.0, 0.0))
        
        if self.show_text:

            draw_text(self.x-5, self.y - self.input_height*self.inputs/2 -19, self.name_string)

    def is_clicked(self, mouse_x, mouse_y):
        x_low = self.x - self.x_CoM
        x_high = self.x - self.x_CoM + self.box_width + self.straight_box_width
        if x_low < mouse_x < x_high and self.y - self.input_height * self.inputs/2 < mouse_y < self.y + self.input_height * self.inputs/2:
            return True
        else:
            return False

    def is_port_clicked(self, mouse_x, mouse_y):
        device_id = None
        port_id = None
        for i in range(self.inputs):
            if (self.x - self.x_CoM - mouse_x)**2 + (self.y + self.input_height * (self.inputs/2 - i - 0.5) - mouse_y)**2 < self.port_radius**2:
                port_id = self.names.query("I" + str(i+1))
                device_id = self.device.device_id
                return (device_id, port_id)
        if (self.x - self.x_CoM + self.box_width + self.straight_box_width - mouse_x)**2 + (self.y - mouse_y)**2 < self.port_radius**2:
            device_id = self.device.device_id
        return (device_id, port_id)

    def get_port_coor(self, port_id):
        if port_id is None:
            x = self.x - self.x_CoM + self.box_width + self.straight_box_width
            y = self.y
        elif self.device.inputs:
            input_ids = self.names.lookup(
                ["I" + str(i) for i in range(1, self.inputs + 1)])
            index = input_ids.index(port_id)
            x = self.x - self.x_CoM
            y = self.y + self.input_height * \
                (self.inputs/2 - 0.5) - self.input_height * index
        else:
            raise IndexError("Port not in device")

        return [x, y]


class Xor_gate(Device_GL):
    """Creates an XOR gate for animation"""

    def __init__(self, x, y, device, names):
        super().__init__(x, y, device, names)

        self.box_width = 45
        self.indent_width = 15
        self.input_height = 30
        self.port_radius = 7
        self.no_segments = 100
        self.x_CoM = 10
        self.straight_box_width = 15
        self.gap_width = 5
        self.thickness = 2
        self.show_text = True

    def render(self):

        GL.glColor3f(0.212, 0.271, 0.310)
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2d(self.x + self.box_width - self.x_CoM, self.y)

        c = self.input_height

        for dy in np.linspace(c, -c, self.no_segments):
            dx = self.box_width*(1 - abs(dy / c)**1.6) + \
                self.straight_box_width
            GL.glVertex2f(self.x + dx - self.x_CoM, self.y + dy)

        for dy in np.linspace(-c, c, self.no_segments):
            dx = self.indent_width*(1 - (dy / c)**2)
            GL.glVertex2f(self.x + dx - self.x_CoM, self.y + dy)

        dx = self.straight_box_width
        GL.glVertex2f(self.x + dx - self.x_CoM, self.y + dy)

        GL.glEnd()

        vertices = []
        for dy in np.linspace(-c, c, self.no_segments):
            dx = self.indent_width*(1 - (dy / c)**2)
            vertices.append((self.x + dx - self.x_CoM -
                            self.gap_width, self.y + dy))
        line_with_thickness(vertices, self.thickness, (0.212, 0.271, 0.310))

        draw_circle(self.port_radius, self.x + self.box_width + self.straight_box_width -
                    self.x_CoM, self.y, (0.0, 0.0, 0.0))

        for dy in np.linspace(-c + self.input_height/2, c - self.input_height/2, self.inputs):
            dx = self.indent_width*(1 - (dy / c)**2)
            draw_circle(self.port_radius, self.x - self.x_CoM - self.gap_width,
                        self.y + dy, (0.0, 0.0, 0.0))
            vertices = [(self.x - self.x_CoM, self.y + dy),
                        (self.x - self.x_CoM + dx, self.y + dy)]
            line_with_thickness(vertices, 3, (0.0, 0.0, 0.0))
        if self.show_text:

            draw_text(self.x-5, self.y - self.input_height*self.inputs/2 -19, self.name_string)

    def is_clicked(self, mouse_x, mouse_y):
        x_low = self.x - self.x_CoM - self.gap_width
        x_high = self.x - self.x_CoM + self.box_width + self.straight_box_width
        if x_low < mouse_x < x_high and self.y - self.input_height < mouse_y < self.y + self.input_height:
            return True
        else:
            return False

    def is_port_clicked(self, mouse_x, mouse_y):
        device_id = None
        port_id = None
        for i in range(2):
            if (self.x - self.x_CoM - mouse_x - self.gap_width)**2 + (self.y + self.input_height * (0.5 - i) - mouse_y)**2 < self.port_radius**2:
                port_id = self.names.query("I" + str(i+1))
                device_id = self.device.device_id
                return (device_id, port_id)
        if (self.x - self.x_CoM + self.box_width + self.straight_box_width - mouse_x)**2 + (self.y - mouse_y)**2 < self.port_radius**2:
            device_id = self.device.device_id
        return (device_id, port_id)

    def get_port_coor(self, port_id):
        if port_id is None:
            x = self.x - self.x_CoM + self.box_width + self.straight_box_width
            y = self.y
        elif self.device.inputs:
            input_ids = self.names.lookup(
                ["I" + str(i) for i in range(1, self.inputs + 1)])
            index = input_ids.index(port_id)
            x = self.x - self.x_CoM - self.gap_width
            y = self.y + self.input_height * \
                (self.inputs/2 - 0.5) - self.input_height * index
        else:
            raise IndexError("Port not in device")

        return [x, y]


class D_type(Device_GL):
    """Creates an Dtype device for animation"""

    def __init__(self, x, y, device, names):
        super().__init__(x, y, device, names)

        self.width = 55
        self.input_height = 30
        self.port_radius = 7
        self.no_segments = 100
        self.show_text = True

    def render(self):

        GL.glColor3f(0.212, 0.271, 0.310)
        GL.glBegin(GL.GL_POLYGON)
        GL.glVertex2f(self.x - self.width/2, self.y + self.input_height*2)
        GL.glVertex2f(self.x + self.width/2, self.y + self.input_height*2)
        GL.glVertex2f(self.x + self.width/2, self.y - self.input_height*2)
        GL.glVertex2f(self.x - self.width/2, self.y - self.input_height*2)
        GL.glEnd()

        vertices = []
        for dy in np.linspace(-1.5 * self.input_height, 1.5 * self.input_height, 4):
            draw_circle(self.port_radius, self.x - self.width /
                        2, self.y + dy, (0.0, 0.0, 0.0))
        draw_circle(self.port_radius, self.x + self.width/2,
                    self.y + self.input_height/2, (0.0, 0.0, 0.0))
        draw_circle(self.port_radius, self.x + self.width/2,
                    self.y - self.input_height/2, (0.0, 0.0, 0.0))
        
        render_text_scale('DATA', 1, self.x - self.width/2 +10 , self.y + self.input_height*1.5 -4, (1,1,1), 0.05)
        render_text_scale('CLK', 1, self.x - self.width/2 +10 , self.y + self.input_height/2-4, (1,1,1),0.05)
        render_text_scale('SET', 1, self.x - self.width/2 +10 , self.y - self.input_height/2-4, (1,1,1),0.05)
        render_text_scale('CLR', 1, self.x - self.width/2 +10 , self.y - self.input_height*1.5-4, (1,1,1), 0.05)
        render_text_scale('Q', 1, self.x + self.width/2 -13 , self.y + self.input_height/2-4, (1,1,1),0.05)
        render_text_scale(overline('Q'), 1, self.x + self.width/2 -13, self.y - self.input_height/2-4, (1,1,1),0.05)
        line_with_thickness([(self.x + self.width/2-13, self.y - self.input_height/2+3), (self.x + self.width/2 - 9, self.y - self.input_height/2+3)], 0.3, (1,1,1))
        
        if self.show_text:

            draw_text(self.x-7, self.y - self.input_height*self.inputs/2 - 19, self.name_string)

    def is_clicked(self, mouse_x, mouse_y):
        x_low = self.x - self.width/2
        x_high = self.x + self.width
        if x_low < mouse_x < x_high and self.y - self.input_height*2 < mouse_y < self.y + 2*self.input_height:
            return True
        else:
            return False

    def is_port_clicked(self, mouse_x, mouse_y):
        device_id = self.device.device_id
        port_id = None
        if (self.x - self.width/2 - mouse_x)**2 + (self.y + self.input_height * 1.5 - mouse_y)**2 < self.port_radius**2:
            port_id = self.names.query("DATA")
            return (device_id, port_id)
        elif (self.x - self.width/2 - mouse_x)**2 + (self.y + self.input_height * 0.5 - mouse_y)**2 < self.port_radius**2:
            port_id = self.names.query("CLK")
            return (device_id, port_id)
        elif (self.x - self.width/2 - mouse_x)**2 + (self.y - self.input_height * 0.5 - mouse_y)**2 < self.port_radius**2:
            port_id = self.names.query("SET")
            return (device_id, port_id)
        elif (self.x - self.width/2 - mouse_x)**2 + (self.y - self.input_height * 1.5 - mouse_y)**2 < self.port_radius**2:
            port_id = self.names.query("CLEAR")
            return (device_id, port_id)
        elif (self.x + self.width/2 - mouse_x)**2 + (self.y + self.input_height * 0.5 - mouse_y)**2 < self.port_radius**2:
            port_id = self.names.query("Q")
            return (device_id, port_id)
        elif (self.x + self.width/2 - mouse_x)**2 + (self.y - self.input_height * 0.5 - mouse_y)**2 < self.port_radius**2:
            port_id = self.names.query("QBAR")
            return (device_id, port_id)
        return (None, port_id)

    def get_port_coor(self, port_id):
        if port_id == self.names.query("CLK"):
            x = self.x - self.width/2
            y = self.y + self.input_height * 0.5
        elif port_id == self.names.query("SET"):
            x = self.x - self.width/2
            y = self.y - self.input_height * 0.5
        elif port_id == self.names.query("CLEAR"):
            x = self.x - self.width/2
            y = self.y - self.input_height * 1.5
        elif port_id == self.names.query("DATA"):
            x = self.x - self.width/2
            y = self.y + self.input_height * 1.5
        elif port_id == self.names.query("Q"):
            x = self.x + self.width/2
            y = self.y + self.input_height * 0.5
        elif port_id == self.names.query("QBAR"):
            x = self.x + self.width/2
            y = self.y - self.input_height * 0.5
        else:
            raise IndexError("Port not in device")

        return [x, y]


class Clock(Device_GL):
    """Creates an Clock for animation"""

    def __init__(self, x, y, device, names):
        super().__init__(x, y, device, names)

        self.width = 60
        self.half_height = 20
        self.port_radius = 7
        self.no_segments = 100
        self.thickness = 2
        self.show_text = True

    def render(self):

        GL.glColor3f(0.212, 0.271, 0.310)
        GL.glBegin(GL.GL_POLYGON)
        GL.glVertex2f(self.x - self.width/2, self.y + self.half_height)
        GL.glVertex2f(self.x + self.width/2, self.y + self.half_height)
        GL.glVertex2f(self.x + self.width/2, self.y - self.half_height)
        GL.glVertex2f(self.x - self.width/2, self.y - self.half_height)
        GL.glEnd()

        if self.device.outputs[None]:
            GL.glColor3f(0.617, 0.0, 0.0)
            color = (0.617, 0.0, 0.0)
        else:
            GL.glColor3f(0.0, 0.0, 0.0)
            color = (0.0, 0.0, 0.0)
        GL.glBegin(GL.GL_TRIANGLE_STRIP)
        GL.glVertex2f(self.x - self.width/4, self.y)
        GL.glVertex2f(self.x - self.width/4 + self.thickness, self.y)

        GL.glVertex2f(self.x - self.width/4, self.y + self.half_height/2)
        GL.glVertex2f(self.x - self.width/4 + self.thickness,
                      self.y + self.half_height/2 - self.thickness)

        GL.glVertex2f(self.x + self.thickness/2, self.y + self.half_height/2)
        GL.glVertex2f(self.x - self.thickness/2, self.y +
                      self.half_height/2 - self.thickness)

        GL.glVertex2f(self.x + self.thickness/2, self.y -
                      self.half_height/2 + self.thickness)
        GL.glVertex2f(self.x - self.thickness/2, self.y - self.half_height/2)

        GL.glVertex2f(self.x - self.thickness + self.width/4,
                      self.y - self.half_height/2 + self.thickness)
        GL.glVertex2f(self.x + self.width/4, self.y - self.half_height/2)

        GL.glVertex2f(self.x - self.thickness + self.width/4, self.y)
        GL.glVertex2f(self.x + self.width/4, self.y)
        GL.glEnd()

        draw_circle(self.thickness/2, self.x - self.width /
                    4 + self.thickness/2, self.y, color)
        draw_circle(self.thickness/2, self.x + self.width /
                    4 - self.thickness/2, self.y, color)

        draw_circle(self.port_radius, self.x +
                    self.width/2, self.y, (0.0, 0.0, 0.0))

        if self.show_text:

            draw_text(self.x-15, self.y - self.half_height*2 -5 , self.name_string)

    def is_clicked(self, mouse_x, mouse_y):
        x_low = self.x - self.width/2
        x_high = self.x + self.width
        if x_low < mouse_x < x_high and self.y - self.half_height < mouse_y < self.y + self.half_height:
            return True
        else:
            return False

    def is_port_clicked(self, mouse_x, mouse_y):
        device_id = None
        port_id = None
        if (self.x + self.width/2 - mouse_x)**2 + (self.y - mouse_y)**2 < self.port_radius**2:
            device_id = self.device.device_id
        return (device_id, port_id)

    def get_port_coor(self, port_id):
        if port_id is None:
            x = self.x + self.width/2
            y = self.y
        else:
            raise ValueError(("Port not valid"))

        return [x, y]


class Switch(Device_GL):
    def __init__(self, x, y, device, names):
        super().__init__(x, y, device, names)
        self.inputs = 2

        self.x_CoM = 15
        self.half_height = 15
        self.width = 40
        self.port_radius = 7
        self.line_thickness = 3
        self.show_text = True

        # Could mess up network execution?
        self.device.outputs[None] = self.device.switch_state

    def render(self):
        color = (0.0, 0.0, 0.0)
        draw_circle(self.port_radius, self.x - self.x_CoM,
                    self.y - self.half_height, (0.0, 0.0, 0.0))
        draw_circle(self.port_radius, self.x - self.x_CoM,
                    self.y + self.half_height, (0.617, 0.0, 0.0))
        vertices = [(self.x - self.x_CoM +
                    self.width, self.y)]
        if self.device.switch_state == 1:
            color = (0.617, 0.0, 0.0)
            vertices.append((self.x - self.x_CoM,
                             self.y + self.half_height))
        else:
            vertices.append((self.x - self.x_CoM,
                             self.y - self.half_height))
        draw_circle(self.port_radius, self.x - self.x_CoM +
                    self.width, self.y, color)
        line_with_thickness(vertices, self.line_thickness, color)

        if self.show_text:

            draw_text(self.x-8, self.y - self.half_height*2.5, self.name_string)

    def is_clicked(self, mouse_x, mouse_y):
        x_low = self.x - self.x_CoM
        x_high = self.x - self.x_CoM + self.width
        if x_low < mouse_x < x_high and self.y - self.half_height < mouse_y < self.y + self.half_height:
            return True
        else:
            return False

    def get_port_coor(self, port_id):
        if port_id is None:
            return (self.x - self.x_CoM + self.width, self.y)
        else:
            raise IndexError("Port does not exist")

    def is_port_clicked(self, mouse_x, mouse_y):
        device_id = None
        port_id = None
        if (self.x - self.x_CoM + self.width - mouse_x)**2 + (self.y - mouse_y)**2 < self.port_radius**2:
            device_id = self.device.device_id
        return (device_id, port_id)


class InteractiveCanvas(wxcanvas.GLCanvas):
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

    def __init__(self, parent, devices, monitors, names, network):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        self.network = network
        self.monitors = monitors
        self.names = names
        self.devices = devices

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position
        self.object_clicked = False
        self.connection_list = [False, None, None]
        self.temp_connection = None

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_ENTER_WINDOW, self. on_enter_window)

        self.init_objects(devices, names)

        # self.objects = [And_gate(50, 50), And_gate(300, 50), Or_gate(500, 50)]

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
        self.switch_GL_list = []
        self.monitors_GL = []

        self.connections = []

        and_gate_ids = devices.find_devices(devices.AND)
        nand_gate_ids = devices.find_devices(devices.NAND)
        or_gate_ids = devices.find_devices(devices.OR)
        nor_gate_ids = devices.find_devices(devices.NOR)
        switch_ids = devices.find_devices(devices.SWITCH)
        xor_gate_ids = devices.find_devices(devices.XOR)
        clock_ids = devices.find_devices(devices.CLOCK)
        dtype_ids = devices.find_devices(devices.D_TYPE)
        x = 100
        y = 100

        for id in switch_ids:
            device = devices.get_device(id)
            switch = Switch(x, y, device, names)
            x += 200
            self.objects.append(switch)
            self.devices_GL_list.append(switch)
            self.switch_GL_list.append(switch)

        for id in and_gate_ids:
            device = devices.get_device(id)
            and_gate = And_gate(x, y, device, names, False)
            x += 200
            self.objects.append(and_gate)
            self.devices_GL_list.append(and_gate)

        for id in nand_gate_ids:
            device = devices.get_device(id)
            nand_gate = And_gate(x, y, device, names, True)
            x += 200
            self.objects.append(nand_gate)
            self.devices_GL_list.append(nand_gate)

        for id in or_gate_ids:
            device = devices.get_device(id)
            or_gate = Or_gate(x, y, device, names, False)
            x += 200
            self.objects.append(or_gate)
            self.devices_GL_list.append(or_gate)

        for id in nor_gate_ids:
            device = devices.get_device(id)
            nor_gate = Or_gate(x, y, device, names, True)
            x += 200
            self.objects.append(nor_gate)
            self.devices_GL_list.append(nor_gate)

        for id in dtype_ids:
            device = devices.get_device(id)
            dtype = D_type(x, y, device, names)
            x += 200
            self.objects.append(dtype)
            self.devices_GL_list.append(dtype)

        for id in clock_ids:
            device = devices.get_device(id)
            clock = Clock(x, y, device, names)
            x += 200
            self.objects.append(clock)
            self.devices_GL_list.append(clock)

        x = 100
        y = 300
        for id in xor_gate_ids:
            device = devices.get_device(id)
            xor_gate = Xor_gate(x, y, device, names)
            x += 200
            self.objects.append(xor_gate)
            self.devices_GL_list.append(xor_gate)

        for device_GL in self.devices_GL_list:
            connections = device_GL.create_connections(
                devices, self.devices_GL_list)
            self.connections += connections
            self.objects += connections

        for device_id, port_id in self.monitors.monitors_dictionary:
            [device_GL] = [
                    i for i in self.devices_GL_list if i.id == device_id]
            monitor = Monitor(device_GL, port_id)
            self.monitors_GL.append(monitor)
            self.objects.append(monitor)
            

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

        if self.temp_connection is not None:
            self.temp_connection.render()

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
        if self.temp_connection is not None:
            self.temp_connection.mouse_x = ox
            self.temp_connection.mouse_y = oy
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

            if self.connection_list[0]:
                for ob in self.devices_GL_list:
                    device_id, port_id = ob.is_port_clicked(ox, oy)
                    if device_id is not None:
                        if self.connection_list[1] is not None:
                            error_code = self.network.make_connection(
                                *self.connection_list[1:], device_id, port_id)
                            if error_code == self.network.NO_ERROR:
                                # Raise error message otherwise
                                [device_GL] = [
                                    i for i in self.devices_GL_list if i.id == device_id]
                                if port_id in device_GL.device.inputs:
                                    self.temp_connection.input_device_GL = device_GL
                                    self.temp_connection.input_port_id = port_id
                                else:
                                    self.temp_connection.output_device_GL = device_GL
                                    self.temp_connection.output_port_id = port_id
                                self.objects.append(self.temp_connection)
                                self.connections.append(self.temp_connection)
                            else:
                                self.raise_error("Connection invalid")
                            self.temp_connection = None
                            self.connection_list = [False, None, None]
                        else:
                            self.connection_list[1] = device_id
                            self.connection_list[2] = port_id
                            [device_GL] = [
                                i for i in self.devices_GL_list if i.id == device_id]
                            if port_id in device_GL.device.inputs:
                                self.temp_connection = Connection_GL(
                                    device_GL, None, port_id, None)
                            else:
                                self.temp_connection = Connection_GL(
                                    None, device_GL, None, port_id)
                            self.temp_connection.mouse_x = ox
                            self.temp_connection.mouse_y = oy
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

    def on_double_click(self, event):
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        for switch in self.switch_GL_list:
            if switch.is_clicked(ox, oy):
                if switch.device.switch_state:
                    switch.device.switch_state = 0
                    switch.device.outputs[None] = 0
                else:
                    switch.device.switch_state = 1
                    switch.device.outputs[None] = 1
                break

    def on_key_down(self, event):
        keycode = event.GetUnicodeKey()
        tmp = ord('c')

        if keycode == 67:
            # When c is pressed
            if self.connection_list[0]:
                self.connection_list = [False, None, None]
                self.temp_connection = None
            else:
                self.connection_list = [True, None, None]
            self.Refresh()
    
    def on_enter_window(self, event):
        self.SetFocus()

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
    
    def create_device(self,device_name, device_type, qualifier = None):
        [device_id] = self.names.lookup([device_name])
        error_code  = self.devices.create_device(device_id, device_type, qualifier)
        if error_code == self.devices.NO_ERROR:
            device = self.devices.get_device(device_id)
            if device_type == self.devices.AND:
                device_GL = And_gate(0, 0, device, self.names, False)
            elif device_type == self.devices.NAND:
                device_GL = And_gate(0, 0, device, self.names, True)
            elif device_type == self.devices.OR:
                device_GL = Or_gate(0, 0, device, self.names, False)
            elif device_type == self.devices.NOR:
                device_GL = Or_gate(0, 0, device, self.names, True)
            elif device_type == self.devices.SWITCH:
                device_GL = Switch(0, 0, device, self.names)
            elif device_type == self.devices.XOR:
                device_GL = Xor_gate(0,0, device, self.names)
            elif device_type == self.devices.D_TYPE:
                device_GL = D_type(0, 0, device, self.names)
            elif device_type == self.devices.CLOCK:
                device_GL = Clock(0,0, device, self.names)
            self.objects.append(device_GL)
            self.devices_GL_list.append(device_GL)
        self.Refresh()

    
    def raise_error(self, string):
        dlg = GMD(None, string,
                      "Error", wx.OK | wx.ICON_ERROR | 0x40)
        dlg.SetIcon(wx.ArtProvider.GetIcon(wx.ART_WARNING))
        dlg.ShowModal()
        dlg.Destroy()


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
        self.Maximize()

        # Initial attributes
        self.first_run = False

        # Canvas for drawing signals
        self.canvas = InteractiveCanvas(self, devices, monitors, names, network)
        choices = ['SW1', 'SW2', 'SW3']

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.cont_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.text_box = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)

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
