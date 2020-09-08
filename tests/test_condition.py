"""Tests for the Condition module."""

import boolean
import pytest

from fsmvhdlgenerator.finitestatemachine.condition import (
    AbstractCondition, ConditionExpressionError, ConditionSet)


@pytest.fixture(name='sample_conditions')
def fixture_sample_conditions():
    """Return some sample conditions."""
    conditions = [Condition('x | y'), Condition('x & y')]
    return conditions


@pytest.fixture(name='exclusive_conditions')
def fixture_exclusive_conditions():
    """Return conditions which are mutually exclusive."""
    conditions = [Condition('x'), Condition('~x & y')]
    return conditions


@pytest.fixture(name='exhaustive_conditions')
def fixture_exhaustive_conditions():
    """Return conditions which are collectively exhaustive."""
    conditions = [
        Condition('x | y'),
        Condition('~x'),
        Condition('~y'),
    ]
    return conditions


test_conversion_data = [
    ("True", 'true'),
    ("False", 'false'),
    ("x", "x='1'"),
    ("x|y|z", "x='1' or y='1' or z='1'"),
    ("x&y&z", "x='1' and y='1' and z='1'"),
    ("x&(y|z)", "x='1' and (y='1' or z='1')"),
    ("x|(y&z)", "x='1' or y='1' and z='1'"),
    ("x&(y|~z)", "x='1' and (y='1' or z='0')"),
    ("~x|(y&z)", "x='0' or y='1' and z='1'"),
    ("(x&y)|(x&~y)", "x='1' and y='1' or x='1' and y='0'"),
    ("(x|y)&(x|~y)", "(x='1' or y='1') and (x='1' or y='0')"),
]

test_conversion_improper_data = [
    ('TRUE*5', "true and 5='1'"),
    ('FALSE*5', "false and 5='1'"),
]


class Condition(AbstractCondition):
    """An example implementation of Abstract Condition."""
    def __init__(self, expression):
        """Create a Condition from a string boolean expression."""
        self._expression = super().parse_expression(expression)

    @property
    def expression(self):
        """Return the expression of the condition."""
        return self._expression


@pytest.mark.parametrize("condition,output", test_conversion_data)
def test_convert_condition_to_string(condition, output):
    """Test conversions of conditions to their VHDL equivalents."""
    cond = Condition(condition)
    assert cond.vhdl == output


@pytest.mark.parametrize("condition,output", test_conversion_improper_data)
def test_convert_bad_condition_to_string(condition, output):
    """Test proper handling of arbitrary input strings."""
    cond = Condition(condition)
    assert cond.vhdl == output


class TestCondition():
    """Test a basic Condition implementation."""
    def test_create(self):
        """Test creation of the condition."""
        condition = Condition('x | y')
        assert condition

    def test_create_empty(self):
        """Test proper error handling for creating empty conditions."""
        with pytest.raises(ConditionExpressionError):
            Condition('')
        assert True

    def test_inputs(self):
        """Test inference of literal names from an expression."""
        condition = Condition('x & y | z')
        assert {str(i) for i in condition.inputs} == {'x', 'y', 'z'}

    def test_true(self):
        """Test handling of true literals."""
        condition = Condition('TRUE')
        assert condition.inputs == set()
        assert condition.vhdl == 'true'
        assert condition.evaluate(x=0, z=1) == condition.algebra.TRUE

    def test_false(self):
        """Test handling of false literals."""
        condition = Condition('FALSE')
        assert condition.inputs == set()
        assert condition.vhdl == 'false'
        assert condition.evaluate(x=0, z=1) == condition.algebra.FALSE

    def test_evaluate(self):
        """Test condition evaluation."""
        condition = Condition('x & y | z')
        assert condition.evaluate(x=0, z=0) == condition.algebra.FALSE
        assert condition.evaluate(x=0, z=1) == condition.algebra.TRUE

    def test_and(self):
        """Test handling of conjunctions of expression conditions."""
        condition1 = Condition('x & ~y')
        condition2 = Condition('~x | y')
        assert boolean.AND(
            condition1.expression,
            condition2.expression).simplify() != condition1.algebra.FALSE

    def test_or(self):
        """Test handling of disjunctions of expression conditions."""
        condition1 = Condition('x & ~y')
        condition2 = Condition('~x | y')
        assert boolean.OR(
            condition1.expression,
            condition2.expression).simplify() != condition1.algebra.TRUE


class TestConditionSet():
    """Test the ConditionSet container."""
    def test_create(self, sample_conditions, exclusive_conditions,
                    exhaustive_conditions):
        """Test the creation of ConditionSet."""
        conditions = ConditionSet(sample_conditions)
        conditions = ConditionSet(exclusive_conditions)
        conditions = ConditionSet(exhaustive_conditions)
        assert conditions

    def test_inputs(self, sample_conditions):
        """Test the inference of literals from a ConditionSet."""
        conditions = ConditionSet(sample_conditions)
        assert {str(i) for i in conditions.inputs} == {'x', 'y'}

    def test_expressions(self, sample_conditions):
        """Test the collection of expressions of a ConditionSet."""
        conditions = ConditionSet(sample_conditions)
        for expression in conditions.expressions:
            assert isinstance(expression, boolean.boolean.Expression)

    def test_exclusive(self, exclusive_conditions, exhaustive_conditions):
        """Test the exclusive property of ConditionSet."""
        assert ConditionSet(exclusive_conditions).exclusive
        assert not ConditionSet(exhaustive_conditions).exclusive
        assert ConditionSet([Condition('FALSE')]).exclusive
        assert ConditionSet().exclusive

    def test_exhaustive(self, exclusive_conditions, exhaustive_conditions):
        """Test the exhaustive property of ConditionSet."""
        assert not ConditionSet(exclusive_conditions).exhaustive
        assert ConditionSet(exhaustive_conditions).exhaustive
        assert ConditionSet([Condition('TRUE')]).exhaustive
        assert not ConditionSet().exhaustive
