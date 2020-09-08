"""Collection of fixtures for tests."""

import sys
sys.path.append('./src/')

import pytest

from fsmvhdlgenerator.finitestatemachine.moore_finite_state_machine import \
    MooreFiniteStateMachine
from test_condition import Condition
from test_state import State
from test_transition import Transition


@pytest.fixture
def sample_states():
    """Return some sample states.

    Each state is named ``stateN``, where N is a number 0 to 9.

    Each state has two outputs, div2, and div4, which correspond to whether
    N is divisible by 2 or 4, respectively.

    """
    states = [
        State('state' + str(n), {
            'div2': int((n % 2) == 0),
            'div4': int((n % 4) == 0)
        }) for n in range(10)
    ]
    return states


@pytest.fixture
def complete_fsm():
    """Return a complete Moore finite state machine."""
    fsm = MooreFiniteStateMachine()
    state0 = State(name='s0', outputs=dict(u=0, v=0))
    state1 = State(name='s1', outputs=dict(u=1, v=0))
    fsm.add_state(state0, default=True)
    fsm.add_state(state1)
    fsm.add_transition(Transition(state0, state0, Condition('x')))
    fsm.add_transition(Transition(state0, state1, Condition('~x')))
    fsm.add_transition(Transition(state1, state0, Condition('x&~y')))
    fsm.add_transition(Transition(state1, state1, Condition('~x|y')))
    return fsm
