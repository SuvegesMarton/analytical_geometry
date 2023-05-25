from visualizer import *
from math import sin, cos, tan


class Bouncer:
    # starting coords and starting directions
    def __init__(self, x, y, direction):
        self.last_x = x
        self.last_y = y
        self.intersections = [[x, y, None]]
        self.already_calculated_intersections = False
        self.start_direction = direction
        self.last_direction = direction
        self.type = 'bouncer'
        self.visualization = []

    def add_coordinate_system_reference(self, cs):
        self.cs = cs

    def evaluate_at_x(self, x):
        x_distance = x - self.last_x
        y_distance = x_distance * tan(self.last_direction)
        return self.last_y + y_distance

    def calculate_next_intersection(self):
        # vector parallel to the bouncer line:
        vector_x = round(cos(self.last_direction), 10)
        vector_y = round(sin(self.last_direction), 10)
        # equation of the line
        equation_x_coefficient = -vector_y
        equation_y_coefficient = vector_x
        equation_c = equation_x_coefficient * self.last_x + equation_y_coefficient * self.last_y
        # calculate all intersections with other elements
        intersections = self.cs.line_with_anything_intersections(equation_x_coefficient, equation_y_coefficient, equation_c)


        # find the distances of the intersections
        smallest_distance = 10e10
        closest_intersection = None

        # choose the relevant intersection
        for i in range(len(intersections)):
            # if the intersection is the current location of the bouncer, ignore the intersection
            # check if it is the same intersection by accurate coordinates. This can fail at extremely large numbers.
            if round(intersections[i][0], 5) == round(self.last_x, 5) and round(intersections[i][1], 5) == round(self.last_y, 5):
                continue
            #  check if it is the same intersection by the ratio of the coordinates.
            #  Even large numbers will be ruled out, if needed. Zeros have to be filtered for division!
            elif self.last_x != 0 and self.last_y != 0:
                ratio_limit = 0.0001
                if 0 <= abs(1 - intersections[i][0] / self.last_x) <= ratio_limit and\
                        0 <= abs(1 - intersections[i][1] / self.last_y) <= ratio_limit:
                    continue


            if vector_x == 0:
                if (intersections[i][1] - self.last_y) / abs(intersections[i][1] - self.last_y) == vector_y / abs(vector_y):
                    distance = sqrt((intersections[i][0] - self.last_x) ** 2 + (intersections[i][1] - self.last_y) ** 2)
                    if distance < smallest_distance:
                        smallest_distance = distance
                        closest_intersection = intersections[i]

            elif vector_y == 0:
                if (intersections[i][0] - self.last_x) / abs(intersections[i][0] - self.last_x) == vector_x / abs(vector_x):
                    distance = sqrt((intersections[i][0] - self.last_x) ** 2 + (intersections[i][1] - self.last_y) ** 2)
                    if distance < smallest_distance:
                        smallest_distance = distance
                        closest_intersection = intersections[i]

            else:
                if (intersections[i][0] - self.last_x) / abs(intersections[i][0] - self.last_x) == vector_x / abs(vector_x):
                    if (intersections[i][1] - self.last_y) / abs(intersections[i][1] - self.last_y) == vector_y / abs(vector_y):
                        distance = sqrt((intersections[i][0] - self.last_x) ** 2 + (intersections[i][1] - self.last_y) ** 2)
                        if distance < smallest_distance:
                            smallest_distance = distance
                            closest_intersection = intersections[i]

        # if there is no intersection, mark a point along the bouncer line as final intersection. Drawing function will
        # complete this to the borders of the GUI.
        if closest_intersection is None:
            new_direction = None
            closest_intersection = [self.last_x + vector_x, self.last_y + vector_y, None]


        else:
            # get a vector perpendicular to the line segment hit by the bouncer
            perp_vector = closest_intersection[2].get_perpendicular_vector_at_point(closest_intersection[0], closest_intersection[1])
            # get the angle between the perpendicular vector and the bouncer's direction
            perp_vector_relative_angle = get_vector_direction(*perp_vector) - self.last_direction
            collision_angle = get_angle_between_vectors(perp_vector, [vector_x, vector_y])
            # get the angle between perpendicular vector and bouncer between 0 and 90 degrees, by eliminating angles
            # calculated on the -1*perp_vector 's data
            if collision_angle > pi / 2:
                collision_angle = pi - collision_angle

            if perp_vector_relative_angle % pi >= pi / 2:
                new_direction = self.last_direction + 2 * (pi/2 - collision_angle)
            else:
                new_direction = self.last_direction - 2 * (pi / 2 - collision_angle)

        # set new values for the bouncer
        self.last_x = closest_intersection[0]
        self.last_y = closest_intersection[1]
        self.last_direction = new_direction


        self.intersections.append(closest_intersection)

    def calculate_all_intersections(self, limit=20):
        number_of_intersections = 0
        while number_of_intersections < limit:
            self.calculate_next_intersection()
            if self.last_direction is None:
                break
            number_of_intersections += 1
        self.already_calculated_intersections = True

    def draw(self, color='cyan', width=1, recalculate=False):
        if not self.already_calculated_intersections or recalculate:
            self.calculate_all_intersections()
        for i in range(len(self.intersections) - 1):
            new_segment = self.cs.canvas.create_line(self.cs.system_coord_to_gui_coord(self.intersections[i][0], self.intersections[i][1]),
                                                     self.cs.system_coord_to_gui_coord(self.intersections[i + 1][0], self.intersections[i + 1][1]),
                                                            fill=color, width=width)
            self.visualization.append(new_segment)

        # if the bouncer goes to infinity without hitting anything, make the line longer according to zoom and dragging
        if self.intersections[-1][2] is None:
            left_border, right_border, upper_border, lower_border = self.cs.get_gui_edge_with_system_coords()

            x_direction = self.intersections[-1][0] - self.intersections[-2][0]
            y_direction = self.intersections[-1][1] - self.intersections[-2][1]

            last_x, last_y = self.intersections[-2][0], self.intersections[-2][1]
            if round(x_direction, 8) == 0:
                if y_direction > 0:
                    new_segment = self.cs.canvas.create_line(
                        self.cs.system_coord_to_gui_coord(last_x, last_y),
                        self.cs.system_coord_to_gui_coord(last_x, upper_border),
                        fill=color, width=width)
                else:
                    new_segment = self.cs.canvas.create_line(
                        self.cs.system_coord_to_gui_coord(last_x, last_y),
                        self.cs.system_coord_to_gui_coord(last_x, lower_border),
                        fill=color, width=width)
            elif round(y_direction, 8) == 0:
                if x_direction > 0:
                    new_segment = self.cs.canvas.create_line(
                        self.cs.system_coord_to_gui_coord(last_x, last_y),
                        self.cs.system_coord_to_gui_coord(right_border, last_y),
                        fill=color, width=width)
                else:
                    new_segment = self.cs.canvas.create_line(
                        self.cs.system_coord_to_gui_coord(last_x, last_y),
                        self.cs.system_coord_to_gui_coord(left_border, last_y),
                        fill=color, width=width)
            else:

                # draw to the nearest vertical border
                if x_direction > 0:
                    x_distance = right_border - last_x
                    y_distance = (x_distance / x_direction) * y_direction
                    new_segment = self.cs.canvas.create_line(
                        self.cs.system_coord_to_gui_coord(last_x, last_y),
                        self.cs.system_coord_to_gui_coord(right_border, last_y + y_distance),
                        fill=color, width=width)
                else:
                    x_distance = left_border - last_x
                    y_distance = (x_distance / x_direction) * y_direction
                    new_segment = self.cs.canvas.create_line(
                        self.cs.system_coord_to_gui_coord(last_x, last_y),
                        self.cs.system_coord_to_gui_coord(left_border, last_y + y_distance),
                        fill=color, width=width)
        else:
            new_segment = self.cs.canvas.create_line(self.cs.system_coord_to_gui_coord(self.intersections[-2][0], self.intersections[-2][1]),
                                                     self.cs.system_coord_to_gui_coord(self.intersections[-1][0], self.intersections[-1][1]),
                                                            fill=color, width=width)
        self.visualization.append(new_segment)

    def undraw(self):
        for element in self.visualization:
            self.cs.canvas.delete(element)
        self.visualization = []
        self.last_direction = self.start_direction


def rotating_bouncers(x, y, start_direction, end_direction, number_of_bouncers_between, show_only_last=False, delay=0):
    unit_of_rotation = (end_direction - start_direction) / number_of_bouncers_between
    for i in range(number_of_bouncers_between + 1):
        new_bouncer = Bouncer(x, y, start_direction+i*unit_of_rotation)
        coord_system.add_element(new_bouncer)



if __name__ == '__main__':
    coord_system, window = setup()


    # first add static elements
    for i in range(10):
        for j in range(5):
            coord_system.add_element(Circle(origo_x=30+j*8, origo_y=-36+i*8,radius=2))

    # then add bouncers

    rotating_bouncers(0, 0, 0.5, 0.51, 300)


    window.mainloop()