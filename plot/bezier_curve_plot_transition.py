#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import math


"""
Standalone script to make a Bezier curve plot with interpolated points along the path.

Demonstrates correcting 
"""

# Case were non-corrected equal distant points appear valid
control_points = np.array(
    [
        [0, 1],
        [0, 0],
        [1, 0],
    ]
)

# Case were non-correct equal distant points appear invalid
control_points = np.array(
    [
        [0, 0.5],
        [0, 0],
        [1, 1],
    ]
)


def distance_between_points(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    # Calculating Euclidean distance
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def angle_between(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    angle_radians = math.atan2(y2 - y1, x2 - x1)
    angle_degrees = math.degrees(angle_radians)
    return angle_degrees


def move_point(point, distance, angle_degrees):
    angle_radians = math.radians(angle_degrees)
    delta_x = distance * math.cos(angle_radians)
    delta_y = distance * math.sin(angle_radians)
    new_x = point[0] + delta_x
    new_y = point[1] + delta_y
    return (new_x, new_y)


# Bernstein polynomial function
def bernstein(t, i, n):
    return math.comb(n, i) * (t**i) * ((1 - t) ** (n - i))


# Bézier curve function
def bezier_curve(control_points, num_points=1000):
    n = len(control_points) - 1
    t_values = np.linspace(0, 1, num_points)
    curve_points = np.zeros((num_points, 2))

    for j, t in enumerate(t_values):
        curve_point = np.zeros(2)
        for i in range(n + 1):
            curve_point += bernstein(t, i, n) * control_points[i]
        curve_points[j] = curve_point

    return curve_points


# Generate the Bézier curve
bezier_points = bezier_curve(control_points)

# Generate equally spaced points along the curve
num_sample_points = 20
t_values_sample = np.linspace(0, 1, num_sample_points)
sampled_points = np.zeros((num_sample_points, 2))
n = len(control_points) - 1
for j, t in enumerate(t_values_sample):
    point = np.zeros(2)
    for i in range(n + 1):
        point += bernstein(t, i, n) * control_points[i]
    sampled_points[j] = point


# Get average distance between the points
distances = np.sqrt(np.sum(np.diff(sampled_points, axis=0) ** 2, axis=1))
average_distance = np.mean(distances)
print("Average distance:", average_distance)


# Generate equally spaced points along the curve
num_sample_points = 1000
t_values_sample = np.linspace(0, 1, num_sample_points)
all = np.zeros((num_sample_points, 2))
n = len(control_points) - 1
for j, t in enumerate(t_values_sample):
    point = np.zeros(2)
    for i in range(n + 1):
        point += bernstein(t, i, n) * control_points[i]
    all[j] = point

# Extract equal distance points, remove middle points
corrected_points = []
i = 1
end = len(all)
check = 0
while i < end:
    if distance_between_points(all[check], all[i]) < average_distance:
        i += 1
    else:
        corrected_points.append(all[check])
        check = i
corrected_points.append(all[-1])

distance_last_two = distance_between_points(corrected_points[-2], corrected_points[-1])
print("distance_last_two: ", distance_last_two)
angle = angle_between(corrected_points[0], corrected_points[-1])
print("angle_between: ", angle)

# Stretch points in the direction of the each point relative to the last point to close the gap of the last two points.
for i in range(len(corrected_points) - 1):
    angle = angle_between(corrected_points[i], corrected_points[-1])
    distance = (distance_last_two - average_distance) * i / len(corrected_points)
    corrected_points[i] = move_point(corrected_points[i], distance, angle)

corrected_points = np.array(corrected_points)


fig, axs = plt.subplots(2, 2, figsize=(10, 8))

# Plot 1: Bézier Curve
axs[0, 0].plot(bezier_points[:, 0], bezier_points[:, 1], label="Bézier Curve", color="blue")
axs[0, 0].set_title("Bézier Curve")
axs[0, 0].grid(True)
axs[0, 0].set_aspect("equal", adjustable="box")
axs[0, 0].legend()

# Plot 2: Control Points
axs[0, 1].plot(control_points[:, 0], control_points[:, 1], "ro-", label="Control Points")
axs[0, 1].set_title("Control Points")
axs[0, 1].grid(True)
axs[0, 1].set_aspect("equal", adjustable="box")
axs[0, 1].legend()

# Plot 3: Equally Spaced Points
axs[1, 0].plot(
    sampled_points[:, 0],
    sampled_points[:, 1],
    "go-",
    label="Equally Spaced Points",
    markersize=3,
)
axs[1, 0].set_title("Equally Spaced Points")
axs[1, 0].grid(True)
axs[1, 0].set_aspect("equal", adjustable="box")
axs[1, 0].legend()

# Plot 4: Corrected Points
axs[1, 1].plot(corrected_points[:, 0], corrected_points[:, 1], "bo-", label="Corrected Points")
axs[1, 1].set_title("Corrected Points")
axs[1, 1].grid(True)
axs[1, 1].set_aspect("equal", adjustable="box")
axs[1, 1].legend()

# Make sure that all subplots have the same axis limits
# Find the min and max for all points
all_points = [bezier_points, control_points, sampled_points, corrected_points]

offset = 0.05
x_min = min([point[:, 0].min() - offset for point in all_points])
x_max = max([point[:, 0].max() + offset for point in all_points])
y_min = min([point[:, 1].min() - offset for point in all_points])
y_max = max([point[:, 1].max() + offset for point in all_points])

# Set the same axis limits for all subplots
for ax in axs.flat:
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

# Adjust layout for better spacing
plt.tight_layout()
plt.show()
