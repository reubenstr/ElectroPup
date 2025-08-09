#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import math

"""
    Standalone script to make Bezier curve plot with interpolated points along the path.
"""

control_points = np.array(
    [
        [-0.5, 0],
        [-1, 0],
        [-1, 1],
        [0, 1],
        [1, 1],
        [1, 0],
        [0.5, 0],
    ]
)


# Bernstein polynomial function
def bernstein(t, i, n):
    return math.comb(n, i) * (t**i) * ((1 - t) ** (n - i))


# Bézier curve function
def bezier_curve(control_points: np.array, num_points: int):
    n = len(control_points) - 1  # Degree of the curve (4 for 5 control points)
    t_values = np.linspace(0, 1, num_points)
    curve_points = np.zeros((num_points, 2))

    for j, t in enumerate(t_values):
        curve_point = np.zeros(2)
        for i in range(n + 1):
            curve_point += bernstein(t, i, n) * control_points[i]
        curve_points[j] = curve_point

    return curve_points


bezier_points = bezier_curve(control_points, num_points=1000)
sampled_points = bezier_curve(control_points, num_points=20)


plt.figure(figsize=(8, 6))
plt.plot(bezier_points[:, 0], bezier_points[:, 1], label="Bézier Curve", color="blue")
plt.plot(control_points[:, 0], control_points[:, 1], "ro-", label="Control Points")
plt.plot(
    sampled_points[:, 0],
    sampled_points[:, 1],
    "go",
    label="Equally Spaced Points",
    markersize=8,
)
plt.title("Bézier Curve")
plt.legend()
plt.grid(True)
plt.gca().set_aspect("equal", adjustable="box")
plt.show()
