# This script runs unit tests for functions in eval_tools.

import math

from tools import eval_tools


def assert_calculate_angle_diff(x, y, angle):

    result = eval_tools.calculate_angle_diff(x, y)
    assert math.isclose(result, angle, rel_tol=1e-4)


def test_calculate_angle_diff():

    assert_calculate_angle_diff(0, 0, 0)
    assert_calculate_angle_diff(90, 90, 0)
    assert_calculate_angle_diff(0, 315, 45)
    assert_calculate_angle_diff(315, 0, 45)
    assert_calculate_angle_diff(0, 180, 180)
    assert_calculate_angle_diff(0, 179, 179)
    assert_calculate_angle_diff(0, 181, 179)
