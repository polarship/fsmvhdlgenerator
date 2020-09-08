"""A collection of basic classes for working with the tkinter Canvas.

The tkinter.Canvas class interacts with items on a strictly imperative
basis, assigning each of it's displayed items a canvas ID. These classes
intend to encapsulate these items in objects and collections of their
own.

"""

import tkinter as tk
from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional

from fsmvhdlgenerator.mainapplication.shared import UniversalDict
from fsmvhdlgenerator.utils.filtered_collections import MonotonicSet
from fsmvhdlgenerator.utils.geometry import Vector


class CanvasItem:
    """A single item registered on the tkinter Canvas.

    A CanvasItem is any single item on the canvas with its own specific
    canvas ID.

    """
    def __init__(self, canvas_id: Optional[int] = None):
        """Initialize a CanvasItem, optionally providing the canvas_id.

        Args:
            canvas_id: The canvas ID of the item being initialized

        """
        self._canvas_id = canvas_id
        super().__init__()

    @property
    def canvas(self):
        """Return the associated tkinter Canvas."""
        return UniversalDict()['canvas']

    @property
    def canvas_id(self) -> Optional[int]:
        """Return the canvas ID of the CanvasItem."""
        return self._canvas_id

    def __hash__(self):
        """Return a hash of the CanvasItem based on its canvas ID."""
        return hash(self.canvas_id)

    def __eq__(self, other):
        """Return True if two CanvasItems are equal.

        Two CanvasItems are equal if their canvas_ids are the same.

        Returns:
            If the canvas IDs of both CanvasItems are the same

        """
        return self.canvas_id == other.canvas_id

    def move(self, delta: Vector):
        """Move the CanvasItem by a given displacement delta.

        This is a wrapper for tkinter's Canvas.move method.

        Args:
            delta: The displacement vector for moving the item

        """
        self.canvas.move(self.canvas_id, *delta)

    def config(self, *args, **kwargs):
        """Configure the CanvasItem with tkinter's canvas.itemconfig.

        This is a wrapper for tkinter's Canvas.itemconfig method.

        Args:
            *args: Passed to self.canvas.itemconfig
            **kwargs: Passed to self.canvas.itemconfig

        """
        self.canvas.itemconfig(self.canvas_id, *args, **kwargs)

    @property
    def coords(self) -> Iterable[float]:
        """Return an iterable of the canvas coordinates of CanvasItem.

        This is a wrapper for tkinter's Canvas.coords method.

        """
        return self.canvas.coords(self.canvas_id)  # type: ignore

    @coords.setter
    def coords(self, coords: Iterable[float]):
        """Set the coordinates of the CanvasItem.

        This is a wrapper for tkinter's Canvas.coords method.

        Args:
            coords: An iterable of the coordinates of the items, as arguments
            to the tkinter Canvas.coords method

        """
        self.canvas.coords(self.canvas_id, *coords)

    def delete(self):
        """Delete this CanvasItem from the canvas.

        This is a wrapper for tkinter's Canvas.delete method.

        """
        self.canvas.delete(self.canvas_id)


CanvasItemTypeSet: Any = MonotonicSet(CanvasItem)


class CanvasItemGroup(CanvasItemTypeSet):
    """A set of unique CanvasItems on a canvas.

    A CanvasItemGroup is a collection of unique canvas items, with
    various convenience methods from CanvasItem broadcasted to all of
    the CanvasItems that it contains.

    """
    def move(self, delta: Vector):
        """Move each CanvasItem by a displacement delta."""
        for item in self:
            item.move(delta)

    def delete(self):
        """Delete every CanvasItem in CanvasItemGroup from the canvas.

        Calls CanvasItem.delete(delta) for each contained CanvasItem,
        and then empties the container.

        """
        for item in self:
            item.delete()
        super().clear()

    def discard(self, value: CanvasItem):
        """Delete a single CanvasItem from the CanvasItemGroup.

        Calls item.delete() on the item, and then removes it from the
        container. If the item is not present in the CanvasItemGroup, no
        action is taken.

        Args:
            value: The item on the canvas to delete

        """
        value.delete()
        super().discard(value)


class CanvasWidget(ABC, CanvasItem):
    """An abstract widget item placed on the tkinter canvas in a window.

    Tkinter widgets can be placed on the canvas using a window. This class
    encapsulates this behavior. On the canvas, the widget is the item with a
    canvas ID.

    Subclasses should override the widget property

    """
    @property
    @abstractmethod
    def widget(self) -> tk.Widget:
        """(Abstract) Return the tkinter widget."""

    @property
    def window(self) -> Optional[int]:
        """Return the canvas ID of the window of the CanvasWidget."""
        return self.canvas_id

    def create_window(self, *args, **kwargs):
        """Create a window to display the CanvasWidget on the canvas.

        Args:
            *args: Passed to tkinter's Canvas.create_window method
            **kwargs: Passed to tkinter's Canvas.create_window method

        """
        self._canvas_id = self.canvas.create_window(*args,
                                                    window=self.widget,
                                                    **kwargs)

    def delete(self):
        """Destroy CanvasWidget and delete it from the tkinter Canvas."""
        self.widget.destroy()
        super().delete()
