"""Contains generic finite state machine(s).

Classes:
    MooreFiniteStateMachine: A Moore finite state machine

"""
from collections import Counter
from typing import Iterable, Optional, Set

import boolean

from fsmvhdlgenerator.finitestatemachine.state import AbstractState, StateSet
from fsmvhdlgenerator.finitestatemachine.transition import (AbstractTransition,
                                                            TransitionSet)


class MooreFiniteStateMachine():
    """A Moore finite state machine.

    Encapsulates the behavior and contents of a Moore finite state
    machine. States and Transitions should extend AbstractState and
    AbstractTransition from the finitestatemachine.state and
    finitestatemachine.transition modules respectively.

    """
    def __init__(self,
                 states: Iterable[AbstractState] = tuple(),
                 transitions: Iterable[AbstractTransition] = tuple()):
        """Create a Moore finite state machine (FSM).

        Arguments:
            states: an iterable of existing States
            transitions: an iterable of existing Transitions

        """
        self._states: StateSet = StateSet(states)
        self._transitions: TransitionSet = TransitionSet(transitions)
        self._default: Optional[AbstractState] = None

    @property
    def states(self) -> StateSet:
        """Return the states of the FSM."""
        return self._states

    @property
    def transitions(self) -> TransitionSet:
        """Return the transitions of the FSM."""
        return self._transitions

    @property
    def default_state(self) -> Optional[AbstractState]:
        """Return the default state of the FSM."""
        return self._default

    @property
    def inputs(self) -> Set[boolean.Symbol]:
        """Return the inputs of the FSM.

        Returns:
            The inputs of the finite state machine

        """
        return self._transitions.conditions.inputs

    @property
    def outputs(self) -> Counter:
        """Return the outputs of the FSM and how often they occur.

        Returns:
            A mapping of the outputs of the FSM, with each output name mapped
            to the number of states containing that output

        """
        return self._states.outputs

    def add_state(self, state: AbstractState, default: bool = False):
        """Add an existing state to the FSM.

        Args:
            state: the state to add
            default: if the state is the default state

        """
        self._states.add(state)
        if default:
            self._default = state
            state.default = True

    def get_state(self, name) -> StateSet:
        """Get states of the FSM based on their name.

        States may have the same name, so the StateSet returned may have more
        than one item.

        An empty StateSet is returned if no states have the given name.

        Returns:
            The state(s) matching the given name

        """
        return self._states[name]

    def add_transition(self, transition: AbstractTransition):
        """Adds an existing transition to the FSM.

        Note that two transitions may have the same source and destination
        states. As long as they are different objects, they will be added
        nonetheless.

        Args:
            transition: the transition to add

        """
        self._transitions.add(transition)
