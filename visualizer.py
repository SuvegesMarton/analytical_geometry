import tkinter as tk
from matrix_calculations import solve_system_of_2_equations
from solve_polynomial import main as solvpol
from solve_polynomial import evaluate as eval_pol
from math import pi, atan, sqrt, sin, cos
# dimensions of GUI
CANVAS_HEIGHT = 900
CANVAS_WIDTH = 1400

# how much zooming happens / click
ZOOM_STEPSIZE = 1.05

# width of elements under the cursor
HIGHLIGHT_WIDTH = 3

# delays for moving elements on screen
BOUNCER_ROTATION_DELAY = 20
BALL_PHYSICS_DELAY = 20


# calculate the direction between two vectors
def get_angle_between_vectors(vector1, vector2):
    if vector1[0] == 0:
        if vector1[0] >= 0:
            vector1_direction = pi / 2
        else:
            vector1_direction = pi / 2 * 3
    else:
        vector1_direction = atan(vector1[1] / vector1[0])
        if vector1[1] < 0:
            vector1_direction += pi
        if vector1[1] == 0 and vector1[0] < 0:
            vector1_direction = pi

    if vector2[0] == 0:
        if vector2[0] >= 0:
            vector2_direction = pi / 2
        else:
            vector2_direction = pi / 2 * 3
    else:
        vector2_direction = atan(vector2[1] / vector2[0])
        if vector2[1] < 0:
            vector2_direction += pi
        if vector2[1] == 0 and vector2[0] < 0:
            vector2_direction = pi

    angle_between = abs(vector1_direction - vector2_direction)
    if angle_between > pi:
        return pi * 2 - angle_between
    else:
        return angle_between


def two_lines_intersection(x1, y1, c1, x2, y2, c2):
    # equation of the line: x_coeff * x + y_coeff * y = c
    if y1 == y2 == 0:
        return None, None
    if not (y1 == 0 or y2 == 0) and x1 / y1 == x2 / y2:
        return None, None
    return solve_system_of_2_equations(x1, y1, c1, x2, y2, c2)


def line_circle_intersection(lx, ly, c, ox, oy, r):
    # equation of the circle: (x - ox) ** 2 + (y - oy) ** 2 = r ** 2
    # equation of the line: lx * x + ly * y = c
    # from line: x = (c - ly * y) / lx, if lx != 0

    if lx == 0:
        # if lx is zero, the line equation fixes the y value
        if ly == 0:
            # i dunno what that is but not a line equation
            print('Faulty line equation!')
            return []

        y_constant = c / ly
        if round(r**2 - (y_constant - oy)**2, 5) < 0:
            return []

        if round(r**2 - (y_constant - oy)**2, 5) == 0:
            x_solution = +sqrt(r**2 - (y_constant - oy)**2) + ox
            y_solution = (c - lx * x_solution) / ly
            return [[x_solution, y_solution]]

        if round(r**2 - (y_constant - oy)**2, 5) > 0:
            x_solution1 = +sqrt(r**2 - (y_constant - oy)**2) + ox
            x_solution2 = -sqrt(r**2 - (y_constant - oy)**2) + ox
            y_solution1 = (c - lx * x_solution1) / ly
            y_solution2 = (c - lx * x_solution2) / ly
            return [[x_solution1, y_solution1], [x_solution2, y_solution2]]
    else:
        # substitute x into the circle equation:
        # (((c - ly * y) / lx) - ox) ** 2 + (y - oy) ** 2 = r ** 2
        # (c / lx - ly * y / lx - ox) ** 2 + (y - oy) ** 2 = r ** 2
        # (- y * ly / lx + c / lx  - ox) ** 2 + (y - oy) ** 2 = r ** 2
        # ((ly/lx)**2) * (y ** 2) + 2*(-y*ly/lx)*(c/lx - ox) + (c/lx - ox) ** 2 + y**2 - 2*y*(oy) + oy**2 = r**2

        # (y**2) * ((ly/lx)**2 + 1) + y * (-2*ly/lx*(c/lx - ox) - 2*oy) + ((c/lx - ox)**2 + oy**2 - r**2) = 0
        # the discriminant of this quadratic equation(b**2 - 4*a*c):
        discriminant = (-2*ly/lx*(c/lx - ox) - 2*oy) ** 2 - 4 * ((ly/lx)**2 + 1) * ((c/lx - ox)**2 + oy**2 - r**2)
        if round(discriminant, 5) < 0:
            return []
        if round(discriminant, 5) == 0:
            # x = -b / 2 * a
            y_solution = -(-2*ly/lx*(c/lx - ox) - 2*oy) / (2 * ((ly/lx)**2 + 1))
            # from the line equation
            x_solution = (c - ly * y_solution) / lx
            return [[x_solution, y_solution]]
        if round(discriminant, 5) > 0:
            # y1,y2 = (-b +- sqrt(discriminant)) / 2 * a
            y_solution1 = ((2*ly/lx*(c/lx - ox) + 2*oy) + sqrt(discriminant)) / (2 * ((ly/lx)**2 + 1))
            y_solution2 = ((2*ly/lx*(c/lx - ox) + 2*oy) - sqrt(discriminant)) / (2 * ((ly/lx)**2 + 1))
            # y1,y2 from the line equation
            x_solution1 = (c - ly * y_solution1) / lx
            x_solution2 = (c - ly * y_solution2) / lx
            return [[x_solution1, y_solution1], [x_solution2, y_solution2]]


def line_ordered_polynomial_intersection(x, y, c, exponents, coefficients):
    if y == 0:
        intersection_x = eval_pol(exponents, coefficients, c/x)
        if intersection_x is None:
            return None
        else:
            return [[intersection_x, c/x]]
    else:
        if 1 in exponents:
            coefficients[exponents.index(1)] += x/y
        else:
            exponents.append(1)
            coefficients.append(x/y)
        if 0 in exponents:
            coefficients[exponents.index(0)] -= c/y
        else:
            exponents.append(0)
            coefficients.append(-c/y)
        # solve the polynomial to get the x coords of intersections
        solutions = solvpol(exponents, coefficients, degree_of_accuracy=700)
        # calculate y coords from the line's equation
        intersections = []
        for s in solutions:
            intersections.append([s, (c-s*x)/y])
        return intersections


def radian_to_degree(rad):
    return rad / 2 / pi * 360


def get_vector_direction(x, y):
    if x == 0:
        if y > 0:
            return pi / 2
        else:
            return pi / 2 * 3
    return atan(y / x)


def point_element_distance(x, y, element):
    if element.type == 'circle' or element.type == 'ball':
        # distance from the middle of the circle
        dist = ((x - element.origo_x) ** 2 + (y - element.origo_y) ** 2) ** 0.5
        # direction vector to the point from the origo
        #vector_x = x - element.origo_x
        #vector_y = y - element.origo_y
        # vector_x * c, vector_y * c -> closest point on the perimeter
        # (vector_x * c) ** 2 + (vector_y * c) ** 2 = radius ** 2
        #c = (element.radius**2 / (vector_x**2 + vector_y**2)) ** 0.5

        # return distance from the perimeter
        return abs(dist - element.radius)

    elif element.type == 'line':
        distance = abs(x*element.x_coefficient + y*element.y_coefficient - element.c) / (element.x_coefficient ** 2 + element.y_coefficient**2) ** 0.5
        return distance
    else:
        return 10e10
'''        y_at_x = element.evaluate_at_x(x)
        if y_at_x is None:
            return 10e10
        elif not isinstance(y_at_x, list):
            y_at_x = [y_at_x]
        for i in range(len(y_at_x)):
            y_at_x[i] = abs(y_at_x[i] - y)
        return min(y_at_x)'''


def get_bounce_direction_vector_from_vectors(surface_perpendicular_x, surface_perpendicular_y, incoming_x, incoming_y):
    # get the incoming vector's direction
    if incoming_x == 0:
        if incoming_y > 0:
            incoming_direction = pi/2
        else:
            incoming_direction = 3*pi/2
    else:
        incoming_direction = atan(incoming_y / incoming_x)
        if incoming_x < 0:
            incoming_direction += pi

    # get the angle between the perpendicular vector and the bouncer's direction
    perp_vector_relative_angle = get_vector_direction(surface_perpendicular_x, surface_perpendicular_y) - incoming_direction
    collision_angle = get_angle_between_vectors([surface_perpendicular_x, surface_perpendicular_y], [incoming_x, incoming_y])
    # get the angle between perpendicular vector and bouncer between 0 and 90 degrees, by eliminating angles
    # calculated on the -1*perp_vector 's data
    if collision_angle > pi / 2:
        collision_angle = pi - collision_angle

    # get the outgoing vector's direction
    if perp_vector_relative_angle % pi >= pi / 2:
        new_direction = incoming_direction + 2 * (pi / 2 - collision_angle)
    else:
        new_direction = incoming_direction - 2 * (pi / 2 - collision_angle)
    out_x = round(cos(new_direction), 10)
    out_y = round(sin(new_direction), 10)
    return out_x, out_y, new_direction


class CoordinateSystem:
    def __init__(self, canvas, draw_it=True):
        # location of the origo compared to the GUI coordsystem
        self.origo_coord_x_on_gui = CANVAS_WIDTH / 2
        self.origo_coord_y_on_gui = CANVAS_HEIGHT / 2

        # number of pixels / coordsystem units
        self.x_stepsize_on_gui = 8
        self.y_stepsize_on_gui = 8
        # list of existing elements in the coordinate system
        self.elements = []

        self.canvas = canvas
        if draw_it:
            self.draw()

        # gui variables
        self.last_mouse_x = None
        self.last_mouse_y = None
        self.element_under_cursor = None

    # get the borders of the GUI surface expressed with the metrics of this coordinate system
    def get_gui_edge_with_system_coords(self):
        left_border = -self.origo_coord_x_on_gui / self.x_stepsize_on_gui
        right_border = (CANVAS_WIDTH - self.origo_coord_x_on_gui) / self.y_stepsize_on_gui
        upper_border = self.origo_coord_y_on_gui / self.y_stepsize_on_gui
        lower_border = (self.origo_coord_y_on_gui - CANVAS_HEIGHT) / self.y_stepsize_on_gui
        return left_border, right_border, upper_border, lower_border

    # convert between coordinates used by the GUI and this coordinate system
    def system_coord_to_gui_coord(self, x, y):
        gui_y = -(y * self.y_stepsize_on_gui) + self.origo_coord_y_on_gui
        gui_x = (x * self.x_stepsize_on_gui) + self.origo_coord_x_on_gui
        return gui_x, gui_y

    def gui_coord_to_system_coord(self, x, y):
        sys_y = -(y - self.origo_coord_y_on_gui) / self.y_stepsize_on_gui
        sys_x = (x - self.origo_coord_x_on_gui) / self.x_stepsize_on_gui
        return sys_x, sys_y

    # create visual representation of the coordinate system
    def draw(self, color='red', line_width=1.4):
        # load the borders of the GUI with this system's coordinates
        left_border, right_border, upper_border, lower_border = self.get_gui_edge_with_system_coords()
        # y = 0
        self.x_coefficient_axis = self.canvas.create_line(self.system_coord_to_gui_coord(left_border, 0),
                                              self.system_coord_to_gui_coord(right_border, 0),
                                              fill=color, width=line_width)
        # x = 0
        self.y_coefficient_axis = self.canvas.create_line(self.system_coord_to_gui_coord(0, upper_border),
                                              self.system_coord_to_gui_coord(0, lower_border),
                                              fill=color, width=line_width)

    def complete_redraw(self):
        # delete everything
        for element in self.elements:
            element.undraw()
        self.canvas.delete(self.x_coefficient_axis)
        self.canvas.delete(self.y_coefficient_axis)
        # redraw everything
        self.draw()
        for element in self.elements:
            element.draw()

    # add a new element to the coordinate system
    def add_element(self, element):
        element.add_coordinate_system_reference(self)
        self.elements.append(element)
        element.draw()

    # get any elements crossing a specific point
    def get_element_at_point(self, x, y, precise=True):
        elements_at_point = []
        if not precise:
            precision_treshold = 10 / self.y_stepsize_on_gui
        else:
            precision_treshold = 0
        for element in self.elements:
            if element.type == 'bouncer':
                continue
            else:
                dist = point_element_distance(x, y, element)
                if dist <= precision_treshold:
                    elements_at_point.append(element)
        return elements_at_point

    # calculate intersections between a given line and all other elements in the coordinate system
    def line_with_anything_intersections(self, x, y, c):
        intersections = []
        for element in self.elements:
            if element.type == 'line':
                intersect_x, intersect_y = two_lines_intersection(
                    x, y, c, element.x_coefficient, element.y_coefficient, element.c)
                if intersect_x is not None and intersect_y is not None:
                    intersections.append([intersect_x, intersect_y, element])
            elif element.type == 'circle':
                current_circle_intersections = line_circle_intersection(
                    x, y, c, element.origo_x, element.origo_y, element.radius)
                for i in current_circle_intersections:
                    if i[0] is not None and i[1] is not None:
                        intersections.append([i[0], i[1], element])
            elif element.type == 'ordered_polynomial':
                current_polynomial_intersections = line_ordered_polynomial_intersection(x, y, c, element.exponents.copy(), element.coefficients.copy())
                if current_polynomial_intersections is not None:
                    for i in current_polynomial_intersections:
                        intersections.append([i[0], i[1], element])

        return intersections

    # functions for mouse actions on GUI
    def mouse_motion(self, event):
        x, y = self.gui_coord_to_system_coord(event.x, event.y)
        element_under_cursor = self.get_element_at_point(x, y, precise=False)
        if element_under_cursor is not None:
            for element in element_under_cursor:
                element.line_width = HIGHLIGHT_WIDTH
                element.undraw()
                element.draw()
            # if an element is no longer under the mouse
            if self.element_under_cursor is not None:
                for element in self.element_under_cursor:
                    if element not in element_under_cursor:
                        element.line_width = 1
                        element.undraw()
                        element.draw()
        if element_under_cursor != self.element_under_cursor:
            self.element_under_cursor = element_under_cursor
            self.canvas.update()

    def mouse_left_button_clicked(self, e):
        self.last_mouse_x = None
        self.last_mouse_y = None

    def mouse_drag(self, e):
        if self.last_mouse_x is not None and self.last_mouse_y is not None:
            self.origo_coord_x_on_gui += e.x - self.last_mouse_x
            self.origo_coord_y_on_gui += e.y - self.last_mouse_y
        self.last_mouse_x = e.x
        self.last_mouse_y = e.y

        self.complete_redraw()

    def mouse_scroll(self, e):
        if e.delta > 0:
            self.zoom(ZOOM_STEPSIZE, e)
        elif e.delta < 0:
            self.zoom(1 / ZOOM_STEPSIZE, e)

    def zoom(self, ratio, event):
        mouse_gui_x, mouse_gui_y = event.x, event.y
        before_x, before_y = self.gui_coord_to_system_coord(mouse_gui_x, mouse_gui_y)
        self.x_stepsize_on_gui *= ratio
        self.y_stepsize_on_gui *= ratio
        after_x, after_y = self.gui_coord_to_system_coord(mouse_gui_x, mouse_gui_y)
        # account for shifting by changing the position of the coordinate system's origo
        self.origo_coord_x_on_gui += (after_x - before_x) * self.x_stepsize_on_gui
        self.origo_coord_y_on_gui += (before_y - after_y) * self.y_stepsize_on_gui

        self.complete_redraw()


class Line:
    # equation of the line: x_coeff * x + y_coeff * y = c
    def __init__(self, x=1, y=1, c=0):
        self.visualization = None
        self.type = 'line'
        # x_coeff * x + y_coeff * y = c
        self.x_coefficient = x
        self.y_coefficient = y
        self.c = c

        # gui variables
        self.line_width = 1

        # variable for the physics.py extension
        self.physics_type = 'static'

    def add_coordinate_system_reference(self, coordinate_system):
        self.cs = coordinate_system

    def evaluate_at_x(self, x):
        if self.y_coefficient == 0:
            return None
        return (self.c - x*self.x_coefficient) / self.y_coefficient

    def x_at_y(self, y):
        if self.x_coefficient == 0:
            return None
        return (self.c - y*self.y_coefficient) / self.x_coefficient

    # return normalvectior
    def get_perpendicular_vector_at_point(self, x, y):
        return [self.x_coefficient, self.y_coefficient]

    def get_direction(self):
        return get_vector_direction(-self.y_coefficient, self.x_coefficient)

    # drawing from left to right GUI border.
    # if the line is vertical, drawing from upper to lower border.
    def draw(self, color="lime", width=None):
        if width is None:
            width = self.line_width
        left_border, right_border, upper_border, lower_border = self.cs.get_gui_edge_with_system_coords()
        if self.y_coefficient == 0:
            self.visualization = self.cs.canvas.create_line(self.cs.system_coord_to_gui_coord(self.c / self.x_coefficient, upper_border),
                                                            self.cs.system_coord_to_gui_coord(self.c / self.x_coefficient, lower_border),
                                                            fill=color, width=width)
        else:
            self.visualization = self.cs.canvas.create_line(self.cs.system_coord_to_gui_coord(left_border, self.evaluate_at_x(left_border)),
                                                            self.cs.system_coord_to_gui_coord(right_border, self.evaluate_at_x(right_border)),
                                                            fill=color, width=width)

    def undraw(self):
        self.cs.canvas.delete(self.visualization)


class Circle:
    # equation of the circle: (x - origo_x) ** 2 + (y - origo_y) ** 2 = radius ** 2
    def __init__(self, origo_x=0, origo_y=0, radius=1):
        self.visualization = None
        self.type = 'circle'

        self.origo_x = origo_x
        self.origo_y = origo_y
        self.radius = radius

        # gui variables
        self.line_width = 1

        # variable for the physics.py extension
        self.physics_type = 'static'

    def add_coordinate_system_reference(self, cs):
        self.cs = cs

    def evaluate_at_x(self, x):
        if (x - self.origo_x) ** 2 - self.radius ** 2 > 0:
            y_positive_sqrt = ((x - self.origo_x) ** 2 - self.radius ** 2) ** 0.5 + self.origo_y
            y_negative_sqrt = -((x - self.origo_x) ** 2 - self.radius ** 2) ** 0.5 + self.origo_y
            return [y_positive_sqrt, y_negative_sqrt]
        else:
            return None

    def get_perpendicular_vector_at_point(self, x, y):
        return [x - self.origo_x, y - self.origo_y]

    def draw(self, color='yellow', width=None):
        if width is None:
            width = self.line_width
        self.visualization = self.cs.canvas.create_oval(
            self.cs.system_coord_to_gui_coord(self.origo_x - self.radius, self.origo_y + self.radius),
            self.cs.system_coord_to_gui_coord(self.origo_x + self.radius, self.origo_y - self.radius),
            outline=color, width=width)

    def undraw(self):
        self.cs.canvas.delete(self.visualization)


class OrderedPolynomial:
    def __init__(self, exponents=None, coefficients=None):
        self.visualization = None
        self.type = 'ordered_polynomial'

        # set exponents and coefficients (y = coeff[0] * x ** exp[0] + coeff[1] * x ** exp[1] + ...)
        if exponents == None:
            self.exponents = [1]
        else:
            self.exponents = exponents
        if coefficients == None:
            self.coefficients = [1]
        else:
            self.coefficients = coefficients
        # repair incorrect input
        if len(self.exponents) > len(self.coefficients):
            self.coefficients.append([0] * (len(self.exponents) - len(self.coefficients)))
        elif len(self.exponents) < len(self.coefficients):
            self.exponents.append([0] * (len(self.coefficients) - len(self.exponents)))
        # calculate derivative values
        self.derivative_exponents = exponents.copy()
        self.derivative_coefficients = coefficients.copy()

        for i in range(len(self.derivative_coefficients)):
            self.derivative_coefficients[i] *= self.derivative_exponents[i]
            self.derivative_exponents[i] -= 1

        # gui variables
        self.line_width = 1

        # variable for the physics.py extension
        self.physics_type = 'static'

    def add_coordinate_system_reference(self, cs):
        self.cs = cs

    def get_perpendicular_vector_at_point(self, x, y):
        slope = self.evaluate_at_x(x, derivative_evaluation=True)

        return [-slope, 1]

    def evaluate_at_x(self, x, derivative_evaluation=False):
        if derivative_evaluation:
            c = self.derivative_coefficients
            e = self.derivative_exponents
        else:
            c = self.coefficients
            e = self.exponents
        y = 0
        for i in range(len(c)):
            if x == 0 and e[i] < 0:
                return None
            else:
                y += x ** e[i] * c[i]
        return y

    def draw(self, color='orange', width=None):
        if width is None:
            width = self.line_width
        self.visualization = []
        left_border, right_border, upper_border, lower_border = self.cs.get_gui_edge_with_system_coords()
        first = True
        x = left_border
        increment = 1 / (self.cs.x_stepsize_on_gui)
        old_x, old_y = None, None
        while x < right_border:
            new_y = self.evaluate_at_x(x)
            if not first and new_y is not None:
                self.visualization.append(self.cs.canvas.create_line
                                          (self.cs.system_coord_to_gui_coord(old_x, old_y),
                                           self.cs.system_coord_to_gui_coord(x, new_y),
                                           fill=color, width=width))
            else:
                first = False
            old_x, old_y = x, new_y
            x += increment

    def undraw(self):
        for visual in self.visualization:
            self.cs.canvas.delete(visual)
        self.visualization = []


def setup():
    # set window for visualizing stuff
    visualizer_site = tk.Tk()
    visualizer_site.title('Analytic geometry')
    canvas = tk.Canvas(visualizer_site, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background='black')
    canvas.pack()
    # create internal coordsystem (different from gui coords)
    coord_system = CoordinateSystem(canvas)
    # set mouse actions for the visualizer window
    canvas.bind("<Button-1>", coord_system.mouse_left_button_clicked)
    canvas.bind("<B1-Motion>", coord_system.mouse_drag)
    canvas.bind('<Motion>', coord_system.mouse_motion)
    canvas.bind("<MouseWheel>", coord_system.mouse_scroll)


    return coord_system, visualizer_site


if __name__ == '__main__':
    coord_system, window = setup()
    l = Line()
    coord_system.add_element(l)
    c = Circle()
    coord_system.add_element(c)

    window.mainloop()