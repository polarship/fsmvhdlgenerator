"""Defines the classes used for creating the CodeTab side panel.

The side panel of the application contains tabbed interfaces, one of which
is CodeTab, dedicated to the HDL generation of the app.

Note that all widget-based classes needs to be displayed using a geometry
manager in its parent frame. In short, they don't display themselves.

Classes:
    CodeTab: The frame with all code-related functions
    CodeText: The widget containing the code itself, as text

"""

import logging
import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pygments.lexers as pyglexers
import pygments.styles as pygstyles

from fsmvhdlgenerator.customwidgets.scrolled_frame import scrolled_frame
from fsmvhdlgenerator.customwidgets.toolbar import Toolbar


class CodeTab(ttk.Frame):
    """A container class extending ttk.Frame for displaying VHDL code.

    The CodeTab is the frame nested on the side panel of the application. It
    contains the toolbar for the interacting with the code as well as the code
    itself.

    Attributes:
        filepath: Class attribute for storing the last saved location for the
            code file
        code_toolbar: A widget with buttons for interacting with code_text
        code_text: contains the code text generated from the application

    """

    filepath = None

    def __init__(self, master: tk.Widget, drawing_area, **kwargs):
        """Create the CodeTab.

        Create the CodeTab, including the related toolbar of buttons for the
        various tools as well as the CodeText

        Args:
            master: The master widget of the CodeTab
            drawing_area: The DrawingArea with code generation abilities
            **kwargs: Passed directly to super().__init__

        """
        super().__init__(master, **kwargs)
        self.code_toolbar: Toolbar = Toolbar(
            master=self,
            text_callback_items=[
                ('Generate VHDL', drawing_area.generate_vhdl_tool),
                ('Generate VHDL Testbench',
                 drawing_area.generate_vhdl_testbench_tool),
                ('Save as VHDL file', self.save_code_to_file),
                ('Copy to clipboard', self.copy_code_to_clipboard_tool),
            ])
        self.code_toolbar.grid(row=0, column=0)
        self.code_text: CodeText = CodeText(master=self,
                                            width=40,
                                            state='disabled',
                                            wrap='none')
        self.code_text.grid(row=1, column=0, sticky="nwes")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.text = "*** Generated VHDL will appear here ***"

    @property
    def text(self) -> str:
        """Return the text inside the code_text."""
        return str(self.code_text.widget.text)  # type: ignore

    @text.setter
    def text(self, input_text: str):
        """Set the text inside the code_text.

        Args:
            input_text: The text to set the code text area with

        """
        self.code_text.widget.text = input_text  # type: ignore

    def save_code_to_file(self):
        """Open a system file dialog box prompt to save the code to a file."""
        saved_filepath = filedialog.asksaveasfilename(
            title="Select destination VHDL file",
            filetypes=(("VHDL files", "*.vhd"), ("all files", "*.*")),
            initialfile=getattr(self.filepath, 'name', 'MooreFSM'),
            initialdir=getattr(self.filepath, 'parent', pathlib.Path.home()))
        if saved_filepath:
            with open(saved_filepath, mode='w') as file:
                file.write(self.text)
            self.filepath = pathlib.Path(saved_filepath)
            messagebox.showinfo(title='File saved successfully',
                                message=f'VHDL code saved to {saved_filepath}')
            logging.info("Saving filename for next save: %s", self.filepath)
            logging.debug("Filename has type: %s", type(self.filepath))

    def copy_code_to_clipboard_tool(self):
        """Set the clipboard contents to the text inside code_text."""
        self.clipboard_clear()
        self.clipboard_append(self.text)


@scrolled_frame('h', 'v')
class CodeText(tk.Text):
    """An area for displaying the VHDL code, extending the tk.Text widget.

    Extends tkinter's tk.Text to provide a widget that can display VHDL code
    with syntax highlighting.

    Scrollbars are provided via a class decorator. Note that after
    instantiation, CodeText must be accessed with the "widget" attribute due to
    the behavior of scrolled_frame, i.e. CodeText().widget.text.

    """
    def __init__(self, master: tk.Widget, **kwargs):
        """Create a CodeText widget for displaying code.

        Args:
            master: The master of the CodeText widget
            **kwargs: Passed to super().__init__

        """
        super().__init__(master, **kwargs)
        self._configure_syntax_highlighting()

    @property
    def text(self):
        """Return the displayed text."""
        return self.get("1.0", "end")

    @text.setter
    def text(self, input_text: str):
        """Set the displayed text.

        The CodeText text is cleared and replaced with input_string,
        automatically providing VHDL syntax highlighting.

        Args:
            input_text: The text for code text to display

        """
        self['state'] = "normal"
        self.delete("1.0", "end")
        for token, content in pyglexers.VhdlLexer().get_tokens(input_text):
            self.insert("end", content, str(token))
        self['state'] = "disabled"

    def _configure_syntax_highlighting(self, style: str = 'default'):
        """Configure text area with syntax highlighting.

        Syntax highlighting is prepared by assigning each VHDL token type to a
        tag in CodeText, and coloring that tag with the color given from the
        the token's style in pygments.

        Args:
            style: Name of the pygments library style

        """
        for token, token_style in pygstyles.get_style_by_name(style):
            if token_style['color']:  # Some tokens lack color
                self.tag_configure(str(token),
                                   foreground=f'#{token_style["color"]}')
