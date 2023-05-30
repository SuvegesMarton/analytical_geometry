from physics import *

def springy_block(x, y):
    coord_system, window = setup()

    # first add static elements
    coord_system.add_element(Line(x=0, y=1, c=-30))
    coord_system.add_element(Line(x=1, y=0, c=50))
    coord_system.add_element(Circle(0, -30, 10))

    # then add moving and special elements
    balls = [[Ball(i*4, j*4) for i in range(x)] for j in range(y)]
    spring_force = 3000
    for j in range(len(balls)):
        for i in range(len(balls[j])):
            coord_system.add_element(balls[j][i])

            if i < x-1:
                coord_system.add_element(Spring(balls[j][i], balls[j][i+1], standard_length=4, spring_force=spring_force))
            if j < y-1:
                coord_system.add_element(Spring(balls[j][i], balls[j+1][i], standard_length=4, spring_force=spring_force))
            if i < x-1 and j < y-1:
                coord_system.add_element(Spring(balls[j][i], balls[j+1][i+1], standard_length=32**0.5, spring_force=spring_force))
            if i > 0 and j < y-1:
                coord_system.add_element(Spring(balls[j][i], balls[j+1][i-1], standard_length=32**0.5, spring_force=spring_force))


    p = PhysicsEngine(coord_system, window)
    p.simulate()

    window.mainloop()

springy_block(6, 4)