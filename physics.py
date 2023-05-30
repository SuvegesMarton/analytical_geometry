from visualizer import *
from matrix_calculations import dot_product, vector_to_unit_vector
import time

DESIRED_FPS = 50
MOVING_AVERAGE_LENGTH = 5


class PhysicsEngine:
    def __init__(self, coordinate_system, window):
        self.cs = coordinate_system
        self.window = window
        # net acceleration experienced by the inertia system
        self.system_acceleration = [0, 0]

        self.add_external_acceleration(0, -9.81)  # add gravity

        self.moving_physics_elements = []  # moving objects
        self.special_elements = []   # springs, maybe later others
        self.static_elements = []  # lines, non-moving circles, polynomials
        for element in self.cs.elements:
            if element.physics_type == 'moving':
                self.moving_physics_elements.append(element)
            elif element.physics_type == 'special':
                self.special_elements.append(element)
            else:
                self.static_elements.append(element)

        self.frame_count = 0
        self.last_time = time.time()
        self.time_differences = []

    # add acceleration to the inertia system (gravity)
    def add_external_acceleration(self, vector_x, vector_y):
        self.system_acceleration[0] += vector_x
        self.system_acceleration[1] += vector_y

    def simulate(self):
        self.frame_count += 1
        now = time.time()
        time_differences = self.time_differences[-MOVING_AVERAGE_LENGTH:] + [now - self.last_time]
        average_seconds_between_frames = sum(time_differences)/len(time_differences)
        if self.frame_count % 200 == 0:
            print('fps:', int(1 / average_seconds_between_frames))
        for element in self.moving_physics_elements + self.special_elements:
            element.undraw()
            element.draw()

        self.update(1000*average_seconds_between_frames)
        self.window.after(1, self.simulate)
        self.last_time = now

    def update(self, time_passed):
        # calculate forces applied by special elements, and add acceleration(F=ma).
        for element in self.special_elements:
            if element.type == 'spring':
                force1, force2 = element.get_force_applied()
                element.attached_object_1.velocity_x += force1[0] / element.attached_object_1.mass * time_passed / 1000
                element.attached_object_1.velocity_y += force1[1] / element.attached_object_1.mass * time_passed / 1000
                element.attached_object_2.velocity_x += force2[0] / element.attached_object_2.mass * time_passed / 1000
                element.attached_object_2.velocity_y += force2[1] / element.attached_object_2.mass * time_passed / 1000


        # add constant acceleration.
        for body in self.moving_physics_elements:
            # add constant acceleration to all velocities
            body.velocity_x += self.system_acceleration[0] * time_passed / 1000
            body.velocity_y += self.system_acceleration[1] * time_passed / 1000


            # set new 'predicted' coordinates for the bodies
            body.new_x = body.origo_x + body.velocity_x * time_passed / 1000
            body.new_y = body.origo_y + body.velocity_y * time_passed / 1000

        # check for bounces on active objects.
        for body in self.moving_physics_elements:
            if body.collide is False:
                continue
            for element in self.moving_physics_elements:
                if body == element or element.collide is False:
                    continue
                if element.type == 'ball':
                    # calculate distance
                    distance = ((body.new_x - element.new_x)**2 + (body.new_y - element.new_y)**2)**0.5
                    if distance < body.radius + element.radius:
                        # all calculations here done according to https://www.youtube.com/watch?v=1L2g4ZqmFLQ (25:00)
                        # calculate the relative speed of the body (compared to the element)
                        relative_speed_x = body.velocity_x - element.velocity_x
                        relative_speed_y = body.velocity_y - element.velocity_y
                        # calculate the vector between the to ball's centers
                        normal_vector = vector_to_unit_vector([body.new_x - element.new_x, body.new_y - element.new_y])
                        # calculate the speed at which the to objects are approaching each other
                        dot_product_value = dot_product([relative_speed_x, relative_speed_y], normal_vector)

                        impulse = -(1 + body.elasticity*element.elasticity)*dot_product_value/\
                                   (1/body.mass + 1/element.mass)
                        body.velocity_x += normal_vector[0] * impulse / body.mass
                        body.velocity_y += normal_vector[1] * impulse / body.mass
                        body.new_x, body.new_y = body.origo_x, body.origo_y

                        element.velocity_x -= normal_vector[0] * impulse / element.mass
                        element.velocity_y -= normal_vector[1] * impulse / element.mass
                        element.new_x, element.new_y = element.origo_x, element.origo_y

        # check for bounces on static objects, and move.
        for body in self.moving_physics_elements:
            # check for collision with static elements
            for element in self.static_elements:
                distance = point_element_distance(body.new_x, body.new_y, element)
                # collision happens
                if distance <= body.radius:
                    # get the vector perpendicular to the surface to calculate bounce direction
                    perp_vector = element.get_perpendicular_vector_at_point(body.origo_x, body.origo_y)
                    # get the new direction vector of movement
                    new_dir_x, new_dir_y, dir_radian = get_bounce_direction_vector_from_vectors(perp_vector[0],
                                                                                                perp_vector[1],
                                                                                                body.velocity_x,
                                                                                                body.velocity_y)

                    # calculate the original combined speed and reduce it according to the elasticity of the object
                    full_speed = (body.velocity_x**2 + body.velocity_y**2) ** 0.5
                    # new_dir_x * c, new_dir_y * c -> new velocities
                    # (new_dir_x * c) ** 2 +  (new_dir_y * c) ** 2 = full_speed ** 2
                    c = (full_speed ** 2 / (new_dir_x ** 2 + new_dir_y ** 2)) ** 0.5
                    # assign new speed to the object
                    body.velocity_x, body.velocity_y = new_dir_x * c * body.elasticity, new_dir_y * c * body.elasticity
                    # move object back, so there will be no contact
                    body.new_x, body.new_y = body.origo_x, body.origo_y
            # for all bodies after finishing applying forces, checking for collision on active and static elements:
            body.origo_x, body.origo_y = body.new_x, body.new_y


class Ball(Circle):
    # equation of the circle: (x - origo_x) ** 2 + (y - origo_y) ** 2 = radius ** 2
    def __init__(self, start_x, start_y, radius=1, start_velocity=None, collide=True):
        Circle.__init__(self, origo_x=start_x, origo_y=start_y, radius=radius)
        self.type = 'ball'
        if start_velocity is None:
            self.velocity_x, self.velocity_y = 0, 0
        else:
            self.velocity_x, self.velocity_y = start_velocity[0], start_velocity[1]

        self.new_x, self.new_y = None, None

        # objects effected by physics will always collide with static elements. Two such 'active' objects will collide,
        # if both of them are set collide=True
        self.physics_type = 'moving'
        self.collide = collide

        # constants effecting physical behaviour
        self.elasticity = 1
        self.mass = 10


class Spring:
    def __init__(self, attached_object_1, attached_object_2, standard_length=10, spring_force=5):
        self.attached_object_1 = attached_object_1
        self.attached_object_2 = attached_object_2
        self.standard_length = standard_length
        self.spring_force = spring_force  #Newtons per units stretched/squeezed

        self.type = 'spring'
        self.physics_type = 'special'

        self.visualization = None
        self.line_width = 1

    def get_endpoints(self):
        x_1, y_1 = None, None
        if self.attached_object_1.type == 'ball' or self.attached_object_1.type == 'circle':
            x_1, y_1 = self.attached_object_1.origo_x, self.attached_object_1.origo_y
        x_2, y_2 = None, None
        if self.attached_object_2.type == 'ball' or self.attached_object_2.type == 'circle':
            x_2, y_2 = self.attached_object_2.origo_x, self.attached_object_2.origo_y
        return x_1, y_1, x_2, y_2

    def get_force_magnitude(self):
        x_1, y_1, x_2, y_2 = self.get_endpoints()
        current_length = ((x_1 - x_2)**2 + (y_1 - y_2)**2) ** 0.5
        total_force = (self.standard_length - current_length) * self.spring_force
        return total_force

    def get_force_applied(self):
        x_1, y_1, x_2, y_2 = self.get_endpoints()
        force_magnitude = self.get_force_magnitude()
        force_direction = vector_to_unit_vector([x_1 - x_2, y_1 - y_2])
        force_1 = [force_direction[0] * force_magnitude, force_direction[1] * force_magnitude]
        force_2 = [-force_direction[0] * force_magnitude, -force_direction[1] * force_magnitude]
        return force_1, force_2

    def add_coordinate_system_reference(self, cs):
        self.cs = cs

    def draw(self):
        x_1, y_1, x_2, y_2 = self.get_endpoints()

        self.visualization = self.cs.canvas.create_line(
                self.cs.system_coord_to_gui_coord(x_1, y_1),
                self.cs.system_coord_to_gui_coord(x_2, y_2),
                fill='lime', width=self.line_width)

    def undraw(self):
        self.cs.canvas.delete(self.visualization)


if __name__ == '__main__':
    coord_system, window = setup()

    # first add static elements
    coord_system.add_element(Line(x=0, y=1, c=-30))
    coord_system.add_element(Line(x=1, y=0, c=-30))
    coord_system.add_element(Line(x=1, y=0, c=30))

    # then add moving and special elements
    b1 = Ball(10, 10)
    b2 = Ball(-10, 5)
    spr = Spring(b1, b2)
    coord_system.add_element(b1)
    coord_system.add_element(b2)
    coord_system.add_element(spr)

    p = PhysicsEngine(coord_system, window)
    p.simulate()


    window.mainloop()

