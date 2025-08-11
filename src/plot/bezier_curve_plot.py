#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import math

"""
    Standalone script to visualize Bezier curve plot with interpolated points along the path.
"""

# Control point sets
control_sets = [
    np.array([
        [-0.5, 0],
        [-1, 0],
        [-1, 1],
        [0, 1],
        [1, 1],
        [1, 0],
        [0.5, 0],
    ]),
    np.array([
        [-0.5, 0],
        [-1.5, 0.5],
        [-1, 1.5],
        [0, 1],
        [1, 1.5],
        [1.5, 0.5],
        [0.5, 0],
    ]),
    np.array([
        [-0.5, 0],
        [-0.5, 1],
        [-.5, 2],
        [0, 2],
        [0.5, 2],
        [0.5, 1],
        [0.5, 0],
    ]),
    np.array([
        [-1, 0],
        [-1, 0],
        [-1, 1],
        [0, 1],
        [1, 1],
        [1, 0],
        [1, 0],
    ])
]

titles = [
    "Bézier Curve - Set 1",
    "Bézier Curve - Set 2",
    "Bézier Curve - Set 3",
    "Bézier Curve - Set 4",
]

# Bernstein polynomial function
def bernstein(t, i, n):
    return math.comb(n, i) * (t**i) * ((1 - t) ** (n - i))

# Bézier curve function
def bezier_curve(control_points: np.array, num_points: int):
    n = len(control_points) - 1
    t_values = np.linspace(0, 1, num_points)
    curve_points = np.zeros((num_points, 2))
    for j, t in enumerate(t_values):
        curve_point = np.zeros(2)
        for i in range(n + 1):
            curve_point += bernstein(t, i, n) * control_points[i]
        curve_points[j] = curve_point
    return curve_points

# Plot all 4 curves
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle("Comparison of Bezier Control Points", fontsize=14)

for ax, control_points, title in zip(axes.flatten(), control_sets, titles):
    bezier_points = bezier_curve(control_points, num_points=1000)
    sampled_points = bezier_curve(control_points, num_points=20)

    ax.plot(bezier_points[:, 0], bezier_points[:, 1], label="Bézier Curve", color="blue")
    ax.plot(control_points[:, 0], control_points[:, 1], "ro-", label="Control Points")
    ax.plot(
        sampled_points[:, 0],
        sampled_points[:, 1],
        "go",
        label="Sampled Points",
        markersize=8,
    )
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    ax.set_aspect("equal", adjustable="box")

plt.tight_layout()
plt.show()
