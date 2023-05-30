import copy


def calculate_determinant(matrix):
    # filter non-square matrices, since they have no determinant
    if len(matrix) != len(matrix[0]):
        print('Not a square matrix!')
        return False
    # calculate determinant of 2x2 matrices
    if len(matrix) == 1:
        return matrix[0][0]
    if len(matrix) == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    # calculate determinant of matrices bigger than 2x2
    # create sign table for final addition
    fixed_row_index = 2
    sign_table = []
    for i in range(len(matrix[0])):
        if (i + fixed_row_index) % 2 == 0:
            sign_table.append(1)
        else:
            sign_table.append(-1)
    # calculate values to add up
    values = []
    for i in range(len(matrix[0])):
        value_in_fixed_column = matrix[fixed_row_index][i]
        # get (n-1)*(n-1) matrix
        smaller_matrix = copy.deepcopy(matrix)
        del smaller_matrix[fixed_row_index]
        for j in range(len(smaller_matrix)):
            del smaller_matrix[j][i]
        # calculate new value
        det = calculate_determinant(smaller_matrix)
        values.append(value_in_fixed_column * det)
    # apply sign table to values and add up to get the final determinant
    final_determinant = 0
    for i in range(len(sign_table)):
        final_determinant += sign_table[i] * values[i]
    return final_determinant


def calculate_matrix_of_minors(matrix):
    matrix_of_minors = []
    for fixed_row_index in range(len(matrix)):
        # calculate values to add up
        values = []
        for i in range(len(matrix[0])):
            value_in_fixed_column = matrix[fixed_row_index][i]
            # get (n-1)*(n-1) matrix
            smaller_matrix = copy.deepcopy(matrix)
            del smaller_matrix[fixed_row_index]
            for j in range(len(smaller_matrix)):
                del smaller_matrix[j][i]
            # calculate new value
            det = calculate_determinant(smaller_matrix)
            values.append(det)
        # apply sign table to values and add up to get the final determinant
        matrix_of_minors.append(values)
    return matrix_of_minors


def calculate_matrix_of_cofactors(matrix):
    minor_matrix = calculate_matrix_of_minors(matrix)
    cofactor_matrix = minor_matrix
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if (i + j) % 2 == 1:
                cofactor_matrix[i][j] *= -1
    return cofactor_matrix


def calculate_inverse_of_matrix(matrix):
    cofactor_matrix = calculate_matrix_of_cofactors(matrix)
    determinant = calculate_determinant(matrix)
    # transpose matrix of cofactors
    transposed_matrix = []
    for i in range(len(cofactor_matrix)):
        transposed_matrix.append([cofactor_matrix[j][i] for j in range(len(cofactor_matrix))])
    # divide transposed matrix by the determinant to get the inverse matrix
    inverse_matrix = []
    for i in transposed_matrix:
        new_line = []
        for j in i:
            new_line.append(j / determinant)
        inverse_matrix.append(new_line)
    return inverse_matrix


def matrix_vector_multiplication(matrix, vector):
    new_vector = []
    if len(matrix) == len(matrix[0]) == len(vector):
        for i in range(len(matrix)):
            new_value = 0
            for j in range(len(matrix[0])):
                new_value += matrix[i][j] * vector[j]
            new_vector.append(new_value)
        return new_vector

    else:
        print('Invalid input')
        return False


def matrix_matrix_multiplication(matrix1, matrix2):
    pass


def solve_system_of_2_equations(x1, y1, c1, x2, y2, c2):
    input_matrix = [[x1, y1],
                    [x2, y2]]
    output_vector = [c1, c2]
    inverse_matrix = calculate_inverse_of_matrix(input_matrix)
    vector_of_solutions = matrix_vector_multiplication(inverse_matrix, output_vector)
    return vector_of_solutions


def dot_product(vector_1, vector_2):
    dot_product = 0
    for i in range(len(vector_1)):
        dot_product += vector_1[i] * vector_2[i]
    return dot_product


def vector_to_unit_vector(vector):
    original_length = sum([i**2 for i in vector]) ** 0.5
    unit_vector = [i/original_length for i in vector]
    return unit_vector



if __name__ == "__main__":
    two_by_two_matrix = [[2, -4],
                         [5, 0]]

    three_by_three_matrix = [[1, 3, 2],
                             [4, 1, 3],
                             [2, 5, 2]]

    two_d_vector = [1, 1]

    print(calculate_determinant(three_by_three_matrix))
    print(calculate_matrix_of_minors(three_by_three_matrix))
    print(calculate_matrix_of_cofactors(three_by_three_matrix))
    print(calculate_inverse_of_matrix(two_by_two_matrix))
    print(matrix_vector_multiplication(two_by_two_matrix, two_d_vector))
