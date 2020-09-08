"""Contains generic State classes.

Classes:
    OutputsDict: A dict-like container for output assignments
    AbstractState: An abstract state
    StateSet: A container for conditions subclassing AbstractState

"""

from abc import ABC, abstractmethod
from collections import Counter
from functools import reduce
from typing import AbstractSet, Any, TypeVar, cast

from fsmvhdlgenerator.utils.filtered_collections import (FilteredDict,
                                                         MonotonicSet)


class OutputsDict(FilteredDict):
    """A dict-like class for managing the outputs of a state.

    Extends the abstract class FilteredDict, overriding name_filter and
    value_filter to provide filter functions for the names and values
    stored in the dictionary (to guard against improper output names or
    values)

    """
    def name_filter(self, name):
        """Return the filtered name, where the filter is an identity."""
        return name

    def value_filter(self, value):
        """Return the filtered value.

        Raises:
            ValueError: The value wasn't one of 0, '0', False, 1, '1', True, so
                it couldn't be converted to a boolean value

        """
        supported_values = (0, '0', False, 1, '1', True)
        if value not in supported_values:
            raise ValueError("Value {} not in supported values".format(value))
        return int(value)


class AbstractState(ABC):
    """An abstract state class, to represent finite state machine states.

    Subclasses should override the name and outputs property methods.

    """
    def __repr__(self):
        """Return a string representation of the state."""
        return f'State("{self.name}", {self.outputs})'

    # NOQA: See https://github.com/python/mypy/issues/1362
    @property  # type: ignore
    @abstractmethod
    def name(self):
        """(Abstract) Return the state name."""

    @name.setter  # type: ignore
    @abstractmethod
    def name(self, val):
        """(Abstract) Set the state name."""

    @property  # type: ignore
    @abstractmethod
    def outputs(self):
        """(Abstract) Return the state outputs."""

    @outputs.setter  # type: ignore
    @abstractmethod
    def outputs(self, val):
        """(Abstract) Set the state outputs."""

    @property
    def output_identifiers(self):
        """Return the names of the State's outputs."""
        return self.outputs.keys()

    @property
    def default(self) -> bool:
        """Return whether this state is marked as the default state."""
        return self._default

    @default.setter
    def default(self, value: bool):
        """Set whether this state is marked as the default state."""
        self._default = value


StateTypeSet: Any = MonotonicSet(AbstractState)

AS = TypeVar('AS', bound=AbstractState)


class StateSet(AbstractSet[AS], StateTypeSet):
    """A set that can only hold States as entries.

    Note that states do not have to be uniquely named, nor do they have
    to provide all outputs that other states have.

    """
    def __getitem__(self, state_name: str) -> 'StateSet[AS]':
        """Return a StateSet of the state(s) with the name state_name."""
        return StateSet(state for state in self if state_name == state.name)

    def __delitem__(self, state_name: str):
        """Delete state(s) with the name state_name from the StateSet."""
        self = cast('StateSet[AS]', self - self[state_name])

    @property
    def names(self) -> Counter:
        """Return a mapping of each state's name to its count.

        The count returned is the number of states with the given name.

        """
        return self._name_identifiers

    @property
    def outputs(self) -> Counter:
        """Return a mapping of each output's name to its count.

        The count returned is the number of states with the given
        output.

        """
        return self._output_identifiers

    @property
    def _name_identifiers(self) -> Counter:
        return reduce(lambda x, y: x + y,
                      (Counter({state.name: 1}) for state in self), Counter())

    @property
    def _output_identifiers(self) -> Counter:
        return reduce(lambda x, y: x + y,
                      (Counter(state.output_identifiers) for state in self),
                      Counter())

    def is_valid(self) -> bool:
        """Return if each state is uniquely named and isn't missing outputs."""
        outputs = self._output_identifiers

        if [val for val in outputs if outputs[val] != len(outputs)]:
            return False
        if len(self) != len(self._name_identifiers):
            return False
        return True
