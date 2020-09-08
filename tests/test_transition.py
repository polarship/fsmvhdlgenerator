"""Tests for the Transition module."""

from fsmvhdlgenerator.finitestatemachine.condition import AbstractCondition
from fsmvhdlgenerator.finitestatemachine.state import AbstractState
from fsmvhdlgenerator.finitestatemachine.transition import (AbstractTransition,
                                                            TransitionSet)
from test_condition import Condition
from test_state import State


class Transition(AbstractTransition):
    """An example implementation of a Transition."""
    @staticmethod
    def _state_filter(state):
        if not isinstance(state, AbstractState):
            raise TypeError("Argument {} is not a state".format(state))
        return state

    @staticmethod
    def _condition_filter(condition):
        if not isinstance(condition, AbstractCondition):
            raise TypeError("Argument {} is not a condition".format(condition))
        return condition

    def __init__(self, source, destination, condition):
        """Create a transition from source to destination upon condition."""
        self.source = source
        self.destination = destination
        self.condition = condition

    @property
    def source(self):
        """Return the source state."""
        return self._source

    @source.setter
    def source(self, source_state):
        """Set the source state."""
        self._source = self._state_filter(source_state)

    @property
    def destination(self):
        """Return the destination state."""
        return self._destination

    @destination.setter
    def destination(self, destination_state):
        """Set the destination state."""
        self._destination = self._state_filter(destination_state)

    @property
    def condition(self):
        """Return the transition condition."""
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Set the transition condition."""
        self._condition = self._condition_filter(condition)


class TestTransition():
    """Test a basic Transition class implementation."""
    def test_create(self):
        """Test transition creation."""
        state0 = State('s0', dict(u=1))
        state1 = State('s1', dict(u=0))
        cond = Condition('x')
        Transition(state0, state1, cond)
        assert True

    def test_properties(self):
        """Test transition properties."""
        state0 = State('s0', dict(u=1))
        state1 = State('s1', dict(u=0))
        cond = Condition('x | y')
        transition = Transition(state0, state1, cond)
        assert transition.source == state0
        assert transition.destination == state1
        assert transition.condition == cond


class TestTransitionSet():
    """Tests the TransitionSet container."""
    def test_create(self):
        """Test creation of a TransitionSet."""
        state0 = State('s0', dict(u=1))
        state1 = State('s1', dict(u=0))
        state2 = State('s2', dict(u=0))
        transition1 = Transition(state0, state1, Condition('x | ~y'))
        transition2 = Transition(state0, state2, Condition('~x & y'))
        transitions = TransitionSet([transition1, transition2])
        assert transitions

    def test_get_transitions(self):
        """Test filtering of TransitionSet by states."""
        state0 = State('s0', dict(u=1))
        state1 = State('s1', dict(u=0))
        state2 = State('s2', dict(u=0))
        trans1 = Transition(state0, state1, Condition('x | ~y'))
        trans2 = Transition(state0, state2, Condition('~x & y'))
        trans3 = Transition(state2, state0, Condition('~x & y'))
        trans4 = Transition(state2, state2, Condition('x | ~y'))
        transitions = TransitionSet([trans1, trans2, trans3, trans4])
        transitions_1_to_3 = TransitionSet([trans1, trans2, trans3])
        assert transitions.from_states(state0) == TransitionSet(
            [trans1, trans2])
        assert transitions.from_states(state0,
                                       state2) == TransitionSet([trans2])
        assert transitions.from_states(state0, state0,
                                       mode='or') == transitions_1_to_3
        assert transitions.from_states(state2,
                                       state2) == TransitionSet([trans4])
        assert transitions.from_states(state1, state2) == TransitionSet()

    def test_evaluate(self):
        """Test filtering of TransitionSet by input testing."""
        state0 = State('s0', dict(u=1))
        state1 = State('s1', dict(u=0))
        state2 = State('s2', dict(u=0))
        trans1 = Transition(state0, state1, Condition('x | ~y'))
        trans2 = Transition(state0, state2, Condition('~x & y'))
        transitions = TransitionSet([trans1, trans2])
        assert transitions.evaluate(x=1, y=0) == TransitionSet([trans1])
        assert transitions.evaluate(x=1) == TransitionSet([trans1])
        assert transitions.evaluate(x=0, y=1) == TransitionSet([trans2])
        trans2.condition = Condition('~x & ~y')
        assert transitions.evaluate(x=0,
                                    y=0) == TransitionSet([trans1, trans2])
        assert transitions.evaluate(x=0, y=1) == TransitionSet()

    def test_exclusive(self):
        """Test mutually exclusive transitions."""
        state0 = State('s0', dict(u=1))
        state1 = State('s1', dict(u=0))
        state2 = State('s2', dict(u=0))
        trans1 = Transition(state0, state1, Condition('x'))
        trans2 = Transition(state0, state2, Condition('~x & y'))
        transitions = TransitionSet([trans1, trans2])
        assert transitions.is_exclusive()
        trans2.condition = Condition('x & y')
        assert not transitions.is_exclusive()

    def test_exhaustive(self):
        """Test collectively exhaustive transitions."""
        state0 = State('s0', dict(u=1))
        state1 = State('s1', dict(u=0))
        state2 = State('s2', dict(u=0))
        trans1 = Transition(state0, state1, Condition('x | ~y'))
        trans2 = Transition(state0, state2, Condition('~x & y'))
        transitions = TransitionSet([trans1, trans2])
        assert transitions.is_exhaustive()
        trans1.condition = Condition('x')
        assert not transitions.is_exhaustive()

    def test_check_reachability(self):
        """Test that all states are in a transition cycle."""
        state0 = State('s0', dict(u=1))
        state1 = State('s1', dict(u=0))
        state2 = State('s2', dict(u=0))
        trans1 = Transition(state0, state1, Condition('x | ~y'))
        trans2 = Transition(state0, state2, Condition('~x & y'))
        trans3 = Transition(state1, state2, Condition('~x'))
        trans4 = Transition(state2, state0, Condition('y'))
        transitions = TransitionSet([trans1, trans2, trans3, trans4])
        assert transitions.check_reachability()
