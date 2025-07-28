import math
import numpy as np
from typing import List

from system.quadruped.point import Point

"""
Generates points along a Bezier and returns results as an array of vectors.
See ./plot/bezier_curve_plot.py for example unscaled plot.
"""


@staticmethod
def generate_bezier_points(num_points: int, length_scale: float, height_scale: float) -> List[Point]:
    """
    Generates equally spaced points along a Beizer curve in the y and z axis
    """

    # Bernstein polynomial function
    def bernstein(t, i, n):
        return math.comb(n, i) * (t**i) * ((1 - t) ** (n - i))

    base_control_points = np.array(
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

    control_points = np.array([[point[0] * length_scale, point[1] * height_scale] for point in base_control_points])
    t_values_sample = np.linspace(0, 1, num_points)
    vectors: List[Point] = []

    # Compute the corresponding points on the Bézier curve
    n = len(control_points) - 1
    for j, t in enumerate(t_values_sample):
        point = np.zeros(2)
        for i in range(n + 1):
            point += bernstein(t, i, n) * control_points[i]
        vectors.append(Point(0, point[0], point[1]))
    return vectors
