from physics import *


# functions for adding more complex elements
def springy_block(coord_system, x, y, start_x=0, start_y=0, radius=1, spacing=4, spring_force=3000, coloring_limit=1000):
    balls = [[Ball(start_x + i*spacing, start_y + j*spacing, radius=radius) for i in range(x)] for j in range(y)]

    for j in range(len(balls)):
        for i in range(len(balls[j])):
            coord_system.add_element(balls[j][i])

            if i < x-1:
                coord_system.add_element(Spring(balls[j][i], balls[j][i+1], standard_length=spacing,
                                                spring_force=spring_force, coloring_limit=coloring_limit))
            if j < y-1:
                coord_system.add_element(Spring(balls[j][i], balls[j+1][i], standard_length=spacing,
                                                spring_force=spring_force, coloring_limit=coloring_limit))
            if i < x-1 and j < y-1:
                coord_system.add_element(Spring(balls[j][i], balls[j+1][i+1], standard_length=(2**0.5)*spacing,
                                                spring_force=spring_force, coloring_limit=coloring_limit))
            if i > 0 and j < y-1:
                coord_system.add_element(Spring(balls[j][i], balls[j+1][i-1], standard_length=(2**0.5)*spacing,
                                                spring_force=spring_force, coloring_limit=coloring_limit))


# functions for full simulation environments
def springy_block_demo():
    coord_system, window = setup()

    # first add static elements
    coord_system.add_element(Line(x=0, y=1, c=-30))
    coord_system.add_element(Line(x=1, y=0, c=50))
    coord_system.add_element(Circle(0, -30, 10))

    springy_block(coord_system, 6, 4, spring_force=10000)
    p = PhysicsEngine(coord_system, window)
    p.simulate()

    window.mainloop()



if __name__ == '__main__':
    springy_block_demo()
