"""Contains a Toolbar class, for holding a row of buttons."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, List, Tuple


class Toolbar(ttk.Frame):
    """A container frame for a row of buttons.

    Extends ttk.Frame to provide a horizontal list of buttons, suitable
    for creating common toolbars.

    """
    def __init__(self,
                 master: tk.BaseWidget,
                 text_callback_items: Iterable[Tuple[str, Callable]] = (),
                 **kwargs):
        """Create a Toolbar with the given buttons.

        Args:
            master: The master of the widget
            text_callback_items: An iterable of tuples, where each tuple is a
                text, callback pair corresponding to the text and callback to
                create for the button
            **kwargs: Passed to super().__init__

        """
        super().__init__(master, **kwargs)
        self._buttons: List[ttk.Button] = []
        for text, callback in text_callback_items:
            self.create_button(text, callback)

    def create_button(self, text: str, callback: Callable):
        """Create a button in the toolbar.

        Args:
            text: The text displayed on the button
            callback: A function callback to call when the button is clicked

        """
        button = ttk.Button(self, text=text, command=callback)
        button.grid(row=0, column=len(self._buttons) + 1, padx=2, pady=4)
        self._buttons.append(button)

    @property
    def buttons(self):
        """Return the list of contained buttons."""
        return self._buttons
