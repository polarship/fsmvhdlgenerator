"""Contains the classes for drawing transitions on the tkinter canvas.

Classes:
    Transition: A class for drawing transitions between states and storing
        transition source, destination, and condition information
    DefaultTransition: A class for drawing a transition to the default state,
        storing the default.

"""

import logging
from math import pi, radians
from typing import Union

from fsmvhdlgenerator.canvasitems.canvas_entities import (CanvasItem,
                                                          CanvasItemGroup)
from fsmvhdlgenerator.canvasitems.items import Bulb, Condition, Curve
from fsmvhdlgenerator.canvasitems.state import State
from fsmvhdlgenerator.finitestatemachine.transition import AbstractTransition
from fsmvhdlgenerator.mainapplication.config import TRANSITION
from fsmvhdlgenerator.utils.geometry import Line, Vector


class Transition(CanvasItemGroup, AbstractTransition):
    """A Transition drawn on canvas for use in a Moore FSM.

    Extends CanvasItemGroup to unify various contained CanvasItems and
    also extends AbstractTransition to provide transition functionality
    for the MooreFiniteStateMachine

    """
    def __init__(self, source_state: State, destination_state: State):
        """Create a Transition from a source and destination state.

        When a Transition is created, it is drawn on the tkinter canvas
        it is associated with as a CanvasItemGroup.

        Args:
            source_state: The source state of the transition
            destination_state: The destination state of the transition

        """
        self._source, self._destination = source_state, destination_state
        self._arc: Union[Bulb, Curve]

        self.loop_transition = (source_state == destination_state)
        if self.loop_transition:
            logging.info("Creating transition from state to same state")
            logging.info("State  %s", source_state)
            self._arc = Bulb(self.source.circle,
                             pi / 2,
                             angle_offset=radians(15),
                             tags=('transition_arc'),
                             **TRANSITION['arrow'])

        else:
            logging.info("Creating transition between different states")
            logging.info("Source state is %s", self.source)
            logging.info("Destination state is %s", self.destination)
            self._arc = Curve(self.source.circle,
                              self.destination.circle,
                              tags=('transition_arc'),
                              **TRANSITION['arrow'])

        condition_location = self.calc_condition_location()

        self._condition = Condition(default_text="True", width=8)
        self._condition.create_window(*condition_location,
                                      tags=('transition_window'))

        super().__init__([self._arc, self._condition])

    def __hash__(self):
        """Return a hash of the Transition, based on its arc."""
        return hash(self._arc)

    def redraw(self):
        """Update the Curve or Bulb and condition geometry and locations.

        This causes the Transition to re-read the position of its source
        and destination states, recalculate the needed position of its arrow
        and Condition entry fields, and redraw them.

        This generally needs to be called when either the source or destination
        state are moved.

        """
        if self.loop_transition:
            self._arc.redraw(self.source.circle, pi / 2)
        else:
            self._arc.redraw(self.source.circle, self.destination.circle)

        self._condition.coords = self.calc_condition_location()

    def calc_condition_location(self) -> Vector:
        """Calculate the intended location of the condition item.

        Determines the location based on whether the Transition is a
        loop transition and returns it (without actually moving it).

        """
        offset: Vector
        if self.loop_transition:
            offset = Vector.polar(5 * TRANSITION['radius'] / 3, pi / 2)
            location = self.source.center - offset
        else:
            line = Line(self.source.center, self.destination.center)
            offset = (TRANSITION['radius'] / 2) * line.unit_normal()
            location = line.progress(0.4) + offset
        return location

    @property
    def source(self) -> State:
        """Return the source state of the Transition."""
        return self._source

    @property
    def destination(self) -> State:
        """Return the destination state of the Transition."""
        return self._destination

    @property
    def condition(self) -> Condition:
        """Return the condition of the Transition."""
        return self._condition

    @property
    def arc(self):
        """Return the curve or bulb of the Transition's arrow."""
        return self._arc


class DefaultTransition(CanvasItem):
    """A CanvasItem for an arrow drawn on tkinter canvas.

    The arrow points to a default_state, stored internally.

    """
    @property
    def arc(self):
        """Return the canvas_id of the DefaultTransition arrow."""
        return self.canvas_id

    def __init__(self, default_state: State):
        """Create a default transition on the default_state.

        Args:
            default_state: The state on which to create the DefaultTransition

        """
        self._default_state = default_state

        state_center = self._default_state.center
        logging.info("Creating default state transition")
        logging.info("State located at %s", state_center)
        start_point = state_center - Vector(2 * TRANSITION['radius'], 0)
        end_point = state_center - Vector(TRANSITION['radius'], 0)
        super().__init__(
            self.canvas.create_line(*start_point, *end_point,
                                    **TRANSITION['arrow']))
        logging.info("Arc coordinates: %s", self.canvas.coords(self.arc))

    @property
    def default_state(self) -> State:
        """Return the default state."""
        return self._default_state

    def __hash__(self):
        """Return a hash of the DefaultTransition, based on its arc."""
        return hash(self.arc)
