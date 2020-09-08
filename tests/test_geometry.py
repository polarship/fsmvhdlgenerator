"""Tests for the Vector class."""

from math import pi

import pytest

from fsmvhdlgenerator.utils.geometry import Line, Vector


class TestVector:
    """Test the Vector class."""
    def test_create(self):
        """Test Vector creation from its elements."""
        vec = Vector(3, 7)
        assert vec.x == 3 and vec.y == 7

    def test_polar_create(self):
        """Test Vector creation from polar coordinates."""
        assert abs(Vector.polar(1, pi / 2) - Vector(0, 1)) < 0.001

    def test_repr(self):
        """Test Vector representation."""
        assert repr(Vector(1, 2, 3)) == 'Vector(1, 2, 3)'

    def test_str(self):
        """Test Vector user-friendly representation."""
        assert str(Vector(1, 2, 3)) == '<1, 2, 3>'

    def test_iter(self):
        """Test Vector iteration."""
        ite = iter(Vector(1, 2, 3))
        assert next(ite) == 1
        assert next(ite) == 2
        assert next(ite) == 3

    def test_len(self):
        """Test Vector length."""
        assert len(Vector(1, 2, 3, 4)) == 4

    def test_abs(self):
        """Test Vector magnitude."""
        return abs(Vector(3, -4)) == 5

    def test_eq(self):
        """Test Vector equality."""
        assert Vector(1, 2) == Vector(1, 2)
        assert not Vector(1, 3) == Vector(1, 2)

    def test_add(self):
        """Test Vector addition."""
        with pytest.raises(ValueError):
            _ = Vector(1, 2) + Vector(3, 4, 5)
        assert Vector(1, -2) + Vector(-3, 4) == Vector(-2, 2)
        assert Vector(2, 3) + 1 == Vector(3, 4)
        assert 1 + Vector(2, 3) == Vector(3, 4)

    def test_neg(self):
        """Test Vector negation."""
        assert -Vector(2, 3) == Vector(-2, -3)

    def test_sub(self):
        """Test Vector subtraction."""
        assert Vector(1, 2) - Vector(1, 2) == Vector(0, 0)
        assert Vector(1, 2) - 1 == Vector(0, 1)
        assert 1 - Vector(1, 2) == Vector(0, -1)

    def test_mul(self):
        """Test Vector scaler multiplication and the dot product."""
        assert Vector(1, 2) * 5 == Vector(5, 10)
        assert 5 * Vector(1, 2) == Vector(5, 10)
        assert Vector(3, 2) * Vector(1, 2) == 7

    def test_round(self):
        """Test element-wise rounding of Vector."""
        assert round(Vector(1.1, 2.1)) == Vector(1, 2)

    def test_hash(self):
        """Test hashing of the Vector by its elements."""
        assert hash(tuple(Vector(1, 2)._elems)) == hash(Vector(1, 2))

    def test_dist(self):
        """Test Euclidean distance to another Vector."""
        assert Vector(0, -4).dist(Vector(0, 4)) == 8
        assert Vector(-4, 0).dist(Vector(4, 0)) == 8

    def test_isclose(self):
        """Test Vector element-wise proximity."""
        assert Vector(0, 1).isclose(Vector(0, 0.9999999999999))

    def test_unit(self):
        """Test creation of a unit vector from Vector."""
        assert Vector(2, 0).unit() == Vector(1, 0)

    def test_rotate(self):
        """Test rotation of Vector."""
        test_vector1 = Vector(1, 0).rotate(pi / 2)
        assert test_vector1.dist(Vector(0, 1)) < 0.001
        test_vector2 = Vector(2, 1).rotate(pi / 2, Vector(1, 1))
        assert test_vector2.dist(Vector(1, 2)) < 0.001


class TestLine:
    """Test the Line class."""
    def test_create(self):
        """Test creation of a Line."""
        line = Line(Vector(1, 2), Vector(2, 2))
        assert line
        assert line.start == Vector(1, 2)
        assert line.end == Vector(2, 2)

    def test_unit(self):
        """Test the creation of a unit vector for the Line."""
        line = Line(Vector(1, 2), Vector(3, 2))
        assert line.unit() == Vector(1, 0)

    def test_progress(self):
        """Test a position vector created from along the Line."""
        line = Line(Vector(1, 1), Vector(3, 3))
        assert line.progress(0.5) == Vector(2, 2)

    def test_midpoint(self):
        """Test position vector to the middle of the Line."""
        assert Line(Vector(1, 1), Vector(3, 3)).progress(0.5) == Vector(2, 2)

    def test_phase(self):
        """Test the phase method of the line."""
        assert Line(Vector(0, 1), Vector(0, 3)).phase() == pi / 2
