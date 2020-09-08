"""Contains condition classes and functions for finite state machines.

A condition represents a boolean expression and the various operations
that can be performed on it. Conditions are the key component of transitions

Classes:
    ConditionExpressionError: Error for bad expressions
    ConditionConversionError: Error for condition conversion
    AbstractCondition: An abstract boolean condition
    ConditionSet: A container for conditions subclassing AbstractCondition

"""

import itertools
from abc import ABC, abstractmethod
from typing import Any, Iterable, Set, Union

import boolean

from fsmvhdlgenerator.utils.filtered_collections import MonotonicSet


class ConditionExpressionError(ValueError):
    """Condition could not be created due to bad expression."""


class ConditionConversionError(ValueError):
    """Condition could not be converted."""


class AbstractCondition(ABC):
    """An abstract class for describing boolean conditions.

    Subclasses should override the expression property to provide the
    expression object.

    Attributes:
        _algebra: The boolean algebra to which the expression belongs

    """
    _algebra: boolean.BooleanAlgebra = boolean.BooleanAlgebra()

    _operation_list = [
        dict(name='variable', sub='', precedence=0, cls=boolean.Symbol),
        dict(name='literal',
             sub='',
             precedence=0,
             cls=boolean.boolean.BaseElement),
        dict(name='or', sub=' or ', precedence=1, cls=boolean.OR),
        dict(name='and', sub=' and ', precedence=2, cls=boolean.AND),
        dict(name='not', sub='not ', precedence=3, cls=boolean.NOT),
    ]

    def __repr__(self):
        """Return a string representation of the condition."""
        return f"Condition('{self.expression}')"

    @property
    def algebra(self) -> boolean.BooleanAlgebra:
        """Return the algebra used by the condition."""
        return self._algebra

    @classmethod
    def cls_algebra(cls) -> boolean.BooleanAlgebra:
        """Return the algebra used by the condition class."""
        return cls._algebra

    @property
    @abstractmethod
    def expression(self) -> boolean.Expression:
        """(Abstract) Return the expression of the condition."""

    def parse_expression(self, expression: str) -> boolean.Expression:
        """Parse a boolean expression string with the boolean library parser.

        Args:
            expression: The boolean expression to parse

        Returns:
            The parsed expression

        Raises:
            ConditionExpressionError: If the expression can't be parsed

        """
        try:
            parsed_expression = self.algebra.parse(expression)
        except boolean.boolean.ParseError:
            raise ConditionExpressionError(expression)
        else:
            return parsed_expression

    def evaluate(self, **arguments: Union[str, int]) -> boolean.Expression:
        """Evaluate the condition using substitutions into the expression.

        Evaluates the condition from the key-value mapping of **arguments,
        substituting each key with its value in the condition expression

        Args:
            **arguments: keyword arguments are used to directly substitute
                values in the expression condition

        Returns:
            The expression after substitution and simplification

        """
        substitutions = {
            boolean.boolean.Symbol(k): self.algebra.parse(str(v))
            for k, v in arguments.items()
        }
        return self.expression.subs(substitutions, simplify=True)

    @property
    def inputs(self) -> Set[boolean.Symbol]:
        """Return the inputs of the condition."""
        return set(self.expression.symbols)

    @property
    def vhdl(self) -> str:
        """Return the VHDL code for the condition."""
        return self._vhdl()

    def _vhdl(self) -> str:
        """Return an expression to a string representation of VHDL code.

        Args:
            The boolean expression to convert

        Returns:
            The expression as VHDL in a string

        """
        def _convert_r(expression, last_operator_precednce: int) -> str:
            operation = [
                operation for operation in self._operation_list
                if isinstance(expression, operation['cls'])
            ][0]

            if not operation:
                raise ConditionConversionError(
                    f"Couldn't parse expression {expression!r}")

            if operation['name'] in ('or', 'and'):
                subexp = operation['sub'].join([
                    _convert_r(subexp, operation['precedence'])
                    for subexp in expression.args
                ])
                if operation['precedence'] < last_operator_precednce:
                    return f'({subexp})'
                return f'{subexp}'

            if operation['name'] == 'not':
                sym = expression.symbols
                subexp = expression.args[0]
                if len(sym) == 1:
                    return f"{sym.pop()}='0'"

                converted_subexp = _convert_r(subexp, operation['precedence'])
                return f"{operation['sub']}({converted_subexp})"

            if operation['name'] == 'variable':
                return f"{expression}='1'"

            if operation['name'] == 'literal':
                return str(expression.pretty()).lower()
            raise ConditionConversionError(
                f"Couldn't convert expression to VHDL, "
                f"unrecognized operation {operation['name']}")

        return _convert_r(self.expression, 0)


ConditionTypeSet: Any = MonotonicSet(AbstractCondition)


class ConditionSet(ConditionTypeSet):
    """A set that can only contain conditions.

    Has a class variable _algebra shared with the Condition class

    Attributes:
        _algebra: The boolean algebra to which the expression belongs

    """

    _algebra: boolean.BooleanAlgebra = AbstractCondition.cls_algebra()

    @property
    def inputs(self) -> Set[boolean.Symbol]:
        """Return a set of inputs of the ConditionSet.

        The return value is a set union of every condition's input in
        the ConditionSet.

        """
        return set().union(*[condition.inputs for condition in self])

    @property
    def expressions(self) -> Iterable[boolean.Expression]:
        """Return the expressions of the ConditionSet."""
        return (condition.expression for condition in self)

    @property
    def exclusive(self) -> bool:
        """Return whether all conditions are pairwise mutually exclusive.

        Returns:
            Whether no combination of inputs can cause two conditions to be
            true at the same time.

        """
        for exp1, exp2 in itertools.combinations(self.expressions, 2):
            logical_exclusion = self._algebra.dnf(boolean.AND(
                exp1, exp2)).simplify()
            if logical_exclusion != self._algebra.FALSE:
                return False
        return True

    @property
    def exhaustive(self) -> bool:
        """Return whether all conditions are collectively exhaustive.

        Returns:
            Whether any combination of inputs will ensure at least one
            condition is true

        """
        # boolean.OR needs at least two arguments
        logical_coverage = self._algebra.cnf(
            boolean.OR(self._algebra.FALSE, self._algebra.FALSE,
                       *self.expressions)).simplify()
        return bool(logical_coverage == self._algebra.TRUE)
