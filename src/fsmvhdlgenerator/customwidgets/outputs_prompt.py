"""Module for components for the Outputs Prompt dialog.

The Outputs Prompt dialog box pops up to allow a user to specify the outputs
of a state.

Classes:
    UniqueOutputNamesError: Error for repeated output names
    EmptyOutputNameError: Error for empty output names
    OutputsPrompt: A tkinter Toplevel window
    OutputsPromptBody: The body of the dialog box
    OutputEntries: The rows of OutputEntrys as well as an add button
    OutputEntry: A single row for an Output name and value

"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import (TYPE_CHECKING, Callable, Dict, Iterable, List, Optional,
                    Tuple)

from fsmvhdlgenerator.customwidgets.toolbar import Toolbar
from fsmvhdlgenerator.mainapplication.shared import UniversalDict
from fsmvhdlgenerator.utils.geometry import Vector

if TYPE_CHECKING:
    from fsmvhdlgenerator.canvasitems.state import State


class UniqueOutputNamesError(ValueError):
    """Exception for unique output names."""


class EmptyOutputNameError(ValueError):
    """Exception for empty output names."""


class OutputsPrompt(tk.Toplevel):
    """A dialog box for setting the outputs of a state.

    Creates an OutputsPrompt dialog box extended from tkinter's Toplevel
    object

    Attributes:
        root: The top level widget of the application
        state: The canvasitems.state.State containing the outputs being edited
        root_location: the location of the root of the application
        body: the contents of the dialog box
        message: the user message below the body, not created until set_message
            is called
        confirmation_toolbar: the toolbar of buttons to try to close the dialog
            box, "Ok" and "Cancel"

    """
    @classmethod
    def opener(cls, location, state: 'State') -> Callable:
        """Return a callback to open an output prompt dialog box.

        Args:
            location: where to open the OutputsPrompt relative to the root
                window
            state: the state of the outputs

        Returns:
            A function that, when called, creates and opens an modal
            window OutputsPrompt

        """
        def inner():
            logging.info("Opening outputs prompt")
            outputs_prompt = cls(location, state)
            return outputs_prompt

        return inner

    def __init__(self, location, state, title: str = "Outputs editor"):
        """Create an OutputsPrompt dialog box.

        Upon creation, the dialog box assumes control of all mouse and keyboard
        events, gets keyboard focus, and prepares confirmation buttons.

        Args:
            location: Where to open the OutputsPrompt relative to the root
                window
            state: The canvasitems.state.State of the outputs
            title: The title of the dialog box

        """
        root = UniversalDict()['root']
        super().__init__(root)
        self.root: tk.Tk = root
        self.state = state
        self.root_location: Vector = Vector(root.winfo_rootx(),
                                            root.winfo_rooty())
        self.transient(root)
        self.title(title)
        self.grab_set()  # Capture all mouse and keyboard events
        self.focus_set()  # Get keyboard focus
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % tuple(location + self.root_location))
        self.body: ttk.Frame = OutputsPromptBody(
            master=self, initial_outputs=self.state.outputs)
        self.body.grid(row=0, column=0)
        self.body.focus_set()
        self.message: Optional[ttk.Label] = None
        self.confirmation_toolbar = Toolbar(master=self,
                                            text_callback_items=[
                                                ('Ok', self.okay),
                                                ('Cancel', self.cancel)
                                            ])
        self.confirmation_toolbar.grid(row=2, column=0)

        self.wait_window()

    def okay(self, _event=None):
        """Try to set the state outputs and closes the dialog if successful."""
        try:
            self.validate()
        except UniqueOutputNamesError:
            self.body.focus_set()  # put focus back
            self.set_message("Error: Output names must be unique")
            return
        except EmptyOutputNameError:
            self.body.focus_set()  # put focus back
            self.set_message("Error: Output names can't be empty")
            return

        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def set_message(self, text: str):
        """Set a message for the user in the dialog box.

        Can be called multiple times to update the message

        """
        if not self.message:
            self.message = ttk.Label(master=self)
            self.message.grid(row=1, column=0)
            self.confirmation_toolbar.grid(row=2, column=0)
        self.message["text"] = text

    def cancel(self):
        """Abort setting the outputs and close the dialog box."""
        self.master.focus_set()
        self.destroy()

    def validate(self):
        """Check that the outputs the user is trying to submit are valid."""
        if self.body.outputs:
            names, _values = zip(*self.body.outputs)
            if len(names) != len(set(names)):
                raise UniqueOutputNamesError("An output can only appear once")
            if any(len(name) == 0 for name in names):
                raise EmptyOutputNameError("Each output must have a name")
        return True

    def apply(self):
        """Store outputs after successful completion of outputs dialog."""
        self.state.outputs = dict(self.body.outputs)


class OutputsPromptBody(ttk.Frame):
    """A container for output entries and a button to add entries.

    Extends ttk.Frame to create a frame for holding the collection of
    entries for editing the outputs as well as a button creating
    additional rows of entries.

    """
    def __init__(self, master, initial_outputs, **kwargs):
        """Create the OutputsPromptBody with some initial outputs.

        Args:
            master: The master of the widget
            initial_outputs: The outputs to load as OutputEntries upon
                widget creation
            **kwargs: Passed to super().__init__

        """
        super().__init__(master, **kwargs)
        self.add_button = ttk.Button(master=self, text="Add output")
        self.add_button.grid(row=0, column=0)
        self.entries = OutputsEntries(master=self,
                                      initial_outputs=initial_outputs)
        self.entries.grid(row=1, column=0)
        self.add_button['command'] = self.entries.add_entry

    @property
    def outputs(self):
        """Return the outputs of OutputsEntries."""
        return self.entries.outputs


class OutputsEntries(ttk.Frame):
    """A container for the output entries.

    Extends ttk.Frame to provide display a vertical list of OutputEntry
    widgets Also provides the exterior for function for deleting and
    removing an OutputEntry widget.

    """
    def __init__(self,
                 master,
                 initial_outputs: Optional[Dict] = None,
                 **kwargs):
        """Create an OutputsEntries widget with initial outputs.

        OutputsEntries is just a vertically stacked list of Entry widgets.

        Args:
            master: The master of the widget
            initial_outputs: A mapping of existing names and outputs to
                fill as defaults into the entries
            **kwargs: Passed to super().__init__

        """
        super().__init__(master, **kwargs)
        initial_outputs = initial_outputs if initial_outputs else {}
        self._entries: List[OutputEntry] = []

        for initial_name, initial_value in initial_outputs.items():
            self.add_entry(initial_name, initial_value)

        if not self._entries:
            self.add_entry()

    def add_entry(self, default_name: str = "", default_value: str = "0"):
        """Create and display a new OutputEntry.

        Additionally, assign the OutputEntry's delete_button command to the
        OutputsEntries del_entry method as a callback.

        Args:
            default_name: The initial name for the entry
            default_value: The initial value for the entry

        """
        output_entry = OutputEntry(master=self,
                                   default_name=default_name,
                                   default_value=default_value)
        output_entry.grid(column=0)
        output_entry.delete_button['command'] = lambda: self.del_entry(
            output_entry)
        self._entries.append(output_entry)
        logging.debug("Total entries now: %s", len(self._entries))

    def del_entry(self, output_entry: 'OutputEntry'):
        """Delete an existing OutputEntry.

        Deleting an entry requires that the OutputEntry be removed from
        the internal list _entries, destroyed be calling
        OutputEntry().destroy, and resetting the grid location of all
        remaining OutputEntry widgets.

        """
        logging.debug("Before deleting the entry, there are %s entries",
                      len(self._entries))
        self._entries.remove(output_entry)
        output_entry.destroy()
        for idx, entry in enumerate(self._entries):
            logging.debug("Resetting grid info of entry %s", entry.grid_info())
            entry.grid(row=idx, column=0)
        logging.debug("Grid size is %s", self.grid_size())

    @property
    def outputs(self) -> Iterable[Tuple[str, str]]:
        """Return the outputs as a list of name, value tuples."""
        return [(entry.name, entry.value) for entry in self._entries]


class OutputEntry(ttk.Frame):
    """A single row of the outputs dialog, also containing a delete button.

    Extends ttk.Frame to contain one ttk.Entry for the output name, one
    tk.Spinbox for the output value, and one ttk.Button for the delete button

    The delete button's command is set outside the scope of its creation.

    Attributes:
        name_entry: A text entry field for the output name
        value_selector: A spinbox for the output value, accepting "0" and "1"
        delete_button: A button for deleting the entry

    """
    def __init__(self,
                 master,
                 default_name: str = "",
                 default_value: str = "0",
                 **kwargs):
        """Create an OutputEntry, a single row of an output and its value.

        Also creates a button for deleting the OutputEntry, though without
        assigning it to a command.

        Args:
            master: The master of the widget
            default_name: The initial value for the name of the output
            default_value: The initial value for the value of the output
            **kwargs: Passed to super().__init__

        """
        super().__init__(master, **kwargs)
        self._name = tk.StringVar()
        self.name_entry: ttk.Entry = ttk.Entry(master=self,
                                               textvariable=self._name,
                                               width=24)
        self.name_entry.grid(row=0, column=0)
        self.value_selector: tk.Spinbox = tk.Spinbox(master=self,
                                                     values=("0", "1"),
                                                     wrap=True,
                                                     width=8,
                                                     state="readonly")
        self.value_selector.grid(row=0, column=1)
        self.delete_button: ttk.Button = ttk.Button(master=self, text="Delete")
        self.delete_button.grid(row=0, column=2)
        self.name = default_name
        self.value = default_value

    def destroy(self):
        """Destroy the OutputEntry.

        The reference to the tkinter StringVar storing the name is set
        to a literal to ensure that it's out of scope even if the
        OutputEntry isn't yet.

        """
        logging.debug("Destroying entry")
        self._name = ''
        super().destroy()

    @property
    def name(self) -> str:
        """Return the name for the output written in the entry field."""
        return str(self._name.get())

    @name.setter
    def name(self, name: str):
        """Set the name for the output written in the entry field."""
        return self._name.set(name)

    @property
    def value(self):
        """Return the value for the output written in the entry field."""
        return self.value_selector.get()

    @value.setter
    def value(self, val: str):
        """Set the value for the output written in the spinbox.

        Args:
            val: The value for the outputs, "0" or "1"

        Raises:
            ValueError: The value was not "0" or "1"

        """
        allowed_values = ("0", "1")
        if val not in allowed_values:
            raise ValueError(f'Output value {val} is not in {allowed_values}')
        self.value_selector['state'] = "normal"
        self.value_selector.delete(0, "end")
        self.value_selector.insert(0, val)
        self.value_selector['state'] = "readonly"
