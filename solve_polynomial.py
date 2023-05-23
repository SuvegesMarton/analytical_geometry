# this script is to solve an equation of this form: a*x**i + b*x**j + ... + c*x**k = 0
from random import randint


def main(exponents, coefficients, degree_of_accuracy=1000):
    solutions = []
    # remove monoms with a coefficient of 0
    i = 0
    while i < len(coefficients):
        if coefficients[i] == 0:
            coefficients.pop(i)
            exponents.pop(i)
            i -= 2
        i += 1

    # check if x = 0 is a solution. This way dividing and multiplying with x will be possible later.
    if evaluate(exponents, coefficients, 0) == 0:
        solutions.append(0)

    # check simple solutions: if there is only one x-something equaling 0, only x=0 will satisfy the equation
    if len(exponents) == 1:
        if exponents[0] != 0:
            return [0]
        else:
            print('Derived to a state with no solution')
            return None
    # these linear functions have only one solution.
    elif exponents == [0, 1]:
        return [-coefficients[0] / coefficients[1]]
    elif exponents == [1, 0]:
        return [-coefficients[1] / coefficients[0]]
    # more complex polynomials
    else:
        # normalize the polynomial, so all coefficients are 0 or positive, and the smallest is 0.
        smallest_exponent = min(exponents)
        for i in range(len(exponents)):
            exponents[i] -= smallest_exponent
        # check again for linear functions (which have 1 solution).
        if exponents == [0, 1]:
            solutions += [-coefficients[0] / coefficients[1]]
            solutions.sort()
            return solutions
        elif exponents == [1, 0]:
            solutions += [-coefficients[1] / coefficients[0]]
            solutions.sort()
            return solutions
        # get the derivative of the normalized polynomial
        derivative_exponents, derivative_coefficients = calculate_derivative(exponents, coefficients)
        # where the derivative is 0, the function has a local minimum or a maximum place.
        local_min_max_points = [-10e10] + main(derivative_exponents, derivative_coefficients) + [10e10]
        # a polynomial with only positive exponents will be strictly monotonic between a local minimum and it's
        # neighbouring local maximum (or max and min). This means in such a section it crosses the x axis 0 or 1 time.
        # if one of these min/max points are positive (in value) and the other is negative, there is a crossing.
        for i in range(len(local_min_max_points) - 1):
            # after setting the borders at the local extremes, narrow the gap by halving it. Perform degree_of_accuracy
            # iterations to get the final result.
            left_border = local_min_max_points[i]

            right_border = local_min_max_points[i + 1]
            # if both border's y values are on the same side of the x axis, there is no solution in between(skip cycle)
            if positivity(evaluate(exponents, coefficients, left_border)) == positivity(evaluate(exponents, coefficients, right_border)):
                continue
            elif evaluate(exponents, coefficients, left_border) == 0:
                if left_border not in solutions:
                    solutions.append(left_border)
                continue
            elif evaluate(exponents, coefficients, right_border) == 0:
                if right_border not in solutions:
                    solutions.append(right_border)
                continue

            for j in range(degree_of_accuracy):
                # geometric mean
                new_border = (left_border + right_border) / 2

                left_border_value = evaluate(exponents, coefficients, left_border)
                right_border_value = evaluate(exponents, coefficients, right_border)
                new_border_value = evaluate(exponents, coefficients, new_border)
                if left_border_value == right_border_value:
                    break
                if positivity(left_border_value) == positivity(new_border_value):
                    left_border = new_border
                elif positivity(right_border_value) == positivity(new_border_value):
                    right_border = new_border
                else:
                    break
            new_solution = round((left_border + right_border) / 2, 8)
            if new_solution not in solutions:
                solutions.append(new_solution)
        solutions.sort()
        return solutions


def calculate_derivative(exponents, coefficients):
    derivative_exponents = []
    derivative_coefficients = []

    for i in range(len(coefficients)):
        if exponents[i] == 0:
            continue
        else:
            derivative_exponents.append(exponents[i] - 1)
            derivative_coefficients.append(coefficients[i] * exponents[i])
    return derivative_exponents, derivative_coefficients


def positivity(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def evaluate(exponents, coefficients, x):
    y = 0
    for i in range(len(coefficients)):
        if x == 0 and exponents[i] < 0:
            return None
        else:
            y += (x ** exponents[i]) * coefficients[i]
    return y


def create_polynomial_set(n=5, coefficients_in_the_brackets=None):
    if coefficients_in_the_brackets is None:
        coefficients_in_the_brackets = [randint(-20, 20) for _ in range(n)]
    else:
        n = len(coefficients_in_the_brackets)
    exponents = [i for i in range(n + 1)]
    coefficients = [0 for _ in range(n + 1)]
    # get the number of ways to multiply the contents of the brackets with each other
    ways = 2 ** n

    # each number from 0 to 'ways' represents a single way to multiply stuff together (convert to base 2, 0=multiply
    # coefficient, 1 = multiply x).
    for i in range(ways):
        coeff = 1
        exp = 0
        counter = 0
        for j in range(n - 1, -1, -1):
            if counter + 2**j <= i:
                counter += 2**j
                exp += 1
            else:
                coeff *= coefficients_in_the_brackets[j]
        coefficients[exp] += coeff

    # transform coefficients_in_the_brackets to expected solutions:
    expected_solutions = []
    for element in coefficients_in_the_brackets:
        if -element not in expected_solutions:
            expected_solutions.append(-element)

    return exponents, coefficients, expected_solutions


def print_polynomial_neatly(exponents, coefficients):
    sum_string = ''
    for i in range(len(exponents)):
        if i != 0:
            sum_string += ' + '
        sum_string += str(str(coefficients[i]) + '*x^' + str(exponents[i]))
    sum_string += ' = 0'
    print(sum_string)


if __name__ == '__main__':
    # [0, 1, 2, 3, 4, 5] [28672, -10240, 640, 160, -25, 1] [-7, 8]
    exp, coeff, sol = create_polynomial_set(coefficients_in_the_brackets=[5, 10, 15])

    print('exp =', exp)
    print('coeff =', coeff)

    print_polynomial_neatly(exp, coeff)
    print('expected s:', sol)
    print('solutions:', main(exp, coeff))
