from visualizer import *
import time

DESIRED_FPS = 50
MOVING_AVERAGE_LENGTH = 5
last_time = time.time()
time_differences = []


class PhysicsEngine:
    def __init__(self, coordinate_system, window):
        self.cs = coordinate_system
        self.window = window
        # net acceleration experienced by the inertia system
        self.system_acceleration = [0, 0]

        # self.add_external_acceleration(0, -9.81) # add gravity

        self.active_physics_elements = []
        self.static_elements = []
        for element in self.cs.elements:
            if element.active_physics is True:
                self.active_physics_elements.append(element)
            else:
                self.static_elements.append(element)

    # add acceleration to the inertia system (gravity)
    def add_external_acceleration(self, vector_x, vector_y):
        self.system_acceleration[0] += vector_x
        self.system_acceleration[1] += vector_y

    def simulate(self):
        global frame_count, last_time, time_differences
        frame_count += 1
        now = time.time()
        time_differences = time_differences[-MOVING_AVERAGE_LENGTH:] + [now - last_time]
        average_seconds_between_frames = sum(time_differences)/len(time_differences)
        if frame_count % 200 == 0:
            print('fps:', int(1 / average_seconds_between_frames))
        for element in self.active_physics_elements:
            element.undraw()
            element.draw()

        self.update(1000*average_seconds_between_frames)
        self.window.after(1, self.simulate)
        last_time = now

    def update(self, time_passed):
        # recalculate all velocities from acceleration and applied forces.
        for body in self.active_physics_elements:
            # add constant acceleration to all velocities
            body.velocity_x += self.system_acceleration[0] * time_passed / 1000
            body.velocity_y += self.system_acceleration[1] * time_passed / 1000

            # add acceleration by forces, such as spring-forces.

            # set new 'predicted' coordinates for the bodies
            body.new_x = body.origo_x + body.velocity_x * time_passed / 1000
            body.new_y = body.origo_y + body.velocity_y * time_passed / 1000

        # check for bounces on active objects.
        for body in self.active_physics_elements:
            for element in self.active_physics_elements:
                if body == element:
                    continue
                if element.type == 'ball':
                    # calculate distance
                    distance = ((body.new_x - element.new_x)**2 + (body.new_y - element.new_y)**2)**0.5
                    if distance < body.radius + element.radius:
                        # calculate the relative speed of the body (compared to the element)
                        relative_speed_x = body.velocity_x - element.velocity_x
                        relative_speed_y = body.velocity_y - element.velocity_y
                        # calculate the vector between the to ball's centers
                        normal_vector = [body.new_x - element.new_x, body.new_y - element.new_y]
                        # calculate the speed at which the to objects are approaching each other
                        dot_product_value = dot_product([relative_speed_x, relative_speed_y],
                                                                      normal_vector)
                        '''
                        body.velocity_x = 0
                        body.velocity_y = 0
                        element.velocity_x = 0
                        element.velocity_y = 0
                        body.new_x = body.origo_x
                        body.new_y = body.origo_y
                        element.new_x = element.origo_x
                        element.new_y = element.origo_y
                        '''

        # check for bounces on static objects, and move.
        for body in self.active_physics_elements:
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
    def __init__(self, start_x, start_y, collide=False, radius=1):
        Circle.__init__(self, origo_x=start_x, origo_y=start_y, radius=radius)
        self.type = 'ball'
        self.velocity_x, self.velocity_y = 0, 0
        self.new_x, self.new_y = None, None

        # objects effected by physics will always collide with static elements. Two such 'active' objects will collide,
        # if both of them are set collide=True
        self.active_physics = True
        self.collide = collide

        # constants effecting physical behaviour
        self.elasticity = 1.0
        self.mass = 10

    def update_location(self):
        self.origo_x = self.new_x
        self.origo_y = self.new_y


if __name__ == '__main__':
    coord_system, window = setup()
    frame_count = 0

    # first add static elements

    # then add moving elements
    b = Ball(-20, 0.5, radius=1)
    coord_system.add_element(b)
    b.velocity_x = 5

    b = Ball(20, 0, radius=1)
    coord_system.add_element(b)
    b.velocity_x = -5

    p = PhysicsEngine(coord_system, window)
    p.simulate()


    window.mainloop()

