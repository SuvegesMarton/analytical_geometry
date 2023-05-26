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

        self.add_external_acceleration(0, -9.81)

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
        self.update(1000*average_seconds_between_frames)
        self.window.after(1, self.simulate)
        if frame_count % 200 == 0:
            print(1 / average_seconds_between_frames)
        last_time = now

    def update(self, time_passed):
        all_elements = self.cs.elements
        # recalculate all velocities from acceleration and applied forces.
        for body in all_elements:
            if body.active_physics is True:
                # add constant acceleration to all velocities
                body.velocity_x += self.system_acceleration[0] * time_passed / 1000
                body.velocity_y += self.system_acceleration[1] * time_passed / 1000
                # add acceleration by forces (implied by other bodies) on the body
                for element in all_elements:
                    if element.active_physics is True:
                        if element.type == 'ball':
                            # calculate distance
                            distance = ((body.origo_x - element.origo_x)**2 + (body.origo_y - element.origo_y)**2)**0.5
                            if distance < body.radius + element.radius:
                                pass
                # set new 'preidcted' coordinates for the bodies
                body.new_x = body.origo_x + body.velocity_x * time_passed / 1000
                body.new_y = body.origo_y + body.velocity_y * time_passed / 1000

        # add the calculated acceleration to the body's velocity, check for bounces on static objects,
        # and move accordingly
        for body in all_elements:
            if body.active_physics is True:
                # check for collision with static elements
                for element in all_elements:
                    # element is static
                    if element.active_physics is False:
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
                            # calculate the original combined speed
                            full_speed = (body.velocity_x**2 + body.velocity_y**2) ** 0.5
                            # reduce full speed according to the bounciness of the object
                            full_speed *= body.bounciness
                            # new_dir_x * c, new_dir_x * c -> new velocities
                            # (new_dir_x * c) ** 2 +  (new_dir_x * c) ** 2 = full_speed ** 2
                            c = (full_speed ** 2 / (new_dir_x ** 2 + new_dir_y ** 2)) ** 0.5
                            # assign new speed to the object
                            body.velocity_x, body.velocity_y = new_dir_x * c, new_dir_y * c
                            full_speed = (body.velocity_x**2 + body.velocity_y**2) ** 0.5
                            # move object back, so there will be no contact
                            body.new_x, body.new_y = body.origo_x, body.origo_y
                body.update_location()
        # check the system for collisions


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
        self.bounciness = 1

    def update_location(self):
        self.origo_x = self.new_x
        self.origo_y = self.new_y
        self.undraw()
        self.draw()

if __name__ == '__main__':
    coord_system, window = setup()

    # first add static elements
    coord_system.add_element(Line(x=1, y=1, c=0))
    coord_system.add_element(Line(x=1, y=-1, c=20))

    #coord_system.add_element(Circle(10, 0, 30))

    # then add moving elements
    frame_count = 0
    for i in range(5, 100):
        coord_system.add_element(Ball(0, i, radius=1))

    p = PhysicsEngine(coord_system, window)
    p.simulate()


    window.mainloop()

