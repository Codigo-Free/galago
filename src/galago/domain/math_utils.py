def bezier_point(p0, p1, p2, p3, t):
    """Calcula un punto en una curva de Bézier cúbica (t va de 0.0 a 1.0)."""
    u = 1.0 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t

    x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
    y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
    return float(x), float(y)
