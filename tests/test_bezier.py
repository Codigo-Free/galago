from galago.domain.math_utils import bezier_point


def test_bezier_endpoints():
    p0, p1, p2, p3 = (0, 0), (10, 40), (30, 40), (40, 0)
    assert bezier_point(p0, p1, p2, p3, 0.0) == (float(p0[0]), float(p0[1]))
    assert bezier_point(p0, p1, p2, p3, 1.0) == (float(p3[0]), float(p3[1]))


def test_bezier_midpoint_is_between_control_points():
    p0, p1, p2, p3 = (0, 0), (0, 100), (100, 100), (100, 0)
    x, y = bezier_point(p0, p1, p2, p3, 0.5)
    assert 0.0 < x < 100.0
    assert y > 0.0
