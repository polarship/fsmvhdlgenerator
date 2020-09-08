"""Tests for the State module."""

import sys

import pytest

from fsmvhdlgenerator.finitestatemachine.state import (AbstractState,
                                                       OutputsDict, StateSet)

sys.path.append('./src/')


class State(AbstractState):
    """An example implementation of a State."""
    def __init__(self, name, outputs=None):
        """Create a state with the given name and outputs."""
        self.name = name
        self.outputs = outputs if outputs else {}

    @property
    def name(self):
        """Return the state name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set the state name."""
        self._name = self.identifier(value)

    @property
    def outputs(self):
        """Return the the state outputs."""
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        """Set the state outputs."""
        self._outputs = OutputsDict(**outputs)

    @classmethod
    def identifier(cls, value):
        """Filter the value for creating the state name."""
        if not isinstance(value, str):
            raise TypeError(f"{value} can't be a state name")
        return value


class TestState:
    """Test a basic State class implementation."""
    def test_create_state(self):
        """Test state creation."""
        state1 = State('state1', {'x': 1, 'y': 0})
        assert state1.name == 'state1'
        assert state1.outputs['x'] == 1
        assert state1.outputs['y'] == 0

    def test_edit_state(self):
        """Test editing of a state name."""
        state1 = State('state1', {'x': 0, 'y': 1})
        state1.name = 'valid_name'
        with pytest.raises(TypeError):
            state1.name = [1, 2]

    def test_hash(self):
        """Test hashing of a state."""
        state1 = State('state1', {'x': 0, 'y': 1})
        hash(state1)
        assert True


class TestStateSet:
    """Tests for the StateSet container."""
    def test_create(self, sample_states):
        """Test creation of a StateSet."""
        states = StateSet(sample_states)
        for state in states['state2']:
            assert state.outputs['div2'] == 1

    def test_add(self):
        """Test adding a state to a StateSet."""
        states = StateSet()
        states.add(State('s0', {'x': 1}))
        assert True

    def test_get_state_by_name(self, sample_states):
        """Test getting state(s) from a StateSet by name."""
        states = StateSet(sample_states)
        for state in states['state3']:
            assert state.name == 'state3'

    def test_outputs(self):
        """Test the counting of StateSet's states' output identifiers."""
        states = StateSet([
            State('s0', dict(x=1, y=0)),
            State('s1', {'x': 0}),
            State('s2', {'x': 1}),
        ])
        assert states.outputs['x'] == 3  # three states had an "x" output
        assert states.outputs['y'] == 1  # only one state had a "y" output

    def test_names(self):
        """Test the counting of StateSet's states' name identifiers."""
        states = StateSet([
            State('s0', dict(x=1, y=0)),
            State('s1', {'x': 0}),
            State('s1', {'x': 1}),
        ])
        assert states.names['s0'] == 1  # one state was named "s0"
        assert states.names['s1'] == 2  # two states were named "s1"

    def test_empty(self):
        """Test properties of an empty StateSet."""
        states = StateSet([])
        assert states.names == {}
        assert states.outputs == {}
