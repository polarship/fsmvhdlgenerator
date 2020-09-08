"""A collection of specific items drawn on the the tkinter canvas.

The tkinter.Canvas class interacts with items on a strictly imperative
basis, assigning each of it's displayed items a canvas ID. These classes
intend to encapsulate these items in classes of their own.

"""

import logging
import tkinter as tk
from itertools import chain
from math import pi, radians
from tkinter import ttk
from typing import Any, Dict, Tuple

from fsmvhdlgenerator.canvasitems.canvas_entities import (CanvasItem,
                                                          CanvasWidget)
from fsmvhdlgenerator.finitestatemachine.condition import AbstractCondition
from fsmvhdlgenerator.utils.geometry import Line, Rectangle, Vector


class Circle(CanvasItem):
    """A circle drawn on a tkinter canvas, extending CanvasItem.

    Wraps tkinter's Canvas.create_oval method to create a circle on the
    canvas

    """
    def __init__(self, center: Vector, radius: float, **kwargs):
        """Initialize and draw the circle on the canvas.

        Additional arguments can be passed to the tkinter canvas's
        create_oval method.

        Args:
            center: The center of the Circle to be drawn
            radius: The radius of the Circle to be drawn
            **kwargs: Passed to tkinter.Canvas.create_oval

        """
        logging.debug("Creating circle at center %s with radius %s", center,
                      radius)
        super().__init__(canvas_id=self.canvas.create_oval(
            *(center - radius), *(center + radius), **kwargs))
        self._radius = radius

    @property
    def center(self) -> Vector:
        """Return the center of the circle as a canvas coordinate."""
        return Rectangle(*self.coords).midpoint()

    @property
    def radius(self) -> float:
        """Return the radius of the circle."""
        return self._radius

    def point(self, phase: float) -> Vector:
        """Return a point on the circle with an angle phase.

        Returns:
            The point on the circle such that it's angle to the polar axis is
                phase

        """
        return self.center + Vector.polar(self.radius, phase)

    def color(self, color: str):
        """Set the color of the Circle's outline.

        Sets the color using the tkinter.Canvas.config method.

        Args:
            color: The desired 24-bit color, formatted '#RRGGBB'

        """
        super().config(outline=color)


class Bulb(CanvasItem):
    """A five point "Bulb" curved arrow for drawing loop transitions of states.

    A loop transition is a transition from a state to itself. This curve
    is implemented as a spline curve calculated from five points

    """
    def __init__(self,
                 reference_circle: Circle,
                 center_angle: float,
                 angle_offset: float = radians(15),
                 **kwargs):
        """Create a Bulb in relation to a reference circle.

        As it is intended to be created when touching a circle, the creation of
        the Bulb is done in reference to a reference circle,

        The Bulb has two endpoints touching the reference circle. Their
        location is determined by first taking the point on the reference
        circle located at center_angle from the pole of the circle (the
        positive horizontal ray starting at the center). This point is then
        used as the center to find the endpoints, which are two points on the
        reference circle, each with an angular distance to the aforementioned
        point of angle_offset, but in opposite directions.

        Args:
            reference_circle: The reference circle for creating the Bulb
            center_angle: The angle of the line of symmetry for the Bulb,
                which passes through center
            angle_offset: The angular offset from the line of symmetry
                along the reference circle for the two bulb endpoints
            **kwargs: Passed to self.canvas.create_line

        """
        points = self.calculate_points(reference_circle, center_angle,
                                       angle_offset)
        super().__init__(canvas_id=self.canvas.create_line(
            *chain(*points), smooth=True, **kwargs))

    def redraw(self,
               reference_circle: Circle,
               center_angle: float,
               angle_offset: float = radians(15)):
        """Recreate the Bulb with new geometry settings.

        See the __init__ method for the argument information.

        """
        points = self.calculate_points(reference_circle, center_angle,
                                       angle_offset)
        self.coords = chain(*points)

    @classmethod
    def calculate_points(
            cls, reference_circle: Circle, center_angle: float,
            angle_offset: float
    ) -> Tuple[Vector, Vector, Vector, Vector, Vector]:
        """Calculate spline points for the Bulb.

        See the __init__ method for the argument information.

        Returns:
            The five points needed to plot the Bulb

        """
        point_1, point_2 = cls.calculate_endpoints_from_center(
            reference_circle, center_angle, angle_offset)
        return cls.calculate_bulb_points_from_endpoints(
            point_1, point_2, scale=reference_circle.radius * 4 / 3)

    @staticmethod
    def calculate_endpoints_from_center(
            reference_circle: Circle, center_angle: float,
            angle_offset: float) -> Tuple[Vector, Vector]:
        """Calculate endpoints on the reference circle.

        See the __init__ method for the argument information.

        Returns:
            The two points on the reference circle

        """
        # Angles negated to compensate for downward y-axis
        center_angle, angle_offset = -center_angle, -angle_offset
        point_1 = reference_circle.point(center_angle + angle_offset)
        point_2 = reference_circle.point(center_angle - angle_offset)
        return point_1, point_2

    @staticmethod
    def calculate_bulb_points_from_endpoints(
            point_a: Vector, point_b: Vector,
            scale: float) -> Tuple[Vector, Vector, Vector, Vector, Vector]:
        """Calculate the spline points of the Bulb from its endpoints.

        The spline points consists of five points:
        - Two endpoints point_a and point_b, which also form a hypothetical
        line segment A-B
        - Two points point_a2 and point_b2 on an axis parallel to A-B,
        forming a hypothetical line segment A2-B2
        - A fifth point point_ab on the perpendicular bisector of A-B and
        A2-B2

        Some other local variables are defined here as well as they help
        form the Bulb shape.

        Locals:
            midband_offset: the inter axis-distance between A-B and A2-B2
            width: the "half-width" of the bulb, it is half the length of A2-B2
            midband_middle: is the midpoint of A2-B2
            scale: the distance between midband_middle and point_ab

        midband_offset and width are set to look nice; they're not
        mathematically necessary

        Args:
            point_a: The start endpoint of the Bulb
            point_b: The end endpoint of the Bulb
            scale: The size of the Bulb. Mathematically, it's the distance
                between the midpoint of A2-B2 and point_AB

        Returns:
            The five points for drawing the spline curve, in the order below:
                point_a, point_a2, point_ab, point_b2, point_b

        """
        midband_offset = scale / 3
        width = 2 * scale / 3
        line = Line(point_a, point_b)
        midband_middle = midband_offset * line.unit_normal()
        point_a2 = line.midpoint() + midband_middle - width * line.unit()
        point_ab = line.midpoint() + scale * line.unit_normal()
        point_b2 = line.midpoint() + midband_middle + width * line.unit()
        return point_a, point_a2, point_ab, point_b2, point_b


class Curve(CanvasItem):
    """A curved arrow for drawing transitions between states.

    This curve is implemented as a spline curve calculated from three
    points.

    """
    def __init__(self,
                 reference_circle1: Circle,
                 reference_circle2: Circle,
                 angle_offset: float = radians(15),
                 **kwargs):
        """Create a Curve in relation to two reference circles.

        The two centers of the reference circles form a hypothetical line
        segment c1-c2 that will be used for drawing the curve.

        The point on the edge of the first reference circle, such that it
        forms an angle of angle_offset from the line c1-c2, will be the
        start endpoint of the curve.

        The second endpoint will be similar, however the orientation is
        different in order to keep both points on the same side of c1-c2.

        Args:
            reference_circle1: The start reference circle
            reference_circle2: The end reference circle
            angle_offset: The angular offset from the line c1-c2 along the
                reference circle for the two Curve endpoints
            **kwargs: Passed to self.canvas.create_line

        """
        points = self.calculate_points(reference_circle1, reference_circle2,
                                       angle_offset)
        super().__init__(canvas_id=self.canvas.create_line(
            *chain(*points), smooth=True, **kwargs))

    def redraw(self,
               reference_circle1: Circle,
               reference_circle2: Circle,
               angle_offset: float = radians(15)):
        """Recreate the Curve with new geometry settings.

        See the __init__ method for the argument information.

        """
        points = self.calculate_points(reference_circle1, reference_circle2,
                                       angle_offset)
        self.coords = chain(*points)

    @classmethod
    def calculate_points(cls, reference_circle1: Circle,
                         reference_circle2: Circle,
                         angle_offset: float) -> Tuple[Vector, Vector, Vector]:
        """Calculate spline points for the Curve.

        See the __init__ method for the argument information.

        Returns:
            The three points needed to plot the Curve

        """
        point_1, point_2 = cls.calculate_endpoints_from_centers(
            reference_circle1, reference_circle2, angle_offset)
        return cls.calculate_spline_points_from_endpoints(point_1, point_2)

    @staticmethod
    def calculate_endpoints_from_centers(
            reference_circle1: Circle, reference_circle2: Circle,
            angle_offset: float) -> Tuple[Vector, Vector]:
        """Calculate endpoints on the reference circles.

        See the __init__ method for the argument information.

        Returns:
            The two points on the reference circle

        """
        axis_angle = Line(reference_circle1.center,
                          reference_circle2.center).phase()
        angle_offset = -angle_offset  # Negated for downward y-axis
        point_1 = reference_circle1.point(axis_angle + angle_offset)
        point_2 = reference_circle2.point(axis_angle - angle_offset + pi)
        return point_1, point_2

    @staticmethod
    def calculate_spline_points_from_endpoints(
            point_a: Vector,
            point_b: Vector,
            offset: float = 15) -> Tuple[Vector, Vector, Vector]:
        """Calculate the three spline points of the Curve from its endpoints.

        Three spline points are calculated, with the third point determined
        from the perpendicular bisecting line formed by point_a and point_b.
        This perpendicular bisector has the length offset

        Args:
            point_a: The start endpoint of the Curve
            point_b: The end endpoint of the Curve
            offset: The magnitude of the perpendicular bisector determining
                the location of the third spline point

        Returns:
            The three points of the spline curve

        """
        line = Line(point_a, point_b)
        point_m = line.midpoint() + offset * line.unit_normal()
        return point_a, point_m, point_b


class Entry(CanvasWidget):
    """A text entry field suitable for placement on a tkinter Canvas.

    This class extends CanvasWidget, overriding the widget property
    method. The user can input text on the Entry drawn on the tkinter
    Canvas. Entry provides a text property for easily accessing the
    widget's text.

    """
    def __init__(self, default_text: str = '', **kwargs):
        """Create an Entry, for user text input on the tkinter Canvas.

        Args:
            default_text: The text to insert into the entry upon creation
            **kwargs: Passed to ttk.Entry.__init__

        """
        self._text = tk.StringVar()
        self._widget = ttk.Entry(master=self.canvas,
                                 textvariable=self._text,
                                 **kwargs)
        self._widget.insert(0, default_text)
        super().__init__()

    @property
    def text(self) -> str:
        """Return the text inside the widget."""
        return str(self._text.get())

    @property
    def widget(self) -> ttk.Entry:
        """Return the Entry widget object."""
        return self._widget


class Condition(Entry, AbstractCondition):
    """A boolean Condition for placement on the tkinter Canvas.

    Condition extends Entry to provide the text input interface and
    AbstractCondition to provide all of the different Finite State
    Machine logic.

    """
    @property
    def expression(self):
        """Return the Entry text parsed as a boolean expression."""
        return super().parse_expression(self.text)


class Button(CanvasWidget):
    """A button suitable for placement on a tkinter Canvas.

    This class extends CanvasWidget, overriding the widget property
    method tor to return the Button.

    """
    def __init__(self, *args, **kwargs):
        """Create a button on the tkinter canvas.

        Args:
            *args: Passed as arguments to ttk.Button
            **kwargs: Passed as arguments to ttk.Button

        """
        self._widget: ttk.Button = ttk.Button(master=self.canvas,
                                              *args,
                                              **kwargs)
        super().__init__()

    @property
    def widget(self) -> ttk.Button:
        """Return the button widget."""
        return self._widget


class OutputsView(CanvasWidget):
    """An CanvasWidget to graphically display the output=value pairs.

    OutputsView extends CanvasWidget, overriding the widget property
    method to return the tkinter frame containing a vertical list of
    tkinter Labels, each label containing an "output_name=value" string.

    """
    def __init__(self, outputs: Dict[Any, Any]):
        """Create an OutputsView to display output information.

        Args:
            outputs: A mapping of output names and values

        """
        self._widget = ttk.Frame(master=self.canvas)
        super().__init__()
        outputs_labels = []
        for idx, (name, value) in enumerate(outputs.items()):
            output = f"{name} = {value}"
            outputs_labels.append(ttk.Label(master=self.widget, text=output))
            outputs_labels[-1].grid(row=idx, column=0)

    @property
    def widget(self) -> ttk.Frame:
        """Return the OutputsView tkinter frame widget."""
        return self._widget
