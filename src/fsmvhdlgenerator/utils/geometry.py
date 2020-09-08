"""Defines generic math objects located on a coordinate system.

Classes:
    DimensionError: Error for incorrect numbers of dimensions
    Vector: A vector class representing an ordered collection of values
    Line: A line class representing a line segment
    Rectangle: A rectangle class representing a rectangle

"""

from math import atan2, cos, fsum, isclose, pi, sin, sqrt
from typing import Iterable, Optional, Union, overload


class DimensionError(ValueError):
    """A geometry element had the wrong number of dimensions."""


class Vector(Iterable[float]):
    """A simple multi-dimensional vector class, with many 2D methods.

    Capable of basic vector arithmetic. Like vectors in math, no attempt
    is made to qualify the vector, so these vectors may be used for positions,
    displacements, velocity, gradients, etc.

    Attributes:
        x: The first element of the vector, if there is one
        y: The second element of the vector, if there is one
        z: The third element of the vector, if there is one

    """
    def __init__(self, *elems: float):
        """Create a vector of numbers.

        Args:
            *args: The n different numbers of the n-dimensional vector

        """
        self._elems = list(elems)

        if 2 <= len(self._elems) <= 3:
            self.x, self.y = self._elems[0], self._elems[1]
            if len(self._elems) == 3:
                self.z = self._elems[2]

    @classmethod
    def polar(cls, radius: float, phase: float) -> 'Vector':
        """Create a 2D vector using polar coordinates.

        Args:
            radius: the length of the vector
            phase: the angle of the vector, in radians

        """
        return cls(radius * cos(phase), radius * sin(phase))

    def __repr__(self):
        """Return a string representation of the vector."""
        return 'Vector(' + ', '.join(map(str, self._elems)) + ')'

    def __str__(self):
        """Return a string representation of the vector in brackets: <1, 2>."""
        return '<' + ', '.join(map(str, self._elems)) + '>'

    def __iter__(self):
        """Iterate through the vector's elements."""
        for elem in self._elems:
            yield elem

    def __getitem__(self, dimension_idx):
        """Return the element in the vector along the nth dimension."""
        return self._elems[dimension_idx]

    def __len__(self):
        """Return the dimension of the vector."""
        return len(self._elems)

    def __abs__(self) -> float:
        """Return the magnitude of the vector."""
        return sqrt(fsum(e**2 for e in self._elems))

    def __add__(self, other: Union['Vector', float]) -> 'Vector':
        """Return the sum of 2 same dimension-numbered vectors.

        Also supported is the addition of a vector and a scaler, where each
        scaler is added to each element in the vector, and a new vector
        created and returned from those values.

        Raises:
            DimensionError: The vectors were not the same length

        """
        if not isinstance(other, Vector):
            return Vector(*(other + e for e in self))

        if len(self) != len(other):
            raise DimensionError("Vector dimensions don't match")

        return Vector(*(s + o for s, o in zip(self, other)))

    __radd__ = __add__

    def __neg__(self) -> 'Vector':
        """Return a new vector with each element negated."""
        return Vector(*(-e for e in self))

    def __sub__(self, other: Union['Vector', float]) -> 'Vector':
        """Return the difference of 2 same-dimensional vectors.

        Also supported is the difference of a scaler and a vector or vice
        versa, in which case the scaler is subtracted by or from each element
        in the vector, and a new vector is created and returned from those
        values.

        Raises:
            DimensionError: The vectors were not the same length

        """
        if not isinstance(other, Vector):
            return Vector(*(e - other for e in self._elems))

        if len(self) != len(other):
            raise DimensionError("Vector dimensions don't match")

        return Vector(*(s - o for s, o in zip(self, other)))

    def __rsub__(self, other: Union['Vector', float]):
        """Return the difference of 2 same-dimensional vectors.

        See the __sub__ method for more details.

        """
        return -self + other

    @overload
    def __mul__(self, other: 'Vector') -> float:
        """Return the dot product of the two vectors."""

    @overload
    def __mul__(self, other: float) -> 'Vector':
        """Return the scaler product of the vector."""

    def __mul__(self, other: Union['Vector', float]) -> Union['Vector', float]:
        """Return the scaler product of the vector and a number.

        Also returns the dot product if the other input is a Vector.

        Returns:
            If only one input is a vector, the scaler product is returned, but
            if both inputs are vectors, the dot product is returned

        Raises:
            DimensionError: The vectors were not the same length

        """
        if not isinstance(other, Vector):
            return Vector(*(other * e for e in self))

        if len(self) != len(other):
            raise DimensionError("Vector dimensions don't match")

        return sum(s * o for s, o in zip(self, other))

    __rmul__ = __mul__

    def __eq__(self, other):
        """Check if two vectors are equal by comparing their elements.

        Returns:
            bool: Whether the two vectors have equal elements

        Raises:
            DimensionError: The vectors were not the same length

        """
        if len(self) != len(other):
            raise DimensionError("Vector dimensions don't match")
        return all(s == o for s, o in zip(self, other))

    def __round__(self, ndigits: Optional[int] = None):
        """Return a rounded version of the vector.

        This implements the "round" built-in, which it uses to round each
        element in the vector

        Args:
            ndigits: The number of digits to round to, passed to the round
                built-in

        """
        return Vector(*list(round(e, ndigits) for e in self))

    def __hash__(self):
        """Return a hash of the vector based on the vector elements."""
        return hash(tuple(self))

    def dist(self, other: 'Vector') -> float:
        """Return the Euclidean distance to another vector.

        Note that the distance is naively calculated, and may not be ideal
        for accuracy or performance purposes.

        Returns:
            The Euclidean distance to the other vector

        Raises:
            DimensionError: The vectors were not the same length

        """
        if len(self) != len(other):
            raise DimensionError("Vector dimensions don't match")

        return sqrt(fsum((se - oe)**2 for se, oe in zip(self, other)))

    def isclose(self, other: 'Vector') -> bool:
        """Return whether another vector is close by checking its elements.

        The other vector is considered close if all of its elements are
        considered close to the corresponding element in this vector.
        Closeness is determined with the isclose built-in.

        """
        return all(isclose(se, oe) for se, oe in zip(self, other))

    def unit(self) -> 'Vector':
        """Return the unit vector for this vector.

        The unit vector is the vector in the same direction of this
        vector, but with magnitude 1

        """
        return (1 / abs(self)) * Vector(*self)

    def unit_normal(self) -> 'Vector':
        """Return the unit vector, but rotated 90 degrees counter-clockwise."""
        return self.unit().rotate(-pi / 2)

    def phase(self) -> float:
        """Return the phase of the vector.

        Returns the phase of a vector in radians using atan2. It is only valid
        for 2D vectors.

        Returns:
            The phase of the vector

        Raises:
            DimensionError: The vectors were not the same length

        """
        if len(self) != 2:
            raise DimensionError("Must be a 2d vector")

        return atan2(self.y, self.x)

    def rotate(self,
               phase: float,
               pole: Optional['Vector'] = None) -> 'Vector':
        """Return the vector after rotation by a phase.

        Returns the vector after rotation by phase radians, around the origin
        by default or the given pole if specified.

        This method is only valid for 2D vectors.

        Args:
            phase: The counterclockwise angle of rotation, in radians.
            pole: An optional vector to indicate the center of rotation

        Returns:
            The rotated Vector.

        Raises:
            DimensionError: phase and/or pole are not 2-dimensional
            TypeError: pole is not a vector

        """
        if len(self) != 2:
            raise DimensionError("Only 2D vectors can be rotated")

        if not pole:
            pole = Vector(0, 0)
        elif not isinstance(pole, Vector):
            raise TypeError("Pole must be a vector")
        elif len(pole) != 2:
            raise DimensionError("Pole must be a 2D vector")

        centered_vector = self - pole
        return Vector(
            Vector.polar(1, -phase) * centered_vector,
            Vector.polar(1, pi / 2 - phase) * centered_vector,
        ) + pole


class Line:
    """A simple class representing a line."""
    def __init__(self, start: Vector, end: Vector):
        """Create a directed line segment from start to end.

        Args:
            start: The point indicating the start of the line segment
            end: The point indicating the end of the line segment

        """
        self._start, self._end = start, end

    @property
    def start(self) -> Vector:
        """Return the position vector for the start of the line."""
        return self._start

    @property
    def end(self) -> Vector:
        """Return the position vector for the end of the line."""
        return self._end

    def unit(self) -> Vector:
        """Return a unit vector indicating the direction of the line."""
        return (self.end - self.start).unit()

    def progress(self, fraction: float) -> Vector:
        """Return a position vector to the point fraction t along the line.

        Args:
            fraction: The fraction of the line traversed. Must be between 0
                and 1

        Returns:
            A position vector

        Raises:
            ValueError: fraction wasn't in between 0 and 1

        """
        if fraction < 0 or fraction > 1:
            raise ValueError("fraction must be in between 0 and 1")
        return (1 - fraction) * self.start + fraction * self.end

    def midpoint(self) -> Vector:
        """Return a position vector to the middle of the line."""
        return self.progress(0.5)

    def phase(self) -> float:
        """Return a phase, in radians, indicating the angle of the line."""
        return (self.end - self.start).phase()

    def unit_normal(self) -> Vector:
        """Return a unit vector perpendicular to the line.

        Takes the vector formed by subtracting the end position vector
        from the start position vector, taking its unit vector, and
        rotating it 90 degrees counter-clockwise

        """
        return (self.end - self.start).unit_normal()


class Rectangle():
    """A simple class representing a rectangle.

    Attributes:
        topleft: The top-left corner of the rectangle
        bottomright: The bottom-right corner of the rectangle

    """
    def __init__(self, x0: float, y0: float, x1: float, y1: float):
        """Create a rectangle with the given coordinates.

        The lesser corner is given by x0, y0, and the greater corner by x1, y1.

        Note that x1 > x0 and y1 > y0, despite the fact that x1, y1 is the
        bottom right corner for most graphical applications, including tkinter.
        x0, y0 is the top left corner in this case.

        The lesser/greater terminology are used to distinguish the values
        from their higher/lower visual interpretations.

        Args:
            x0: The lesser horizontal boundary of the bounding box
            y0: The lesser vertical boundary of the bounding box
            x1: The greater horizontal boundary of the bounding box
            y1: The greater vertical boundary of the bounding box

        Raises:
            ValueError: A lesser boundary was not less than a greater boundary

        """
        if x1 < x0 or y1 < y0:
            raise ValueError(
                "x0, y0 must be the lesser corner of the Rectangle")
        self.topleft = Vector(x0, y0)
        self.bottomright = Vector(x1, y1)
        self._fourcoords = (*self.topleft, *self.bottomright)

    @classmethod
    def frompoint(cls, center: Vector, radius: float) -> 'Rectangle':
        """Create a square bounding box from a center point and radius.

        The radius indicates the desired distance from the center of the
        rectangle to its edge

        Args:
            center: The center of the desired bounding box
            radius: The minimal distance from the center to an edge i.e. half
                the width of the square

        Returns:
            A Rectangle object

        """
        topleft = center - radius * Vector(1, 1)
        bottomright = center + radius * Vector(1, 1)
        return cls(*topleft, *bottomright)

    def __repr__(self):
        """Return a string representation of the rectangle."""
        return f'Rectangle({",".join(map(str, self._fourcoords))})'

    def __iter__(self):
        """Iterate over the input coordinates: x0, y0, x1, y1."""
        for coordinate in self._fourcoords:
            yield coordinate

    def __hash__(self):
        """Return a hash of the rectangle based on its four coordinates."""
        return hash(self._fourcoords)

    def __contains__(self, point: Vector) -> bool:
        """Return if a position vector point is inside the Rectangle.

        Points on an edge of the Rectangle are not considered contained.

        Args:
            point: The position vector being tested

        Returns:
            True if the point is inside the rectangle

        Raises:
            ValueError: The point must be two dimensional

        """
        if len(point) != 2:
            raise DimensionError("Argument point is not 2 dimensional")

        if self.topleft.x < point.x < self.bottomright.x:
            if self.topleft.y < point.y < self.bottomright.y:
                return True
        return False

    def midpoint(self) -> Vector:
        """Return the center of the bounding box."""
        return 0.5 * (self.topleft + self.bottomright)
