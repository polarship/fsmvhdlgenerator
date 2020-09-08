"""A decorator scrolled_frame for making tkinter frames with scrollbars."""

import tkinter as tk
from tkinter import ttk


def scrolled_frame(*scroll_dimensions):
    """Class decorator to add scrolling to a regular tkinter widget.

    Accomplishes this by wrapping the widget in a ttk.Frame. The frame needs to
    be accessed via the widget attribute for instantiated objects of the class
    wrapped

    Args:
        *scroll_dimensions: Can contain "v" and/or "h" for vertical and/or
            horizontal scrollbars. If empty, "v" is assumed

    """
    def scrollbar_widget(cls):
        """Create a class encapsulating a widget with scrollbars."""
        class Frame(ttk.Frame):
            """Create a widget with optional scrollbars.

            Attributes:
                widget: the widget defined by the wrapped class
                v_scrollbar: the vertical scrollbar
                h_scrollbar: the horizontal scrollbar

            """
            def __init__(self, master: tk.Widget, *args, **kwargs):
                """Create a frame containing a class and scrollbars."""
                super().__init__(master=master)
                self._widget = cls(*args, master=self, **kwargs)
                self._widget.grid(row=0, column=0, sticky="nwes")
                self.rowconfigure(0, weight=1)
                self.columnconfigure(0, weight=1)
                if not scroll_dimensions or "v" in scroll_dimensions:
                    self.v_scrollbar = ttk.Scrollbar(self, orient="vertical")
                    self.v_scrollbar.grid(row=0, column=1, sticky="ns")
                    self.v_scrollbar['command'] = self._widget.yview
                    self._widget['yscrollcommand'] = self.v_scrollbar.set
                if "h" in scroll_dimensions:
                    self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal")
                    self.h_scrollbar.grid(row=1, column=0, sticky="we")
                    self.h_scrollbar['command'] = self._widget.xview
                    self._widget['xscrollcommand'] = self.h_scrollbar.set

            @property
            def widget(self):
                """Return the encapsulated widget."""
                return self._widget

        return Frame

    return scrollbar_widget
