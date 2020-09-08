"""Contains the State class for drawing states on the tkinter canvas."""

import logging
import tkinter as tk
from typing import Any, Dict

from fsmvhdlgenerator.canvasitems.canvas_entities import CanvasItemGroup
from fsmvhdlgenerator.canvasitems.items import (Button, Circle, Entry,
                                                OutputsView)
from fsmvhdlgenerator.customwidgets.outputs_prompt import OutputsPrompt
from fsmvhdlgenerator.finitestatemachine.state import AbstractState
from fsmvhdlgenerator.mainapplication.config import STATE
from fsmvhdlgenerator.utils.geometry import Vector


class State(CanvasItemGroup, AbstractState):
    """A State drawn on a tkinter canvas for use in MooreFiniteStateMachine.

    Extends CanvasItemGroup to unify various contained CanvasItems and also
    extends AbstractState to provide state functionality for the
    MooreFiniteStateMachine.

    Attributes:
        circle: The Circle drawn on the tkinter Canvas.

    """
    def __init__(self, center: Vector, name: str = '', default: bool = False):
        """Create a State.

        When a State is created, it is drawn on the tkinter canvas it is
        associated with as a CanvasItemGroup.

        Args:
            center: The location on the canvas to create the State
            name: The initial name of the State
            default: Whether this State is the default state

        """
        super().__init__()
        logging.info("Creating state at: %s", center)

        self._output_view = None
        self._output_store: Dict[str, str] = {}

        logging.info("Creating state located at %s", center)
        self.circle = Circle(center,
                             radius=STATE['radius'],
                             tags=('state', 'circle'),
                             **STATE['normal'])
        self.add(self.circle)

        self._name = Entry(default_text="state" + name, width=8)
        self._name.create_window(*self.center,
                                 tags=('state', 'name', 'window'))
        self.add(self._name)

        self._button = Button(text='Outputs',
                              command=OutputsPrompt.opener(
                                  self.center + Vector(-200, 125),
                                  self,
                              ))
        self._button.create_window(*self.center + Vector(0, 20))
        self.add(self._button)

        self.default = default

    def __hash__(self):
        """Return a hash of the State, based on its circle CanvasItem."""
        return hash(self.circle)

    @property
    def name(self) -> str:
        """Return the name of the state."""
        return self._name.text

    @property
    def outputs(self) -> Dict[Any, Any]:
        """Return the State outputs as a mapping of names to values."""
        return self._output_store

    @outputs.setter
    def outputs(self, output_store):
        """Set the State's displayed outputs.

        Creates a new OutputsView to display the new outputs, discarding the
        old outputs.

        Args:
            output_store: A mappable of output names to their values

        """
        self._output_store = output_store
        if self._output_view:
            self.discard(self._output_view)
        self._output_view = OutputsView(self._output_store)
        self._output_view.create_window(
            *(self.center + Vector(0, STATE['radius'] + 5)), anchor=tk.N)
        self.add(self._output_view)

    @property
    def center(self) -> Vector:
        """Return the center of the State's circle."""
        return self.circle.center
