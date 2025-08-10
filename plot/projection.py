import numpy as np
import matplotlib.pyplot as plt
from math import radians, degrees, cos, sin

class Point:
    __slots__ = ("x", "y", "z", "name")
    def __init__(self, x, y, z=0, name=None):
        self.x = x
        self.y = y
        self.z = z
        self.name = name

# Parameters
twist_angle = 45         # degrees - center direction of arc
radius = 5               # bend radius
num_points = 20          # number of points

# --- Original straight line ---
line_length = 8.0  # length of the straight segment
xs = np.linspace(-line_length/2, line_length/2, num_points)
ys = np.zeros_like(xs)
original_points = [Point(x, y) for x, y in zip(xs, ys)]

# --- Compute arc angle so arc length matches line length ---
arc_angle_rad = line_length / radius
arc_angle_deg = degrees(arc_angle_rad)

# --- Arc generation ---
arc_start = radians(twist_angle) - arc_angle_rad / 2
arc_end   = radians(twist_angle) + arc_angle_rad / 2
thetas = np.linspace(arc_start, arc_end, num_points)

arc_points = [Point(radius * cos(theta), radius * sin(theta)) for theta in thetas]

# --- Plot ---
plt.figure()
plt.scatter([p.x for p in original_points],
            [p.y for p in original_points],
            c='blue', label='Original Line')

plt.scatter([p.x for p in arc_points],
            [p.y for p in arc_points],
            c='red', marker='x', label=f'Bent Arc (arc len={line_length})')

# Connect each original to its arc projection
for op, ap in zip(original_points, arc_points):
    plt.plot([op.x, ap.x], [op.y, ap.y], 'k--', alpha=0.4)

# Reference circle
theta_full = np.linspace(0, 2*np.pi, 300)
plt.plot(radius*np.cos(theta_full), radius*np.sin(theta_full), 'gray', alpha=0.3)

plt.axis('equal')
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.title("Straight Line Bent to Arc with Preserved Length")
plt.show()
