from dataclasses import dataclass
from math import sqrt, radians, sin, cos, degrees, acos, isnan, atan2
from typing import Tuple
import numpy as np


class Point:
    __slots__ = ("x", "y", "z", "name")

    def __init__(self, x, y, z, name=None):
        self.x = x
        self.y = y
        self.z = z
        self.name = name

    def get_point_wrt(self, reference_frame, name=None):
        """
        Given frame_ab which is the pose of frame_b wrt frame_a
        and that this point is defined wrt to frame_b
        Return point defined wrt to frame a
        """
        p = np.array([self.x, self.y, self.z, 1])
        p = np.matmul(reference_frame, p)
        return Point(p[0], p[1], p[2], name)

    def update_point_wrt_frame(self, reference_frame):
        p = np.array([self.x, self.y, self.z, 1])
        p = np.matmul(reference_frame, p)
        self.x = p[0]
        self.y = p[1]
        self.z = p[2]

    def move_xyz(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z

    def move_up(self, z):
        self.z += z

    def scale(self, factor):
        return Point(self.x * factor, self.y * factor, self.z * factor)

    def magnitude(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def as_array(self):
        return np.array([self.x, self.y, self.z])

    @property
    def vec(self):
        return self.x, self.y, self.z

    def __repr__(self):
        s = f"Vector(x={self.x:>+8.3f}, y={self.y:>+8.3f}, z={self.z:>+8.3f}, name='{self.name}')"
        return s

    def __str__(self):
        return repr(self)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __eq__(self, other, percent_tol=0.0075):
        if not isinstance(other, Point):
            return False

        tol = length(self) * percent_tol
        equal_val = np.allclose(self.vec, other.vec, atol=tol)
        equal_name = self.name == other.name
        return equal_val and equal_name


# *********************************************
# https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
# https://www.geeksforgeeks.org/check-whether-a-given-point-lies-inside-a-triangle-or-not/
# It works like this:
# - Walk clockwise or counterclockwise around the triangle
# and project the point onto the segment we are crossing
# by using the dot product.
# - Check that the vector created is on the same side
# for each of the triangle's segments
def is_point_inside_triangle(p, a, b, c):
    ab = (p.x - b.x) * (a.y - b.y) - (a.x - b.x) * (p.y - b.y)
    bc = (p.x - c.x) * (b.y - c.y) - (b.x - c.x) * (p.y - c.y)
    ca = (p.x - a.x) * (c.y - a.y) - (c.x - a.x) * (p.y - a.y)
    # must be all positive or all negative
    return (ab < 0.0) == (bc < 0.0) == (ca < 0.0)


def is_triangle(a, b, c):
    return (a + b > c) and (a + c > b) and (b + c > a)


# https://www.maplesoft.com/support/help/Maple/view.aspx?path=MathApps%2FProjectionOfVectorOntoPlane
# u is the vector, n is the plane normal
def project_vector_onto_plane(u, n):
    s = dot(u, n) / dot(n, n)
    temporary_vector = scalar_multiply(n, s)
    return subtract_vectors(u, temporary_vector)


def angle_between(a, b):
    # returns the shortest angle between two vectors
    cos_theta = dot(a, b) / sqrt(dot(a, a) * dot(b, b))

    # Clamp the value within the valid range
    cos_theta = max(-1.0, min(1.0, cos_theta))

    theta = degrees(acos(cos_theta))

    if isnan(theta):
        """ print(
            f"ERROR: angle_between({a}, {b}) is NAN\
        ... One of them might be a zero vector\
        ... the vectors might be pointing at the same direction or\
        ... something else entirely."
        )         """
        return 0.0

    return theta


def angle_opposite_of_last_side(a, b, c):
    ratio = (a * a + b * b - c * c) / (2 * a * b)
    return degrees(acos(ratio))


# Check if angle from vector a to b about normal n is positive
# Rotating from vector a to is moving into a counter clockwise direction
def is_counter_clockwise(a, b, n):
    return dot(a, cross(b, n)) > 0


# https://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d
def frame_to_align_vector_a_to_b(a, b):
    v = cross(a, b)
    s = length(v)

    # When angle between a and b is zero or 180 degrees
    # cross product is 0, R = I
    if s == 0.0:
        return np.eye(4)
    c = dot(a, b)
    i = np.eye(3)  # Identity matrix 3x3

    # skew symmetric cross product
    vx = skew(v)
    d = (1 - c) / (s * s)
    r = i + vx + np.matmul(vx, vx) * d

    # r00 r01 r02 0
    # r10 r11 r12 0
    # r20 r21 r22 0
    #  0   0   0  1
    r = np.hstack((r, [[0], [0], [0]]))
    r = np.vstack((r, [0, 0, 0, 1]))
    return r


# rotate about y, translate in x
def frame_yrotate_xtranslate(theta, x):
    c, s = _return_sin_and_cos(theta)
    return np.array([[c, 0, s, x], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])


# rotate about z, translate in x and y
def frame_zrotate_xytranslate(theta, x, y):
    c, s = _return_sin_and_cos(theta)
    return np.array([[c, -s, 0, x], [s, c, 0, y], [0, 0, 1, 0], [0, 0, 0, 1]])


def frame_rotxyz(a, b, c):
    rx = rotx(a)
    ry = roty(b)
    rz = rotz(c)
    rxy = np.matmul(rx, ry)
    rxyz = np.matmul(rxy, rz)
    return rxyz

def rotate_z(point: Point, angle_deg: float):
    angle_rad = radians(angle_deg)
    x = point.x * cos(angle_rad) - point.y * sin(angle_rad)
    y = point.x * sin(angle_rad) + point.y * cos(angle_rad)
    z = point.z
    return Point(x, y, z)


def get_x_vector_from_frame(frame):
    raw = frame[:, 0]
    return Point(raw[0], raw[1], raw[2])


def get_y_vector_from_frame(frame):
    raw = frame[:, 1]
    return Point(raw[0], raw[1], raw[2])


def get_z_vector_from_frame(frame):
    raw = frame[:, 2]
    return Point(raw[0], raw[1], raw[2])


def rotx(theta):
    c, s = _return_sin_and_cos(theta)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]])


def roty(theta):
    c, s = _return_sin_and_cos(theta)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])


def rotz(theta):
    c, s = _return_sin_and_cos(theta)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])


def _return_sin_and_cos(theta):
    d = radians(theta)
    c = cos(d)
    s = sin(d)
    return c, s


# get vector pointing from point a to point b
def vector_from_to(a, b):
    return Point(b.x - a.x, b.y - a.y, b.z - a.z)


def scale(v, d):
    return Point(v.x / d, v.y / d, v.z / d)


def dot(a, b):
    return a.x * b.x + a.y * b.y + a.z * b.z


def cross(a, b):
    x = a.y * b.z - a.z * b.y
    y = a.z * b.x - a.x * b.z
    z = a.x * b.y - a.y * b.x
    return Point(x, y, z)


def length(v):
    return sqrt(dot(v, v))


def add_vectors(a, b):
    return Point(a.x + b.x, a.y + b.y, a.z + b.z)


def subtract_vectors(a, b):
    return Point(a.x - b.x, a.y - b.y, a.z - b.z)


def scalar_multiply(p, s):
    return Point(s * p.x, s * p.y, s * p.z)


def get_unit_vector(v):
    return scale(v, length(v))


def get_normal_given_three_points(a, b, c):
    """
    Get the unit normal vector to the
    plane defined by the points a, b, c.
    """
    ab = vector_from_to(a, b)
    ac = vector_from_to(a, c)
    v = cross(ab, ac)
    v = scale(v, length(v))
    return v


def skew(p):
    return np.array([[0, -p.z, p.y], [p.z, 0, -p.x], [-p.y, p.x, 0]])


def get_distance_xy(a, b):
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


def get_distance_xyz(a, b):
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2 + (b.z - a.z) ** 2)


def angle_between_xy(a, b):
    return degrees(atan2(b.y - a.y, b.x - a.x))


def get_distance_statistics(vectors: np.ndarray) -> Tuple[float, float, float]:
    """
    Calculate distance statistics on array of vectors: min, average, and max distances between points
    """
    min_dist: float = float("inf")
    avg_dist: float = 0
    max_dist: float = 0
    for i in range(1, len(vectors) - 1):
        distance = get_distance_xy(vectors[i - 1], vectors[i])
        avg_dist = avg_dist + distance
        max_dist = max(max_dist, distance)
        min_dist = min(min_dist, distance)
    avg_dist = avg_dist / len(vectors) - 1
    return min_dist, avg_dist, max_dist


# https://math.stackexchange.com/questions/1391470/find-distance-between-point-on-tangent-line-and-circle
def move_point_y_to_radius(point: Point, radius: float):
    """
    Moves a point along the x axis to a given radius.
    """

    a = point.x * 2

    if (radius * radius) - (a * a) / 4 < 0:
        return

    distance_from_circle = abs(radius) - sqrt((abs(radius) * abs(radius)) - (a * a) / 4)

    if radius > 0:
        distance_from_circle = -distance_from_circle

    point.move_xyz(0, distance_from_circle, 0)
