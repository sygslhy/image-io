import pytest
import numpy as np
from cxx_image_io import DynamicMatrix, Matrix3

pytestmark = pytest.mark.unittest


def test_array_conv_dynamic_matrix():
    """
    Scenario: Convert a 2x2 DynamicMatrix to a NumPy array

    Given a 2x2 DynamicMatrix [[1.0, 2.0], [3.0, 4.0]]
    When I convert it to a NumPy array
    Then the resulting array should have shape (2, 2)
    And the values should match [[1.0, 2.0], [3.0, 4.0]]
    """
    matrix = DynamicMatrix([[1.0, 2.0], [3.0, 4.0]])
    array = np.array(matrix)
    assert array.shape == (2, 2)
    assert np.allclose(array, np.array([[1.0, 2.0], [3.0, 4.0]]))


def test_array_conv_matrix3():
    """
    Scenario: Convert a 3x3 Matrix3 to a NumPy array

    Given a 3x3 Matrix3 [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
    When I convert it to a NumPy array
    Then the resulting array should have shape (3, 3)
    And the values should match [[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]]
    """
    matrix = Matrix3([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    array = np.array(matrix)
    assert array.shape == (3, 3)
    assert np.allclose(array, np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]))


def test_incorrect_size_array_conv_matrix3():
    """
    Scenario: Creating a Matrix3 with incorrect shape should raise RuntimeError

    Given a 2x3 list [[1.0,2.0,3.0],[4.0,5.0,6.0]]
    When I attempt to create a Matrix3 from it
    Then a RuntimeError with message "Incompatible buffer shape!" should be raised
    """
    with pytest.raises(RuntimeError, match="Incompatible buffer shape!"):
        Matrix3([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])


def test_dynamic_matrix_empty():
    """
    Scenario: Creating an empty DynamicMatrix with no data should raise TypeError

    Given no input
    When I attempt to create a DynamicMatrix()
    Then a TypeError should be raised
    """
    with pytest.raises(TypeError):
        DynamicMatrix()


def test_matrix3_empty():
    """
    Scenario: Creating an empty Matrix3 with no data should raise TypeError

    Given no input
    When I attempt to create a Matrix3()
    Then a TypeError should be raised
    """
    with pytest.raises(TypeError):
        Matrix3()


def test_dynamic_matrix_single_row_col():
    """
    Scenario: DynamicMatrix with single row or single column

    Given a 1x3 matrix [[1.0, 2.0, 3.0]]
    When I convert it to a NumPy array
    Then the array should have shape (1,3) and values [[1.0, 2.0, 3.0]]

    Given a 3x1 matrix [[1.0],[2.0],[3.0]]
    When I convert it to a NumPy array
    Then the array should have shape (3,1) and values [[1.0],[2.0],[3.0]]
    """
    matrix = DynamicMatrix([[1.0, 2.0, 3.0]])
    array = np.array(matrix)
    assert array.shape == (1, 3)
    assert np.allclose(array, [[1.0, 2.0, 3.0]])

    matrix = DynamicMatrix([[1.0], [2.0], [3.0]])
    array = np.array(matrix)
    assert array.shape == (3, 1)
    assert np.allclose(array, [[1.0], [2.0], [3.0]])


def test_dynamic_matrix_mixed_types():
    """
    Scenario: DynamicMatrix with mixed int and float values

    Given a 2x2 list [[1,2.5],[3,4]]
    When I convert it to DynamicMatrix and then to NumPy array
    Then all values should be float and match [[1.0,2.5],[3.0,4.0]]
    """
    matrix = DynamicMatrix([[1, 2.5], [3, 4]])
    array = np.array(matrix)
    assert np.allclose(array, [[1.0, 2.5], [3.0, 4.0]])


def test_dynamic_matrix_inconsistent_columns():
    """
    Scenario: DynamicMatrix with inconsistent row lengths should raise TypeError

    Given a list [[1,2],[3]]
    When I attempt to create a DynamicMatrix
    Then a TypeError should be raised
    """
    with pytest.raises(TypeError):
        DynamicMatrix([[1, 2], [3]])


def test_matrix3_wrong_shape_4x4():
    """
    Scenario: Matrix3 with 4x4 shape should raise RuntimeError

    Given a 4x4 list
    When I attempt to create a Matrix3
    Then a RuntimeError with message 'Incompatible buffer shape!' should be raised
    """
    with pytest.raises(RuntimeError, match="Incompatible buffer shape!"):
        Matrix3([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])


def test_dynamic_matrix_serialize_repr():
    """
    Scenario: DynamicMatrix serialize and repr

    Given a 2x2 DynamicMatrix [[1.0,2.0],[3.0,4.0]]
    When I call serialize() and repr()
    Then serialize() should return [[1.0,2.0],[3.0,4.0]]
    And repr() should match str(serialized)
    """
    matrix = DynamicMatrix([[1.0, 2.0], [3.0, 4.0]])
    serialized = matrix.serialize()
    repr_str = repr(matrix)
    assert serialized == [[1.0, 2.0], [3.0, 4.0]]
    assert repr_str == str(serialized)


def test_matrix3_serialize_repr():
    """
    Scenario: Matrix3 serialize and repr

    Given a 3x3 Matrix3 [[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]]
    When I call serialize() and repr()
    Then serialize() should return [[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]]
    And repr() should match str(serialized)
    """
    matrix = Matrix3([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    serialized = matrix.serialize()
    repr_str = repr(matrix)
    assert serialized == [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
    assert repr_str == str(serialized)


def test_matrix3_with_nan_inf():
    """
    Scenario: Matrix3 containing NaN and Inf

    Given a 3x3 Matrix3 [[nan,1.0,2.0],[3.0,inf,5.0],[6.0,7.0,8.0]]
    When I convert it to NumPy array
    Then the (0,0) element should be NaN
    And the (1,1) element should be Inf
    """
    import math
    matrix = Matrix3([[math.nan, 1.0, 2.0], [3.0, math.inf, 5.0], [6.0, 7.0, 8.0]])
    array = np.array(matrix)
    assert math.isnan(array[0, 0])
    assert math.isinf(array[1, 1])
