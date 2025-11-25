import numpy as np
import pytest

from cxx_image_io import DynamicMatrix, Matrix3

pytestmark = pytest.mark.unittest


def test_array_conv_dynamic_matrix():
    # Given: a 2x2 DynamicMatrix [[1.0, 2.0], [3.0, 4.0]]
    matrix = DynamicMatrix([[1.0, 2.0], [3.0, 4.0]])

    # When: I convert it to a NumPy array
    array = np.array(matrix)

    # Then: the resulting array should have shape (2, 2)
    assert array.shape == (2, 2)
    # And: the values should match [[1.0, 2.0], [3.0, 4.0]]
    assert np.allclose(array, [[1.0, 2.0], [3.0, 4.0]])


def test_array_conv_matrix3():
    # Given: a 3x3 Matrix3 [[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]]
    matrix = Matrix3([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])

    # When: I convert it to a NumPy array
    array = np.array(matrix)

    # Then: the resulting array should have shape (3, 3)
    assert array.shape == (3, 3)
    # And: the values should match the original
    assert np.allclose(array, [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])


def test_incorrect_size_array_conv_matrix3():
    # Given: a 2x3 list [[1.0,2.0,3.0],[4.0,5.0,6.0]]
    # When: I attempt to create a Matrix3 from it
    # Then: a RuntimeError with message "Incompatible buffer shape!" should be raised
    with pytest.raises(RuntimeError, match="Incompatible buffer shape!"):
        Matrix3([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])


def test_dynamic_matrix_empty():
    # Given: no input
    # When: I attempt to create a DynamicMatrix()
    # Then: a TypeError should be raised
    with pytest.raises(TypeError):
        DynamicMatrix()


def test_matrix3_empty():
    # Given: no input
    # When: I attempt to create a Matrix3()
    # Then: a TypeError should be raised
    with pytest.raises(TypeError):
        Matrix3()


def test_dynamic_matrix_single_row_col():
    # Given: a 1x3 DynamicMatrix [[1.0, 2.0, 3.0]]
    matrix = DynamicMatrix([[1.0, 2.0, 3.0]])
    # When: I convert it to a NumPy array
    array = np.array(matrix)
    # Then: the array should have shape (1,3) and values [[1.0,2.0,3.0]]
    assert array.shape == (1, 3)
    assert np.allclose(array, [[1.0, 2.0, 3.0]])

    # Given: a 3x1 DynamicMatrix [[1.0],[2.0],[3.0]]
    matrix = DynamicMatrix([[1.0], [2.0], [3.0]])
    # When: I convert it to a NumPy array
    array = np.array(matrix)
    # Then: the array should have shape (3,1) and values [[1.0],[2.0],[3.0]]
    assert array.shape == (3, 1)
    assert np.allclose(array, [[1.0], [2.0], [3.0]])


def test_dynamic_matrix_mixed_types():
    # Given: a 2x2 list [[1,2.5],[3,4]] with mixed int and float
    matrix = DynamicMatrix([[1, 2.5], [3, 4]])
    # When: I convert it to a NumPy array
    array = np.array(matrix)
    # Then: all values should be float and match [[1.0,2.5],[3.0,4.0]]
    assert np.allclose(array, [[1.0, 2.5], [3.0, 4.0]])


def test_dynamic_matrix_inconsistent_columns():
    # Given: a list [[1,2],[3]] with inconsistent row lengths
    # When: I attempt to create a DynamicMatrix
    # Then: a TypeError should be raised
    with pytest.raises(TypeError):
        DynamicMatrix([[1, 2], [3]])


def test_matrix3_wrong_shape_4x4():
    # Given: a 4x4 list
    # When: I attempt to create a Matrix3
    # Then: a RuntimeError with message 'Incompatible buffer shape!' should be raised
    with pytest.raises(RuntimeError, match="Incompatible buffer shape!"):
        Matrix3([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])


def test_dynamic_matrix_serialize_repr():
    # Given: a 2x2 DynamicMatrix [[1.0,2.0],[3.0,4.0]]
    matrix = DynamicMatrix([[1.0, 2.0], [3.0, 4.0]])

    # When: I call serialize() and repr()
    serialized = matrix.serialize()
    repr_str = repr(matrix)

    # Then: serialize() should return [[1.0,2.0],[3.0,4.0]]
    assert serialized == [[1.0, 2.0], [3.0, 4.0]]
    # And: repr() should match str(serialized)
    assert repr_str == "[[1.0, 2.0], [3.0, 4.0]]"


def test_matrix3_serialize_repr():
    # Given: a 3x3 Matrix3 [[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]]
    matrix = Matrix3([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])

    # When: I call serialize() and repr()
    serialized = matrix.serialize()
    repr_str = repr(matrix)

    # Then: serialize() should return [[1.0,2.0,3.0],[4.0,5.0,6.0],[7.0,8.0,9.0]]
    assert serialized == [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
    # And: repr() should match str(serialized)
    assert repr_str == "[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]"


def test_matrix3_with_nan_inf():
    import math

    # Given: a 3x3 Matrix3 [[nan,1.0,2.0],[3.0,inf,5.0],[6.0,7.0,8.0]]
    matrix = Matrix3([[math.nan, 1.0, 2.0], [3.0, math.inf, 5.0], [6.0, 7.0, 8.0]])

    # When: I convert it to a NumPy array
    array = np.array(matrix)

    # Then: the (0,0) element should be NaN
    assert math.isnan(array[0, 0])
    # And: the (1,1) element should be Inf
    assert math.isinf(array[1, 1])
