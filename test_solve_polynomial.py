from solve_polynomial import main, create_polynomial_set
from random import randint


def test_main():
    for i in range(100):
        exp, coeff, sol = create_polynomial_set(n=randint(1, 10))
        sol2 = main(exp, coeff)
        sol.sort()
        sol2.sort()
        assert sol == sol2


test_main()