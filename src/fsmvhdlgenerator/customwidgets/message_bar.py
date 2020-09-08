"""Contains a MessageBar for holding a single line of text."""

import tkinter as tk
from tkinter import ttk


class MessageBar(ttk.Frame):
    """A message bar, extending ttk.Frame.

    This frame is intended to store a message on a single line of text.

    """
    def __init__(self, master: tk.Widget, **kwargs):
        """Create a MessageBar.

        Args:
            master: The master of the widget
            **kwargs: Passed to super().__init__

        """
        super().__init__(master, **kwargs)
        self._message = tk.StringVar()
        self.label = ttk.Label(master=self, textvariable=self._message)
        self.label.grid(row=0, column=0)

    @property
    def message(self):
        """Return the message bar contents."""
        return self._message.get()

    @message.setter
    def message(self, value: str):
        """Set the message bar contents."""
        self._message.set(value)

    def message_setter(self, value: str, **label_kwargs):
        """Set the message bar with the value and configuration options.

        Args:
            value: The value to set the message bar to
            label_kwargs: Passes to ttk.Label().configure

        """
        self.message = value
        self.label.configure(**label_kwargs)
