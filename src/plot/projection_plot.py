#!/usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt, cos, sin, acos
import copy

class Point:
    __slots__ = ("x", "y", "z", "name")

    def __init__(self, x, y, z, name=None):
        self.x = x
        self.y = y
        self.z = z
        self.name = name

    def move_xyz(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz

def move_point_to_radius_even_arc(point, radius, x_start, x_end, total_points, index, arc_center=(0,0)):
    """
    Moves a point to lie on a circle with given radius and arc center,
    positioning it evenly by arc length between x_start and x_end.

    Args:
        point: Point object to move (modified in-place)
        radius: Radius of the circle
        x_start: Starting x of the arc
        x_end: Ending x of the arc
        total_points: Total number of points in the arc
        index: Index of this point in the sequence (0-based)
        arc_center: (cx, cy) center of the circle
    """
    cx, cy = arc_center
    
    theta_start = acos(max(min((x_start - cx) / radius, 1.0), -1.0))
    theta_end   = acos(max(min((x_end - cx) / radius, 1.0), -1.0))
    
    theta = theta_start + (theta_end - theta_start) * (index / (total_points - 1))
    
    point.x = cx + radius * cos(theta)
    point.y = cy + radius * sin(theta) - radius

def plot_scene(ax, radius):
    x_vals = np.linspace(-4, 4, 15)
    
    before_points = [Point(x, 0, 0) for x in x_vals]
    after_points = copy.deepcopy(before_points)
    
    for i, p in enumerate(after_points):
        move_point_to_radius_even_arc(p, radius=radius, x_start=min(x_vals), x_end=max(x_vals),
                                      total_points=len(after_points), index=i)

    
    ax.set_aspect('equal', adjustable='box')
    ax.scatter([p.x for p in before_points], [p.y for p in before_points], c='blue', label='Before')
    ax.scatter([p.x for p in after_points], [p.y for p in after_points], c='red', label='After')
    for b, a in zip(before_points, after_points):
        ax.plot([b.x, a.x], [b.y, a.y], 'k--', linewidth=0.8)
    circle = plt.Circle((0, -radius), radius, color='green', fill=False, linestyle='solid')
    ax.add_artist(circle)
    ax.set_xlim(-radius - 1, radius + 1)
    ax.set_ylim(-radius - 1, radius + 1)
    ax.legend()
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True)
    ax.set_title(f'Radius = {radius}')

# Plot side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
fig.suptitle("Comparison of Arc Projection for Different Radii", fontsize=14)
plot_scene(ax1, radius=6)
plot_scene(ax2, radius=3)
plt.show()
