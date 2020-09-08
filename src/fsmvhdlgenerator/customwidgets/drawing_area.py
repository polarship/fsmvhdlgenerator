"""Defines the drawing area of the application.

The drawing area of the application is where the finite state machine can be
drawn by the user.

Classes:
    DrawingArea: The area on which users can draw finite state machines

Functions:
    viewport: A decorator for handling canvas events, adjusting for the canvas
        view
    vevent_handler: A decorator for event handlers, wrapping the event into a
        Vector

"""

import logging
import tkinter as tk
from itertools import count
from typing import Callable, Dict, Iterable, Iterator, List, Optional

from fsmvhdlgenerator.canvasitems.items import Circle
from fsmvhdlgenerator.canvasitems.state import State
from fsmvhdlgenerator.canvasitems.transition import (DefaultTransition,
                                                     Transition)
from fsmvhdlgenerator.customwidgets.scrolled_frame import scrolled_frame
from fsmvhdlgenerator.finitestatemachine import hdl
from fsmvhdlgenerator.finitestatemachine.condition import \
    ConditionExpressionError
from fsmvhdlgenerator.finitestatemachine.moore_finite_state_machine import \
    MooreFiniteStateMachine
from fsmvhdlgenerator.finitestatemachine.state import StateSet
from fsmvhdlgenerator.finitestatemachine.transition import TransitionSet
from fsmvhdlgenerator.mainapplication.config import CLICK_HALO, GRID, STATE
from fsmvhdlgenerator.mainapplication.shared import UniversalDict
from fsmvhdlgenerator.utils.coroutine import coroutine
from fsmvhdlgenerator.utils.geometry import Rectangle, Vector


def viewport(handler):
    """Decorator for event handlers, adjusting for the current canvas view."""
    def inner(canvas, event):
        logging.debug("Event yielded: %s", event)
        handler(canvas, Vector(canvas.canvasx(event.x),
                               canvas.canvasy(event.y)))

    return inner


def vevent_handler(func):
    """Takes an event handler and wraps the event coordinates into a vector."""
    def inner(event):
        return func(Vector(event.x, event.y))

    return inner


@scrolled_frame('h', 'v')
class DrawingArea(tk.Canvas):
    """A widget for the creation area for the user's finite state machine.

    Extending the tkinter Canvas widget, this class provides the area for
    graphical creation of the finite state machine as well as the tools for
    operating upon it. As such, it's probably in need of a refactoring :)

    Attributes:
        root: The application root, for spawning dialog boxes
        codetab_setter: A callable for setting code in the CodeTab
        message_setter: A callable for setting a message in the message bar
        region_size: A vector indicating the size of the DrawingArea
        state_names: A generator for creating incremental state names
        gridlines: A dictionary for containing the 'horizontal' and
            'vertical' gridlines displayed on the background
        states: A container for the states created in the application
        transitions: A container for the transitions between states created
            in the application
        default_transition: A DefaultTransition pointing to the default
            state of the application

    """
    def __init__(self, master: tk.Frame, root: tk.Tk, codetab_setter: Callable,
                 message_setter: Callable, region_size: Iterable[int],
                 **kwargs):
        """Create the drawing area, an extension of the tkinter canvas.

        Args:
            master: The parent widget of the underlying tkinter canvas
            root: The top level widget of the application
            codetab_setter: A setter for setting code in the CodeTab
            message_setter: A setter for setting a message in the message
                bar
            region_size: An iterable indicating the size of the drawing area

        """
        super().__init__(master, **kwargs)
        UniversalDict(canvas=self)
        logging.debug("Initiating canvas with root %s", root)
        self.master = master
        self.root: tk.Tk = root
        self.codetab_setter = codetab_setter
        self.message_setter = message_setter
        self.region_size: Vector = Vector(*region_size)
        self.state_names: Iterator[str] = map(str, count())
        self.gridlines: Dict[str, List] = {'horizontal': [], 'vertical': []}
        self.states: StateSet[State] = StateSet()
        self.transitions: TransitionSet[Transition] = TransitionSet()
        self.default_transition: Optional[DefaultTransition] = None

        self.create_grid(spacing=25, limit=self.region_size)
        self.message_setter("Click on a tool to get started")

    @property
    def default_state(self) -> Optional[State]:
        """Return the default state of the finite state machine."""
        if not self.default_transition:
            return None
        return self.default_transition.default_state

    def cursor(self, cursor_name: str):
        """Set the displayed cursor to cursor_name."""
        self.master.config(cursor=cursor_name)

    def create_circle(self, point_x: float, point_y: float, radius: float,
                      **kwargs) -> int:
        """Create a circle on the canvas.

        A wrapper for tkinter.Canvas.create_oval method

        Args:
            point_x: Horizontal location of the center of the circle
            point_y: Vertical location of the center of the circle
            radius: Radius of the circle
            **kwargs: Arguments to pass directly to the create_oval method

        Returns:
            An ID of the item drawn in the tkinter canvas

        """
        return self.create_oval(  # type: ignore
            point_x - radius, point_y - radius, point_x + radius,
            point_y + radius, **kwargs)

    def find_overlapping_withtag(self, tag: str,
                                 search_rectangle: Rectangle) -> List[int]:
        """Find and return items with a tag in a given search area.

        Args:
            tag: The canvas tag by which to filter results
            search_rectangle: An iterable of four points (i.e a Rectangle)
                delimiting the coordinates of the search area

        Returns:
            A list of items found in the search area that have tag
                in the tkinter canvas

        """
        all_items = self.find_overlapping(*search_rectangle)
        return [item for item in all_items if tag in self.gettags(item)]

    def find_closest_state(self, point: Vector) -> Optional[State]:
        """Find the state closest to a point, returning None otherwise.

        Finds the state closest to a point, returning None if no states
        exist.

        Args:
            point: The point to search from

        Returns:
            The state closest to the point, if found (and None otherwise)

        """
        if not self.states:
            return None

        state = min(self.states, key=lambda state: abs(point - state.center))
        return state

    def canvas_vevent(self, vevent: Vector) -> Vector:
        """Return the vevent coordinates shifted by the canvas window."""
        return Vector(self.canvasx(vevent.x), self.canvasy(vevent.y))

    def reset_mouse(self):
        """Reset tools, remove mouse bindings, and delete preview items."""
        logging.info("Unbinding mouse events")
        self.tag_unbind("state", "<Button-1>")
        self.unbind("<Button-1>")
        self.unbind("<Motion>")
        self.delete("preview")
        self.cursor("arrow")
        self.message_setter("Click on a tool to get started")

    def create_state_tool(self):
        """Start the create state tool.

        Clicking will create a state.

        """
        self.reset_mouse()
        self.bind("<Motion>", self._create_and_move_preview_circle_co())
        self.cursor("crosshair")
        self.message_setter("Click anywhere to create a state")

    @coroutine(iteration_decorator=vevent_handler)
    def _create_and_move_preview_circle_co(self):
        """Create and move a preview circle on the drawing area.

        The first iteration over the generator creates the circle, while
        subsequent iterations move the circle to a new position.

        """
        vevent = yield
        vevent = self.canvas_vevent(vevent)
        logging.debug("vevent received: %s", vevent)
        assert isinstance(vevent, Vector)
        circle = Circle(vevent,
                        radius=STATE['radius'],
                        tags=('preview'),
                        **STATE['preview'])
        self.tag_bind("preview", "<Button-1>", self._create_state)
        stored_position = vevent

        while True:
            vevent = yield
            vevent = self.canvas_vevent(vevent)
            circle.move(vevent - stored_position)
            stored_position = vevent

    @viewport
    def _create_state(self, vevent: Vector):
        """Attempt to create a new state on the DrawingArea.

        It will first check to see if any existing states are nearby and
        if so, will send a message to the user via message_setter and exit
        Otherwise, a new state is created.

        Args:
            vevent: Where on the DrawingArea to create the state

        """
        center = vevent
        logging.info("Attempting to create state at %s", center)
        closest_existing_state = self.find_closest_state(center)

        if closest_existing_state:
            distance = abs(closest_existing_state.center - center)
            # Don't create a new state if an existing one is nearby
            if distance < 2.5 * STATE['radius']:
                logging.info("Attempt too close to existing state %s",
                             closest_existing_state)
                self.message_setter("Too close to existing state")
                return

        state = State(center, name=next(self.state_names))
        self.states.add(state)
        self.message_setter("Click anywhere to create a state")

    def move_state_tool(self):
        """Start the move state tool.

        The first click will begin moving the state upon mouse movement,
        and the second click will stop moving the state.

        """
        logging.info("Move state tool called")
        self.reset_mouse()
        self.tag_bind("state", "<Button-1>", self._move_state_selection)
        self.cursor("crosshair")
        self.message_setter("Click on a state to move it")

    @viewport
    def _move_state_selection(self, vevent):
        """Begin moving a state along with mouse movement.

        This method finds the state closest to vevent and binds motion events
        to handler _move_state_co to move that state. It also binds a handler
        for completing the move state operation _move_state_completion.

        Args:
            vevent: The location at which the state to move resides

        """
        target_state = self.find_closest_state(vevent)
        logging.info("Moving target state %s", target_state)
        self.bind("<Motion>", self._move_state_co(target_state))
        self.tag_bind("state", "<Button-1>", self._move_state_completion)
        self.message_setter("Click to place the state here")

    @coroutine(iteration_decorator=vevent_handler)
    def _move_state_co(self, target_state: State):
        """Move the target state and redraw transitions upon each iteration.

        This generator function moves the state, tracking the displacement
        deltas between iterations. It also calls redraw commands on all
        incident transitions on each iteration.

        Args:
            target_state: The state to be moved

        """
        vevent = yield
        vevent = self.canvas_vevent(vevent)
        cursor_offset = target_state.center - vevent
        if abs(cursor_offset) >= STATE['radius']:
            # Prevents cursor from leaving state circle
            cursor_offset = 0.9 * STATE['radius'] * cursor_offset.unit()

        while True:
            vevent = yield
            vevent = self.canvas_vevent(vevent)
            delta = vevent - target_state.center + cursor_offset
            target_state.move(delta)
            for transition in self.transitions.from_states(
                    target_state, target_state, 'or'):
                transition.redraw()
            if self.default_transition:
                if self.default_transition.default_state == target_state:
                    self.default_transition.move(delta)

    @viewport
    def _move_state_completion(self, _):
        """Finish the move state operation.

        Removes intermediary bindings and prepares for a new move state
        operation.

        """
        self.unbind("<Motion>")
        self.tag_unbind("state", "<Button-1>")
        self.tag_bind("state", "<Button-1>", self._move_state_selection)
        self.cursor("crosshair")
        self.message_setter("Click on a state to move it")

    def delete_state_tool(self):
        """Start the delete state tool.

        Clicking on a state will delete it and all connected
        transitions.

        """
        logging.info("Delete state tool called")
        self.reset_mouse()
        self.tag_bind("state", "<Button-1>", self._delete_state)
        self.cursor("crosshair")
        self.message_setter("Click on a state to delete it")

    @viewport
    def _delete_state(self, vevent: Vector):
        """Delete the state at a given location.

        This method finds the state closest to vevent and deletes it. It
        also deletes any incident transitions upon it, including the default
        transition, if any.

        This callback should be assigned only to events on the state objects,
        or else clicking on empty space may delete the state as well.

        Args:
            vevent: The location at which the state to delete resides

        """
        target_state = self.find_closest_state(vevent)

        if not target_state:
            return

        if target_state.default and self.default_transition:
            self.default_transition.delete()
            self.default_transition = None
        incident_transitions = self.transitions.from_states(
            target_state, target_state, 'or')
        for transition in incident_transitions:
            self.transitions.discard(transition)
            transition.delete()
        self.states.discard(target_state)
        target_state.delete()

    def create_transition_tool(self):
        """Start the create transition tool.

        The first click on a state sets the source state, and the second
        click selects the destination state and draws the arrow.

        """
        self.reset_mouse()
        logging.info("Creating transition between states")
        self.tag_bind("state", "<Button-1>", self._create_transition_co())
        self.cursor("crosshair")

    @coroutine(end_behavior='refresh', iteration_decorator=vevent_handler)
    def _create_transition_co(self):
        """Create a transition across two generator iterations.

        This generator function creates a transition from the position
        sent in the first generation to the position send in the second
        generation, if both were states. If a transition already exists,
        nothing will happen. Loop transitions with the same destination
        as the source are also supported.

        """
        state = {}
        for endpoint in ('source', 'destination'):
            self.message_setter(f"Click on the {endpoint} state")
            vevent = yield
            vevent = self.canvas_vevent(vevent)
            logging.info("Finding transition's %s state", endpoint)
            state[endpoint] = self.find_closest_state(vevent)
            logging.info("Transition %s selected", state[endpoint])

        if self.transitions.from_states(state['source'], state['destination']):
            logging.info("Transition between states already exists")
        else:
            transition = Transition(state['source'], state['destination'])
            self.transitions.add(transition)

    def delete_transition_tool(self):
        """Start the delete transition tool.

        Clicking on or near a transition will delete it.

        """
        logging.info("Delete transition tool called")
        self.reset_mouse()
        self.bind("<Button-1>", self._delete_transition)
        self.cursor("crosshair")
        self.message_setter("Click on a transition to delete it")

    @viewport
    def _delete_transition(self, vevent: Vector):
        """Delete the transition located at a given position.

        This method tries to find the transition closest to vevent and deletes
        it. Transitions are thin curved arrows, however, so a constrained
        search halo is used to lessen the need for the user's precision.

        Args:
            vevent: The location at which the transition to delete resides or
                is near to

        """
        logging.info("Finding transition at %s for deletion", vevent)
        search_area = Rectangle.frompoint(vevent, CLICK_HALO)
        transition_items = self.find_overlapping_withtag(
            'transition_arc', search_area)
        transitions = [
            t for t in self.transitions if t.arc.canvas_id in transition_items
        ]
        if transitions:
            logging.info("Deleting transition %s", transitions[0])
            self.transitions.discard(transitions[0])
            transitions[0].delete()

    def set_default_state_tool(self):
        """Start the tool to set the default state."""
        self.reset_mouse()
        logging.info("Setting default state")
        self.tag_bind("state", "<Button-1>", self._set_default_state)
        self.cursor("crosshair")
        self.message_setter("Click on a state to make it the default state")

    @viewport
    def _set_default_state(self, vevent: Vector):
        """Internally set the default state and draw the default transition.

        This method draws and stores the default transition for a state at
        vevent.

        Args:
            vevent: The location at which the state to move resides

        """
        new_default_state = self.find_closest_state(vevent)

        if not new_default_state:
            return

        for state in self.states:
            if state.default and self.default_transition:
                logging.info("Changing default state from %s", state)
                self.default_transition.default_state.default = False
                self.default_transition.delete()
                self.default_transition = None
                break

        logging.info("Setting default state to %s", new_default_state)
        self.default_transition = DefaultTransition(new_default_state)
        new_default_state.default = True

    def generate_vhdl_tool(self):
        """Generate VHDL for the finite state machine."""
        return self.generate_vhdl()

    def generate_vhdl_testbench_tool(self):
        """Generate VHDL for a testbench of the finite state machine."""
        return self.generate_vhdl(testbench=True)

    def generate_vhdl(self, testbench: bool = False):
        """Process states and transitions into VHDL and set code in CodeTab.

        This tool, when called, creates a MooreFiniteStateMachine with the
        drawn states and transitions, generates the VHDL code, and sends
        it to code tab with codetab_setters

        Args:
            testbench: Whether to generate a testbench for the finite state
                machine instead

        Raises:
            ConditionExpressionError: A condition could not be successfully
                parsed

        """
        self.reset_mouse()

        machine = MooreFiniteStateMachine(self.states, self.transitions)
        if self.default_state:
            machine.add_state(self.default_state, default=True)
        try:
            vhdl_code = hdl.render_moore_finite_state_machine_vhdl(
                machine,
                name='MooreFSM',
                testbench=testbench,
            )
        except ConditionExpressionError as exc:
            logging.info("Invalid condition detected")
            self.message_setter(
                f'Error: Condition "{str(exc.args[0]).strip()}" is invalid. '
                f'Valid operators are: !, &, |. '
                f'Valid literals are: True, False')
        else:
            self.codetab_setter(vhdl_code)

    def create_grid(self, spacing: int, limit: Vector):
        """Create the grid on the canvas.

        The grid is purely aesthetic.

        Args:
            spacing: how far apart the gridlines should be
            limit: the greater horizontal and vertical limits of
                the desired gridlines

        """
        for x_offset in range(0, limit[0], spacing):
            vertical_line = self.create_line(x_offset,
                                             0,
                                             x_offset,
                                             limit.y,
                                             tags=('gridline'),
                                             **GRID)
            self.gridlines['vertical'].append(vertical_line)

        for y_offset in range(0, limit[1], spacing):
            horizontal_line = self.create_line(0,
                                               y_offset,
                                               limit.x,
                                               y_offset,
                                               tags=('gridline'),
                                               **GRID)
            self.gridlines['horizontal'].append(horizontal_line)
