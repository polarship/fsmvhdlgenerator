"""Contains Transition classes.

Classes:
    UnreachableState: Error for states that aren't destinations
    UnexitableState: Error for states that aren't sources
    AbstractTransition: An abstract transition between states
    TransitionSet: A container for conditions subclassing AbstractTransition

"""

from abc import ABC, abstractmethod
from typing import AbstractSet, Any, Optional, TypeVar, Union, cast

from fsmvhdlgenerator.finitestatemachine.condition import (AbstractCondition,
                                                           ConditionSet)
from fsmvhdlgenerator.finitestatemachine.state import AbstractState, StateSet
from fsmvhdlgenerator.utils.filtered_collections import MonotonicSet


class UnreachableState(Exception):
    """Indicates a state is not the destination of any transition."""


class UnexitableState(Exception):
    """Indicates a state is not the source of any transition."""


class AbstractTransition(ABC):
    """An abstract class for transition properties and methods.

    Subclasses should override the source, destination, and condition
    property methods.

    """
    def __repr__(self):
        """Return a string representation of the transition."""
        repr_str = (f"Transition({self.source}, {self.destination}, "
                    f"{self.condition})")
        return repr_str

    @property
    @abstractmethod
    def source(self) -> AbstractState:
        """(Abstract) Return the source state."""

    @property
    @abstractmethod
    def destination(self) -> AbstractState:
        """(Abstract) Return the destination state."""

    @property
    @abstractmethod
    def condition(self) -> AbstractCondition:
        """(Abstract) Return the condition for the transition traversal."""

    def parallels(self, other: 'AbstractTransition'):
        """Return if two transitions share source and destination states."""
        sources_match = self.source == other.source
        destinations_match = self.destination == other.destination
        return sources_match and destinations_match


TransitionTypeSet: Any = MonotonicSet(AbstractTransition)

AT = TypeVar('AT', bound=AbstractTransition)


class TransitionSet(AbstractSet[AT], TransitionTypeSet):
    """A set that can only hold Transitions as entries.

    Note that two transitions may have the same source and destination
    state.

    """
    @property
    def sources(self) -> StateSet:
        """Return all source states."""
        return StateSet(transition.source for transition in self)

    @property
    def destinations(self) -> StateSet:
        """Return all destination states."""
        return StateSet(transition.destination for transition in self)

    @property
    def conditions(self) -> ConditionSet:
        """Return a new ConditionSet with all conditions of all transitions."""
        return ConditionSet(transition.condition for transition in self)

    def from_states(self,
                    source: Optional[AbstractState] = None,
                    destination: Optional[AbstractState] = None,
                    mode: str = 'and') -> 'TransitionSet[AT]':
        """Return a new TransitionSet based on the transitions' states.

        Create a new TransitionSet containing only the transitions with a
        given source and/or destination set and return it.

        Args:
            source: The source state that desired transitions should have
            destination: The destination state that desired transitions should
                have
            mode: Takes a value of 'or' or 'and'. When either no source or
                no transition is specified, it has no effect.
                - 'and' (default): Return only the transitions with both the
                    specified source (if any) and destination (if any)
                - 'or': Return the transitions that either have the specified
                    source (if any) or the destination (if any) or both

        Raises:
            ValueError: The mode was neither 'and' nor 'or'

        """
        source_transitions: TransitionSet = TransitionSet()
        destination_transitions: TransitionSet = TransitionSet()
        for transition in self:
            if source and transition.source == source:
                source_transitions.add(transition)
            if destination and transition.destination == destination:
                destination_transitions.add(transition)

        if mode == 'and' and source and destination:
            return cast('TransitionSet[AT]',
                        source_transitions & destination_transitions)
        if mode == 'or' or not source or not destination:
            return cast('TransitionSet[AT]',
                        source_transitions | destination_transitions)
        raise ValueError('Mode must be "and" or "or"')

    def evaluate(self, **arguments: Union[str, int]) -> 'TransitionSet':
        """Return a new TransitionSet based on the arguments.

        Return a new TransitionSet with only the transitions whose conditions
        are true given the arguments

        Args:
            arguments: A mapping of argument names to be substituted to the
                values that substitute them

        """
        return TransitionSet(transition for transition in self
                             if transition.condition.evaluate(**arguments))

    def is_exclusive(self) -> bool:
        """Return the pairwise mutual exclusivity of transition conditions.

        The pairwise mutual exclusivity is determined by whether two
        transition conditions from the same state can be true for the
        same input.

        """
        return self.conditions.exclusive

    def is_exhaustive(self) -> bool:
        """Return whether a transition condition will be true for any input."""
        return self.conditions.exhaustive

    def check_reachability(self) -> bool:
        """Return whether every state is the source and destination of a state.

        If a transition has the same state as its source and destination,
        this criteria is automatically true for that state.

        Note that it's possible the states are still segmented into two
        connected groups.

        Returns:
            If every state is the source and destination of at least one state

        Raises:
            UnreachableState: A state wasn't reachable (it wasn't a
                destination state for any transition)
            UnexitableState: A state wasn't exitable (it wasn't a source
                state for any transition)

        """
        unreachable_states = self.sources - self.destinations
        unexitable_states = self.destinations - self.sources
        if unreachable_states:
            raise UnreachableState(
                f"States {unreachable_states} are not reachable")

        if unexitable_states:
            raise UnexitableState(
                f"States {unexitable_states} are not exitable")

        return True
