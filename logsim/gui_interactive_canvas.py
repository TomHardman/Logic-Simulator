"""Implement the interactive graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to
visualise and move around the connected network.

Classes:
--------
Monitor         - Animates monitor points
Connection_GL   - Animates connections
Device_GL       - Base class for all devices
And_gate        - Animates AND and NAND gates
Or_gate         - Animates OR and NOR gates
Xor_gate        - Animates XOR gates
D_type          - Animates D TYPE device
Clock           - ANimates the clock
Switch          - Animates the switch
InteractiveCanvas  - GL canvas that contains all logic for
    interacing with and displaying the logic network
"""
import wx
import wx.glcanvas as wxcanvas
import numpy as np
from OpenGL import GL, GLUT
from wx.lib.agw.genericmessagedialog import GenericMessageDialog as GMD


def overline(text):
    return u'{}\u0304'.format((text))


def draw_circle(r, x, y, color):
    """Renders a circle of radius r at (x,y)"""
    num_segments = 100
    GL.glColor3f(*color)
    GL.glBegin(GL.GL_TRIANGLE_FAN)
    GL.glVertex2f(x, y)
    for angle in np.linspace(0, 2 * np.pi, num_segments):
        dx = r * np.cos(angle)
        dy = r * np.sin(angle)
        GL.glVertex2f(x + dx, y + dy)
    GL.glEnd()


def draw_text(x, y, text, dark_mode):
    """Renders text at (x,y)"""
    if dark_mode:
        GL.glColor3f(0.7, 0.7, 0.7)
    else:
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
    GL.glRasterPos2f(x, y)
    for char in text:
        GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_18, ord(char))


def render_text(text, w, x_pos, y_pos, color, dark_mode):
    """Handle text drawing operations. Takes width, position,
         colour and dark mode bool as inputs"""
    if dark_mode:
        GL.glColor3f(0.7, 0.7, 0.7)
    else:
        GL.glColor3f(0.0, 0.0, 0.0)
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
    """Renders a line with thickness t that joins up the given vertices"""
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
    """Class that renders a monitor point
        Inputs: names, device (Device_GL class), port_id"""

    def __init__(self, names, device_GL, port_id):
        self.device_GL = device_GL
        self.port_id = port_id
        self.names = names

        self.monitor_radius = 15

    def render(self, dark_mode):
        """Render monitor point"""
        x, y = self.device_GL.get_port_coor(self.port_id)

        # GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glColor(1, 1, 1)
        if dark_mode:
            if self.port_id == self.names.query('QBAR'):
                x -= 5
                y -= 30
                draw_circle(self.monitor_radius, x, y, (0.537, 0.812, 0.941))
                GL.glColor(1, 1, 1)
                render_text('M', 2, x-5, y-5, (0.1, 0.1, 0.1), dark_mode)
                GL.glFlush()

            elif self.port_id == self.names.query('Q'):
                x -= 5
                y += 30
                draw_circle(self.monitor_radius, x, y, (0.537, 0.812, 0.941))
                GL.glColor(1, 1, 1)
                render_text('M', 2, x-5, y-5, (0.1, 0.1, 0.1), dark_mode)
                GL.glFlush()

            else:
                x -= 15
                y += 25
                draw_circle(self.monitor_radius, x, y, (0.537, 0.812, 0.941))
                GL.glColor(1, 1, 1)
                render_text('M', 2, x-5, y-5, (0.1, 0.1, 0.11), dark_mode)
                GL.glFlush()

        else:
            if self.port_id == self.names.query('QBAR'):
                x -= 5
                y -= 30
                draw_circle(self.monitor_radius, x, y, (0, 0.3, 0.87))
                GL.glColor(1, 1, 1)
                render_text('M', 2, x-5, y-5, (1, 1, 1), dark_mode)
                GL.glFlush()

            elif self.port_id == self.names.query('Q'):
                x -= 5
                y += 30
                draw_circle(self.monitor_radius, x, y, (0, 0.3, 0.87))
                GL.glColor(1, 1, 1)
                render_text('M', 2, x-5, y-5, (1, 1, 1), dark_mode)
                GL.glFlush()

            else:
                x -= 15
                y += 25
                draw_circle(self.monitor_radius, x, y, (0, 0.3, 0.87))
                GL.glColor(1, 1, 1)
                render_text('M', 2, x-5, y-5, (1, 1, 1), dark_mode)
                GL.glFlush()


class Connection_GL:
    """Class that renders a connection
    Inputs - input and output devices
            , input and output port_ids"""

    def __init__(
            self, input_device_GL, output_device_GL,
            input_port_id, output_port_id):

        self.input_device_GL = input_device_GL
        self.output_device_GL = output_device_GL
        self.input_port_id = input_port_id
        self.output_port_id = output_port_id
        self.temp = False
        self.line_thickness = 3
        self.mouse_x = None
        self.mouse_y = None

    def render(self, dark_mode):
        """Animates the connection"""
        if self.input_device_GL is None:
            in_x, in_y = self.mouse_x, self.mouse_y
        else:
            in_x, in_y = self.input_device_GL.get_port_coor(
                self.input_port_id)
        if self.output_device_GL is None:
            out_x, out_y = self.mouse_x, self.mouse_y
        else:
            out_x, out_y = self.output_device_GL.get_port_coor(
                self.output_port_id)
        if dark_mode:
            color = (0.7, 0.7, 0.7)
        else:
            color = (0.0, 0.0, 0.0)

        if (self.output_device_GL is not None and
                self.output_device_GL.device.outputs[self.output_port_id]):
            if dark_mode:
                color = (0.647, 0.41, 0.77)
            else:
                color = (0.617, 0.0, 0.0)

        draw_circle(7, in_x, in_y, color)

        GL.glColor3f(*color)
        vertices = [(in_x, in_y)]
        if abs(in_x - out_x) > abs(in_y - out_y):
            if in_x > out_x:
                vertices.append(
                    (out_x - (out_x - in_x - abs(out_y - in_y))/2, in_y))
                vertices.append(
                    (in_x + (out_x - in_x - abs(out_y - in_y))/2, out_y))
            else:
                vertices.append((
                    in_x + (out_x - in_x - abs(out_y - in_y))/2, in_y))
                vertices.append((
                    out_x - (out_x - in_x - abs(out_y - in_y))/2, out_y))
        else:
            if in_y > out_y:
                vertices.append((in_x,
                                 out_y - (out_y - in_y - abs(out_x - in_x))/2))
                vertices.append((out_x,
                                 in_y + (out_y - in_y - abs(out_x - in_x))/2))
            else:
                vertices.append((in_x,
                                 in_y + (out_y - in_y - abs(out_x - in_x))/2))
                vertices.append((out_x,
                                 out_y - (out_y - in_y - abs(out_x - in_x))/2))

        vertices.append((out_x, out_y))
        line_with_thickness(vertices, self.line_thickness, color)


class Device_GL:
    """Creates the base class for a device"""

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
        """Creates and returns a list of
        Connections() from the device inputs"""

        connection_list = []
        for input_id, o in self.device.inputs.items():
            if o is None:
                continue
            output_device_id, output_port_id = o
            if output_device_id is not None:
                [output_device_GL] = [
                    i for i in GL_devices_list
                    if i.id == output_device_id]
                input_device_GL = self
                connection_list.append(Connection_GL(
                    input_device_GL, output_device_GL,
                    input_id, output_port_id))
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

    def render(self, dark_mode):
        """Animates AND/NAND gates"""
        if dark_mode:
            GL.glColor3f(0.03, 0.172, 0.422)
        else:
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

        if dark_mode:
            color = (0.7, 0.7, 0.7)
        else:
            color = (0.0, 0.0, 0.0)

        if self.device.outputs[None]:
            if dark_mode:
                color = (0.647, 0.41, 0.77)
            else:
                color = (0.617, 0.0, 0.0)

        draw_circle(self.port_radius, self.x + self.box_width - self.x_CoM +
                    self.input_height, self.y, color)

        if self.NAND:
            if dark_mode:
                draw_circle(self.port_radius - 2, self.x +
                            self.box_width - self.x_CoM +
                            self.input_height, self.y, (0.2, 0.2, 0.2))
            else:
                draw_circle(self.port_radius - 2, self.x +
                            self.box_width - self.x_CoM +
                            self.input_height, self.y, (1.0, 1.0, 1.0))

        for i in range(self.inputs):
            y = self.input_height * (i + 0.5 - self.inputs*0.5) + self.y
            if dark_mode:
                draw_circle(self.port_radius, self.x -
                            self.x_CoM, y, (0.7, 0.7, 0.7))
            else:
                draw_circle(self.port_radius, self.x -
                            self.x_CoM, y, (0.0, 0.0, 0.0))
        if self.show_text:

            draw_text(self.x-5, self.y - self.input_height *
                      self.inputs/2 - 19, self.name_string, dark_mode)

    def is_clicked(self, mouse_x, mouse_y):
        """Checks if device is clicked"""
        x_low = self.x - self.x_CoM
        x_high = self.x - self.x_CoM + self.box_width + self.input_height
        if (x_low < mouse_x < x_high and
            self.y - self.input_height * self.inputs/2 <
                mouse_y < self.y + self.input_height * self.inputs/2):
            return True
        else:
            return False

    def is_port_clicked(self, mouse_x, mouse_y):
        """Checks if a port is clicked and returns
         the device and port id"""
        device_id = None
        port_id = None
        for i in range(self.inputs):
            if ((self.x - self.x_CoM - mouse_x)**2 +
                (self.y + self.input_height * (self.inputs/2 - i - 0.5) -
                    mouse_y)**2 < (self.port_radius+3)**2):
                port_id = self.names.query("I" + str(i+1))
                device_id = self.device.device_id
                return (device_id, port_id)
        if ((self.x - self.x_CoM + self.box_width +
                self.input_height - mouse_x)**2 +
                (self.y - mouse_y)**2 < self.port_radius**2):
            device_id = self.device.device_id
        return (device_id, port_id)

    def get_port_coor(self, port_id):
        """Returns the coordinates of a port of the device"""
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

    def render(self, dark_mode):
        if dark_mode:
            GL.glColor3f(0.03, 0.172, 0.422)
        else:
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
        if dark_mode:
            color = (0.7, 0.7, 0.7)
        else:
            color = (0.0, 0.0, 0.0)

        if self.device.outputs[None]:
            if dark_mode:
                color = (0.647, 0.41, 0.77)
            else:
                color = (0.617, 0.0, 0.0)

        draw_circle(self.port_radius, self.x + self.box_width +
                    self.straight_box_width -
                    self.x_CoM, self.y, color)
        if self.NOR:
            if dark_mode:
                draw_circle(self.port_radius - 2, self.x + self.box_width -
                            self.straight_box_width - self.x_CoM +
                            self.input_height, self.y, (0.2, 0.2, 0.2))
            else:
                draw_circle(self.port_radius - 2, self.x + self.box_width -
                            self.straight_box_width - self.x_CoM +
                            self.input_height, self.y, (1.0, 1.0, 1.0))

        for dy in np.linspace(
                -c + self.input_height/2, c -
                self.input_height/2, self.inputs):
            dx = self.indent_width*(1 - (dy / c)**2)
            if dark_mode:
                draw_circle(self.port_radius, self.x -
                            self.x_CoM, self.y+dy, (0.7, 0.7, 0.7))
                vertices = [(self.x - self.x_CoM, self.y + dy),
                            (self.x - self.x_CoM + dx, self.y + dy)]
                line_with_thickness(vertices, 3, (0.7, 0.7, 0.7))
            else:
                draw_circle(self.port_radius, self.x -
                            self.x_CoM, self.y+dy, (0.0, 0.0, 0.0))
                vertices = [(self.x - self.x_CoM, self.y + dy),
                            (self.x - self.x_CoM + dx, self.y + dy)]
                line_with_thickness(vertices, 3, (0.0, 0.0, 0.0))

        if self.show_text:

            draw_text(self.x-5, self.y - self.input_height *
                      self.inputs/2 - 19, self.name_string, dark_mode)

    def is_clicked(self, mouse_x, mouse_y):
        """Checks if device is clicked"""
        x_low = self.x - self.x_CoM
        x_high = self.x - self.x_CoM + self.box_width + self.straight_box_width
        if (x_low < mouse_x < x_high and
                self.y - self.input_height * self.inputs/2 < mouse_y <
                self.y + self.input_height * self.inputs/2):
            return True
        else:
            return False

    def is_port_clicked(self, mouse_x, mouse_y):
        """Checks if a port is clicked and returns
         the device and port id"""
        device_id = None
        port_id = None
        for i in range(self.inputs):
            if ((self.x - self.x_CoM - mouse_x)**2 +
                    (self.y + self.input_height *
                        (self.inputs/2 - i - 0.5) - mouse_y)**2 <
                    (self.port_radius+3)**2):
                port_id = self.names.query("I" + str(i+1))
                device_id = self.device.device_id
                return (device_id, port_id)
        if ((self.x - self.x_CoM + self.box_width +
            self.straight_box_width - mouse_x)**2 +
                (self.y - mouse_y)**2 < self.port_radius**2):
            device_id = self.device.device_id
        return (device_id, port_id)

    def get_port_coor(self, port_id):
        """Returns the coordinates of a port of the device"""
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

    def render(self, dark_mode):
        if dark_mode:
            GL.glColor3f(0.03, 0.172, 0.422)
        else:
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
        if dark_mode:
            line_with_thickness(vertices, self.thickness, (0.03, 0.172, 0.422))
            color = (0.7, 0.7, 0.7)
        else:
            line_with_thickness(vertices, self.thickness,
                                (0.212, 0.271, 0.310))
            color = (0.0, 0.0, 0.0)
        if self.device.outputs[None]:
            if dark_mode:
                color = (0.647, 0.41, 0.77)
            else:
                color = (0.617, 0.0, 0.0)
        draw_circle(self.port_radius, self.x + self.box_width +
                    self.straight_box_width -
                    self.x_CoM, self.y, color)

        for dy in np.linspace(-c + self.input_height/2, c -
                              self.input_height/2, self.inputs):
            dx = self.indent_width*(1 - (dy / c)**2)
            if dark_mode:
                draw_circle(self.port_radius, self.x -
                            self.x_CoM, self.y+dy, (0.7, 0.7, 0.7))
                vertices = [(self.x - self.x_CoM, self.y + dy),
                            (self.x - self.x_CoM + dx, self.y + dy)]
                line_with_thickness(vertices, 3, (0.7, 0.7, 0.7))
            else:
                draw_circle(self.port_radius, self.x -
                            self.x_CoM, self.y+dy, (0.0, 0.0, 0.0))
                vertices = [(self.x - self.x_CoM, self.y + dy),
                            (self.x - self.x_CoM + dx, self.y + dy)]
                line_with_thickness(vertices, 3, (0.0, 0.0, 0.0))
        if self.show_text:

            draw_text(self.x-5, self.y - self.input_height *
                      self.inputs/2 - 19, self.name_string, dark_mode)

    def is_clicked(self, mouse_x, mouse_y):
        """Checks if device is clicked"""
        x_low = self.x - self.x_CoM - self.gap_width
        x_high = self.x - self.x_CoM + self.box_width + self.straight_box_width
        if (x_low < mouse_x < x_high and
            self.y - self.input_height < mouse_y <
                self.y + self.input_height):
            return True
        else:
            return False

    def is_port_clicked(self, mouse_x, mouse_y):
        """Checks if a port is clicked and returns
         the device and port id"""
        device_id = None
        port_id = None
        for i in range(2):
            if ((self.x - self.x_CoM - mouse_x - self.gap_width)**2 +
                (self.y + self.input_height * (0.5 - i) - mouse_y)**2 <
                    (self.port_radius+3)**2):
                port_id = self.names.query("I" + str(i+1))
                device_id = self.device.device_id
                return (device_id, port_id)
        if ((self.x - self.x_CoM + self.box_width +
            self.straight_box_width - mouse_x)**2 +
                (self.y - mouse_y)**2 < self.port_radius**2):
            device_id = self.device.device_id
        return (device_id, port_id)

    def get_port_coor(self, port_id):
        """Returns the coordinates of a port of the device"""
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


class D_type(Device_GL):
    """Creates an Dtype device for animation"""

    def __init__(self, x, y, device, names):
        super().__init__(x, y, device, names)

        self.width = 80
        self.input_height = 35
        self.port_radius = 7
        self.no_segments = 100
        self.show_text = True

    def render(self, dark_mode):
        if dark_mode:
            GL.glColor3f(0.03, 0.172, 0.422)
        else:
            GL.glColor3f(0.212, 0.271, 0.310)
        GL.glBegin(GL.GL_POLYGON)
        GL.glVertex2f(self.x - self.width/2, self.y + self.input_height*2)
        GL.glVertex2f(self.x + self.width/2, self.y + self.input_height*2)
        GL.glVertex2f(self.x + self.width/2, self.y - self.input_height*2)
        GL.glVertex2f(self.x - self.width/2, self.y - self.input_height*2)
        GL.glEnd()

        vertices = []
        if dark_mode:
            for dy in np.linspace(
                    -1.5 * self.input_height, 1.5 * self.input_height, 4):
                draw_circle(self.port_radius, self.x - self.width /
                            2, self.y + dy, (0.7, 0.7, 0.7))

        else:
            for dy in np.linspace(
                    -1.5 * self.input_height, 1.5 * self.input_height, 4):
                draw_circle(self.port_radius, self.x - self.width /
                            2, self.y + dy, (0.0, 0.0, 0.0))
        if dark_mode:
            color = (0.7, 0.7, 0.7)
        else:
            color = (0.0, 0.0, 0.0)
        if self.device.outputs[self.names.query("Q")]:
            if dark_mode:
                color = (0.647, 0.41, 0.77)
            else:
                color = (0.617, 0.0, 0.0)
        draw_circle(self.port_radius, self.x + self.width/2,
                    self.y + self.input_height/2, color)
        if dark_mode:
            color = (0.7, 0.7, 0.7)
        else:
            color = (0.0, 0.0, 0.0)
        if self.device.outputs[self.names.query("QBAR")]:
            if not dark_mode:
                color = (0.617, 0.0, 0.0)
            else:
                color = (0.647, 0.41, 0.77)
        draw_circle(self.port_radius, self.x + self.width/2,
                    self.y - self.input_height/2, color)

        render_text_scale('DATA', 1.5, self.x - self.width/2 +
                          10, self.y + self.input_height*1.5 - 4,
                          (1, 1, 1), 0.1)
        render_text_scale('CLK', 1.5, self.x - self.width/2 +
                          10, self.y + self.input_height/2-4,
                          (1, 1, 1), 0.1)
        render_text_scale('SET', 1.5, self.x - self.width/2 +
                          10, self.y - self.input_height/2-4,
                          (1, 1, 1), 0.1)
        render_text_scale('CLR', 1.5, self.x - self.width/2 +
                          10, self.y - self.input_height*1.5-4,
                          (1, 1, 1), 0.1)
        render_text_scale('Q', 1.5, self.x + self.width/2 -
                          19, self.y + self.input_height/2-4,
                          (1, 1, 1), 0.1)
        render_text_scale(overline('Q'), 1.5, self.x + self.width /
                          2 - 19, self.y - self.input_height/2-4,
                          (1, 1, 1), 0.1)
        line_with_thickness([(self.x + self.width/2-19, self.y -
                            self.input_height/2+9.5),
                            (self.x + self.width/2 - 11,
                            self.y - self.input_height/2+9.5)],
                            0.9, (1, 1, 1))

        if self.show_text:

            draw_text(self.x-7, self.y - self.input_height *
                      self.inputs/2 - 19, self.name_string, dark_mode)

    def is_clicked(self, mouse_x, mouse_y):
        """Checks if device is clicked"""
        x_low = self.x - self.width/2
        x_high = self.x + self.width
        if (x_low < mouse_x < x_high and
                self.y - self.input_height*2 < mouse_y <
                self.y + 2*self.input_height):
            return True
        else:
            return False

    def is_port_clicked(self, mouse_x, mouse_y):
        """Checks if a port is clicked and returns
         the device and port id"""
        device_id = self.device.device_id
        port_id = None
        if ((self.x - self.width/2 - mouse_x)**2 +
            (self.y + self.input_height * 1.5 - mouse_y)**2 <
                (self.port_radius+3)**2):
            port_id = self.names.query("DATA")
            return (device_id, port_id)
        elif ((self.x - self.width/2 - mouse_x)**2 +
              (self.y + self.input_height * 0.5 - mouse_y)**2 <
              (self.port_radius+3)**2):
            port_id = self.names.query("CLK")
            return (device_id, port_id)
        elif ((self.x - self.width/2 - mouse_x)**2 +
              (self.y - self.input_height * 0.5 - mouse_y)**2 <
              (self.port_radius+3)**2):
            port_id = self.names.query("SET")
            return (device_id, port_id)
        elif ((self.x - self.width/2 - mouse_x)**2 +
              (self.y - self.input_height * 1.5 - mouse_y)**2 <
              (self.port_radius+3)**2):
            port_id = self.names.query("CLEAR")
            return (device_id, port_id)
        elif ((self.x + self.width/2 - mouse_x)**2 +
              (self.y + self.input_height * 0.5 - mouse_y)**2 <
              (self.port_radius+3)**2):
            port_id = self.names.query("Q")
            return (device_id, port_id)
        elif ((self.x + self.width/2 - mouse_x)**2 +
              (self.y - self.input_height * 0.5 - mouse_y)**2 <
              (self.port_radius+3)**2):
            port_id = self.names.query("QBAR")
            return (device_id, port_id)
        return (None, port_id)

    def get_port_coor(self, port_id):
        """Returns the coordinates of a port of the device"""
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

    def render(self, dark_mode):
        """Animates the clock"""
        if dark_mode:
            GL.glColor3f(0.03, 0.172, 0.422)
        else:
            GL.glColor3f(0.212, 0.271, 0.310)
        GL.glBegin(GL.GL_POLYGON)
        GL.glVertex2f(self.x - self.width/2, self.y + self.half_height)
        GL.glVertex2f(self.x + self.width/2, self.y + self.half_height)
        GL.glVertex2f(self.x + self.width/2, self.y - self.half_height)
        GL.glVertex2f(self.x - self.width/2, self.y - self.half_height)
        GL.glEnd()

        if self.device.outputs[None]:
            if dark_mode:
                GL.glColor3f(0.647, 0.41, 0.77)
                color = (0.647, 0.41, 0.77)
            else:
                GL.glColor3f(0.617, 0.0, 0.0)
                color = (0.617, 0.0, 0.0)
        else:
            if dark_mode:
                GL.glColor3f(0.7, 0.7, 0.7)
                color = (0.7, 0.7, 0.7)
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
        if dark_mode:
            if self.device.outputs[None]:
                color = (0.647, 0.41, 0.77)
            else:
                color = (0.7, 0.7, 0.7)
        elif self.device.outputs[None]:
            color = (0.617, 0, 0)
        else:
            color = (0,0,0)
        draw_circle(self.port_radius, self.x +
                    self.width/2, self.y, color)
        if self.show_text:

            draw_text(self.x-15, self.y - self.half_height *
                      2 - 5, self.name_string, dark_mode)

    def is_clicked(self, mouse_x, mouse_y):
        """Checks if device is clicked"""
        x_low = self.x - self.width/2
        x_high = self.x + self.width
        if (x_low < mouse_x < x_high and
            self.y - self.half_height < mouse_y <
                self.y + self.half_height):
            return True
        else:
            return False

    def is_port_clicked(self, mouse_x, mouse_y):
        """Checks if a port is clicked and returns
         the device and port id"""
        device_id = None
        port_id = None
        if ((self.x + self.width/2 - mouse_x)**2 +
                (self.y - mouse_y)**2 < (self.port_radius+3)**2):
            device_id = self.device.device_id
        return (device_id, port_id)

    def get_port_coor(self, port_id):
        """Returns the coordinates of a port of the device"""
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

    def render(self, dark_mode):
        """Animates the switch"""
        if dark_mode:
            color = (0.7, 0.7, 0.7)
        else:
            color = (0.0, 0.0, 0.0)
        if dark_mode:
            draw_circle(self.port_radius, self.x - self.x_CoM,
                        self.y - self.half_height, (0.7, 0.7, 0.7))
            draw_circle(self.port_radius, self.x - self.x_CoM,
                        self.y + self.half_height, (0.647, 0.41, 0.77))
            vertices = [(self.x - self.x_CoM +
                        self.width, self.y)]
        else:
            draw_circle(self.port_radius, self.x - self.x_CoM,
                        self.y - self.half_height, (0.0, 0.0, 0.0))
            draw_circle(self.port_radius, self.x - self.x_CoM,
                        self.y + self.half_height, (0.617, 0.0, 0.0))
            vertices = [(self.x - self.x_CoM +
                        self.width, self.y)]
        if self.device.switch_state == 1:
            if dark_mode:
                color = (0.647, 0.41, 0.77)
            else:
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

            draw_text(self.x-8, self.y - self.half_height *
                      2.5, self.name_string, dark_mode)

    def is_clicked(self, mouse_x, mouse_y):
        """Checks if device is clicked"""
        x_low = self.x - self.x_CoM
        x_high = self.x - self.x_CoM + self.width
        if (x_low < mouse_x < x_high and
            self.y - self.half_height < mouse_y <
                self.y + self.half_height):
            return True
        else:
            return False

    def get_port_coor(self, port_id):
        """Returns the coordinates of a port of the device"""
        if port_id is None:
            return (self.x - self.x_CoM + self.width, self.y)
        else:
            raise IndexError("Port does not exist")

    def is_port_clicked(self, mouse_x, mouse_y):
        """Checks if a port is clicked and returns
         the device and port id"""
        device_id = None
        port_id = None
        if ((self.x - self.x_CoM + self.width - mouse_x)**2 +
                (self.y - mouse_y)**2 < (self.port_radius+3)**2):
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

    def __init__(self, parent, mother, devices, monitors, names, network):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)
        self.parent = parent
        self.mother = mother

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
        self.choose_monitor = False
        self.temp_connection = None
        self.dark_mode = False

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)
        self.Bind(wx.EVT_ENTER_WINDOW, self. on_enter_window)

        self.init_objects(devices, names)

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
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def init_objects(self, devices, names):
        """Create all the initial devices as classes to animate"""
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

        for id in clock_ids:
            device = devices.get_device(id)
            clock = Clock(x, y, device, names)
            y += 200
            self.objects.append(clock)
            self.devices_GL_list.append(clock)

        for id in switch_ids:
            device = devices.get_device(id)
            switch = Switch(x, y, device, names)
            y += 200
            self.objects.append(switch)
            self.devices_GL_list.append(switch)
            self.switch_GL_list.append(switch)

        y = 100
        x += 200

        for id in and_gate_ids:
            device = devices.get_device(id)
            and_gate = And_gate(x, y, device, names, False)
            y += 200
            if y > 600:
                x += 200
                y = 100
            self.objects.append(and_gate)
            self.devices_GL_list.append(and_gate)

        for id in nand_gate_ids:
            device = devices.get_device(id)
            nand_gate = And_gate(x, y, device, names, True)
            y += 200
            if y > 600:
                x += 200
                y = 100
            self.objects.append(nand_gate)
            self.devices_GL_list.append(nand_gate)

        for id in or_gate_ids:
            device = devices.get_device(id)
            or_gate = Or_gate(x, y, device, names, False)
            y += 200
            if y > 600:
                x += 200
                y = 100
            self.objects.append(or_gate)
            self.devices_GL_list.append(or_gate)

        for id in nor_gate_ids:
            device = devices.get_device(id)
            nor_gate = Or_gate(x, y, device, names, True)
            y += 200
            if y > 600:
                x += 200
                y = 100
            self.objects.append(nor_gate)
            self.devices_GL_list.append(nor_gate)

        for id in dtype_ids:
            device = devices.get_device(id)
            dtype = D_type(x, y, device, names)
            y += 200
            if y > 600:
                x += 200
                y = 100
            self.objects.append(dtype)
            self.devices_GL_list.append(dtype)

        for id in xor_gate_ids:
            device = devices.get_device(id)
            xor_gate = Xor_gate(x, y, device, names)
            y += 200
            if y > 600:
                x += 200
                y = 100
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
            monitor = Monitor(self.names, device_GL, port_id)
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

        self.render_grid(self.dark_mode)

        # Draw a sample signal trace
        for ob in self.objects:
            ob.render(self.dark_mode)

        if self.temp_connection is not None:
            self.temp_connection.render(self.dark_mode)

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

        # Updates the half made connections coordinates
        if self.temp_connection is not None:
            self.temp_connection.mouse_x = ox
            self.temp_connection.mouse_y = oy
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
            # Checks for objects clicked
            for ob in self.devices_GL_list:
                if ob.is_clicked(ox, oy):
                    ob.clicked = True
                    self.object_clicked = True
                    break
            # Checks for new connection if in connection mode
            if self.connection_list[0]:
                self.check_connection_made(ox, oy)
            # Checks for new monitor points in monitor mode
            if self.choose_monitor:
                for ob in self.devices_GL_list:
                    device_id, port_id = ob.is_port_clicked(ox, oy)
                    if device_id is not None:
                        error_code = self.monitors.make_monitor(
                            device_id, port_id, self.mother.cycles_completed)
                        if error_code == self.monitors.NO_ERROR:
                            [device_GL] = [
                                i for i in self.devices_GL_list
                                if i.id == device_id]
                            monitor = Monitor(self.names, device_GL, port_id)
                            self.objects.append(monitor)
                            self.monitors_GL.append(monitor)
                            self.mother.trace_canvas.Refresh()
                        elif self.monitors.remove_monitor(
                                device_id, port_id):
                            [device_GL] = [
                                i for i in self.monitors_GL
                                if i.device_GL.device.device_id == device_id]
                            self.monitors_GL.remove(device_GL)
                            self.objects.remove(device_GL)
                            self.mother.trace_canvas.Refresh()
                        else:
                            self.raise_error("Choose a valid monitor point")
        # Sets all devices to not clicked
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
            if self.object_clicked:
                self.object_clicked = False
                for ob in self.devices_GL_list:
                    ob.clicked = False
        # Sets all devices to not clicked
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
            if self.object_clicked:
                self.object_clicked = False
                for ob in self.devices_GL_list:
                    ob.clicked = False
        # Scrolls canvas or moves device
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
        if event.GetWheelRotation() < 0 and self.zoom > 0.5:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0 and self.zoom < 2:
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

    def check_connection_made(self, ox, oy):
        """Handles click events when in connection mode to
         create a temporary connection or make a connection"""
        for ob in self.devices_GL_list:
            device_id, port_id = ob.is_port_clicked(ox, oy)
            if device_id is not None:
                if self.connection_list[1] is not None:
                    error_code = self.network.make_connection(
                        *self.connection_list[1:], device_id, port_id)
                    if error_code == self.network.NO_ERROR:
                        # Raise error message otherwise
                        [device_GL] = [
                            i for i in self.devices_GL_list
                            if i.id == device_id]
                        if port_id in device_GL.device.inputs:
                            self.temp_connection.input_device_GL = device_GL
                            self.temp_connection.input_port_id = port_id
                        else:
                            self.temp_connection.output_device_GL = device_GL
                            self.temp_connection.output_port_id = port_id
                        self.objects.append(
                            self.temp_connection)
                        self.connections.append(
                            self.temp_connection)
                    else:
                        self.raise_error("Connection invalid")
                    self.temp_connection = None
                    self.connection_list = [True, None, None]
                else:
                    self.connection_list[1] = device_id
                    self.connection_list[2] = port_id
                    [device_GL] = [
                        i for i in self.devices_GL_list
                        if i.id == device_id]
                    if port_id in device_GL.device.inputs:
                        self.temp_connection = Connection_GL(
                            device_GL, None, port_id, None)
                    else:
                        self.temp_connection = Connection_GL(
                            None, device_GL, None, port_id)
                    self.temp_connection.mouse_x = ox
                    self.temp_connection.mouse_y = oy
                break

    def on_double_click(self, event):
        """Changes switches on a double click"""
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

    def on_enter_window(self, event):
        """Sets focus to this canvas on mouse entering"""
        self.SetFocus()

    def render_text(self, text, x_pos, y_pos, dark_mode):
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

    def render_grid(self, dark_mode):
        """Animates the background grid"""

        grid_spacing = 50
        width, height = self.GetSize()

        x_min = (-self.pan_x/self.zoom)//grid_spacing * \
            grid_spacing - grid_spacing
        x_max = (width - self.pan_x) / self.zoom
        y_min = (-self.pan_y/self.zoom)//grid_spacing * \
            grid_spacing - grid_spacing
        y_max = (height - self.pan_y) / self.zoom
        x = x_min
        if dark_mode:
            GL.glColor3f(0.4, 0.4, 0.4)

        else:
            GL.glColor3f(0.7, 0.7, 0.7)
        GL.glLineWidth(1.0)
        GL.glBegin(GL.GL_LINES)
        # while x < width/self.zoom:
        while x < x_max:
            GL.glVertex2f(x, y_min)
            GL.glVertex2f(x, y_max)
            x += grid_spacing
        GL.glEnd()

        GL.glBegin(GL.GL_LINES)
        y = y_min
        while y < y_max:
            GL.glVertex2f(x_min, y)
            GL.glVertex2f(x_max, y)
            y += grid_spacing
        GL.glEnd()

    def create_device(self, device_name, device_type, qualifier=None):
        """Creates a new device"""
        [device_id] = self.names.lookup([device_name])
        error_code = self.devices.make_device(
            device_id, device_type, qualifier)
        if error_code == self.devices.NO_ERROR:
            device = self.devices.get_device(device_id)
            if device_type == self.devices.AND:
                device_GL = And_gate(400, 100, device, self.names, False)
            elif device_type == self.devices.NAND:
                device_GL = And_gate(400, 100, device, self.names, True)
            elif device_type == self.devices.OR:
                device_GL = Or_gate(400, 100, device, self.names, False)
            elif device_type == self.devices.NOR:
                device_GL = Or_gate(400, 100, device, self.names, True)
            elif device_type == self.devices.SWITCH:
                device_GL = Switch(400, 100, device, self.names)
                self.switch_GL_list.append(device_GL)
            elif device_type == self.devices.XOR:
                device_GL = Xor_gate(400, 100, device, self.names)
            elif device_type == self.devices.D_TYPE:
                device_GL = D_type(400, 100, device, self.names)
            elif device_type == self.devices.CLOCK:
                device_GL = Clock(400, 100, device, self.names)
            self.objects.append(device_GL)
            self.devices_GL_list.append(device_GL)
        elif error_code == self.devices.INVALID_QUALIFIER:
            self.raise_error("Please use a valid qualifier")
            return False
        elif error_code == self.devices.DEVICE_PRESENT:
            self.raise_error(
                "Device name already in use - please use another device name")
            return False
        self.Refresh()
        return True

    def raise_error(self, string):
        """Pop up with an error message"""
        dlg = GMD(None, string,
                  "Error", wx.OK | wx.ICON_ERROR | 0x40)
        dlg.SetIcon(wx.ArtProvider.GetIcon(wx.ART_WARNING))
        dlg.ShowModal()
        dlg.Destroy()

    def create_file_string(self):
        file_string = ""
        switch_ids = self.devices.find_devices(self.devices.SWITCH)
        if switch_ids:
            file_string += "SWITCH "
            for i, switch_id in enumerate(switch_ids):
                if i:
                    file_string += ", "
                switch_name = self.names.get_name_string(switch_id)
                device = self.devices.get_device(switch_id)
                switch_state = device.outputs[None]
                file_string +=  str(switch_state) + " " + switch_name
            file_string += ";\n"

        clock_ids = self.devices.find_devices(self.devices.CLOCK)
        if clock_ids:
            file_string += "CLOCK "
            for i, clock_id in enumerate(clock_ids):
                if i:
                    file_string += ", "
                clock_name = self.names.get_name_string(clock_id)
                device = self.devices.get_device(clock_id)
                file_string +=  str(device.clock_half_period) + " " + clock_name
            file_string += ";\n"

        and_ids = self.devices.find_devices(self.devices.AND)
        if and_ids:
            file_string += "AND "
            for i, and_id in enumerate(and_ids):
                if i:
                    file_string += ", "
                and_name = self.names.get_name_string(and_id)
                device = self.devices.get_device(and_id)
                inputs = len(device.inputs.keys())
                file_string +=  str(inputs) + " " + and_name
            file_string += ";\n"

        nand_ids = self.devices.find_devices(self.devices.NAND)
        if nand_ids:
            file_string += "NAND "
            for i, nand_id in enumerate(nand_ids):
                if i:
                    file_string += ", "
                nand_name = self.names.get_name_string(nand_id)
                device = self.devices.get_device(nand_id)
                inputs = len(device.inputs.keys())
                file_string +=  str(inputs) + " " + nand_name
            file_string += ";\n"

        or_ids = self.devices.find_devices(self.devices.OR)
        if or_ids:
            file_string += "OR "
            for i, or_id in enumerate(or_ids):
                if i:
                    file_string += ", "
                or_name = self.names.get_name_string(or_id)
                device = self.devices.get_device(or_id)
                inputs = len(device.inputs.keys())
                file_string +=  str(inputs) + " " + or_name
            file_string += ";\n"
        
        nor_ids = self.devices.find_devices(self.devices.NOR)
        if and_ids:
            file_string += "NOR "
            for i, nor_id in enumerate(nor_ids):
                if i:
                    file_string += ", "
                nor_name = self.names.get_name_string(nor_id)
                device = self.devices.get_device(nor_id)
                inputs = len(device.inputs.keys())
                file_string +=  str(inputs) + " " + nor_name
            file_string += ";\n"

        xor_ids = self.devices.find_devices(self.devices.XOR)
        if xor_ids:
            file_string += "XOR "
            for i, xor_id in enumerate(xor_ids):
                if i:
                    file_string += ", "
                xor_name = self.names.get_name_string(xor_id)
                device = self.devices.get_device(xor_id)
                file_string += xor_name
            file_string += ";\n"
        
        dtype_ids = self.devices.find_devices(self.devices.D_TYPE)
        if dtype_ids:
            file_string += "DTYPE "
            for i, dtype_id in enumerate(dtype_ids):
                if i:
                    file_string += ", "
                dtype_name = self.names.get_name_string(dtype_id)
                device = self.devices.get_device(dtype_id)
                file_string += dtype_name
            file_string += ";\n"
        
        if bool(self.monitors.monitors_dictionary):
            file_string += "MONITOR "
            i = 0
            for device_id, port_id in self.monitors.monitors_dictionary:
                if i:
                    file_string += ", "
                file_string += self.get_port_string(device_id, port_id)
                i += 1
            file_string += ";\n"
        
        if self.connections:
            file_string += "CONNECT "
            for i, connection in enumerate(self.connections):
                if i:
                    file_string += ", "
                file_string += self.get_port_string(connection.input_device_GL.device.device_id, connection.input_port_id) + " > " + self.get_port_string(connection.output_device_GL.device.device_id, connection.output_port_id)
            file_string += ";\n"
        return file_string

    def get_port_string(self, device_id, port_id):
        port_string = self.names.get_name_string(device_id)
        if port_id is None:
            return port_string
        port_string += "." + self.names.get_name_string(port_id)
        return port_string