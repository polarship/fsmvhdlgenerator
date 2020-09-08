"""The top level application and major application components.

Classes:
    Application: The outermost frame of the application
    MainArea: The frame containing both the diagram editor and the side panel
    Editor: The frame containing the DrawingAreaContainer and message bar
    DrawingAreaContainer: The frame encapsulating the drawing area
    TabbedSidePanel: The side panel for showing the code tab

"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Callable

from fsmvhdlgenerator.customwidgets.code_tab import CodeTab
from fsmvhdlgenerator.customwidgets.drawing_area import DrawingArea
from fsmvhdlgenerator.customwidgets.message_bar import MessageBar
from fsmvhdlgenerator.customwidgets.toolbar import Toolbar
from fsmvhdlgenerator.mainapplication.config import (DRAWING_AREA_SIZE,
                                                     ICON_PATH)
from fsmvhdlgenerator.mainapplication.shared import UniversalDict


class Application(ttk.Frame):
    """The outermost container for the application, extending ttk.Frame."""
    def __init__(self, master):
        """Create the outermost frame of the application."""
        super().__init__(master, padding="3 3 3 3")

        self.create_content()
        self.display_content()
        self.populate_toolbar(self.mainarea)
        self.title = None

    def create_content(self):
        """Create application contents.

        Creates the application's primary toolbar and the MainArea below

        """
        self.toolbar = Toolbar(master=self)
        self.separator = ttk.Separator(master=self, orient="horizontal")
        self.mainarea = MainArea(master=self, orient="horizontal")

    def display_content(self):
        """Display application contents.

        Displays the application's contents using tkinter's grid
        geometry manager.

        """
        self.toolbar.grid(column=0, sticky="we")
        self.separator.grid(column=0, sticky="we", pady=(4, 0))
        self.mainarea.grid(column=0, sticky="nwes")
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

    def populate_toolbar(self, mainarea):
        """Fill up the toolbar with the appropriate buttons."""
        drawing_area = mainarea.editor.drawing_area_container.drawing_area
        self.toolbar.create_button("Add state", drawing_area.create_state_tool)
        self.toolbar.create_button("Move state", drawing_area.move_state_tool)
        self.toolbar.create_button("Delete state",
                                   drawing_area.delete_state_tool)
        self.toolbar.create_button("Add transition",
                                   drawing_area.create_transition_tool)
        self.toolbar.create_button("Delete transition",
                                   drawing_area.delete_transition_tool)
        self.toolbar.create_button("Set default state",
                                   drawing_area.set_default_state_tool)


class MainArea(ttk.PanedWindow):
    """The container frame for the editor and tabbed_sidepanel.

    Extends ttk.PanedWindow to display the finite state machine Editor
    and the TabbedSidePanel side-by-side with a movable divider.

    """
    def __init__(self, master, *args, **kwargs):
        """Create the MainArea.

        Adds the editor and tabbed_sidepanel to the ttk.PanedWindow. The
        editor is given twice as much weight to increase it's proportion
        of space used

        """
        super().__init__(master, *args, **kwargs)

        self.editor = Editor(master=self, codetab_setter=self.codetab_setter)
        self.tabbed_sidepanel = TabbedSidePanel(
            master=self, drawing_area=self.editor.drawing_area)
        self.add(self.editor, weight=2)
        self.add(self.tabbed_sidepanel, weight=1)

    def codetab_setter(self, text: str):
        """Set the text in the codetab in the tabbed_sidepanel."""
        self.tabbed_sidepanel.codetab.text = text


class Editor(ttk.Frame):
    """The container frame for the drawing_area and message_bar.

    The Editor contains the drawing_area, where the finite state machine
    is drawn by the user, and the message_bar, which provides feedback
    for the user. It extends ttk.Frame.

    """
    def __init__(self, master, codetab_setter: Callable, **kwargs):
        """Create an Editor frame.

        Args:
            master: The master of the frame
            codetab_setter: A callable that can be called to set the text in
                the CodeText frame.
            **kwargs: Passed to super().__init__

        """
        super().__init__(master, **kwargs)
        self.codetab_setter = codetab_setter
        self.create_contents()
        self.display_contents()

    def create_contents(self):
        """Create the drawing_area_container and message bar."""
        self.message_bar = MessageBar(master=self)

        self.message_setter = self.message_bar.message_setter
        self.drawing_area_container = DrawingAreaContainer(
            master=self,
            codetab_setter=self.codetab_setter,
            message_setter=self.message_setter)

    def display_contents(self):
        """Display the drawing area and message bar."""
        self.message_bar.grid(row=2, column=0, sticky="we")
        self.drawing_area_container.grid(row=0, column=0, sticky="nwes")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    @property
    def drawing_area(self):
        """Return the drawing_area, where the finite state machine is drawn."""
        return self.drawing_area_container.drawing_area


class DrawingAreaContainer(ttk.Frame):
    """The container frame for the drawing area.

    The drawing area is where the user's finite state machine is drawn.
    DrawingAreaContainer extends ttk.Frame.

    """
    def __init__(self, master: tk.Widget, codetab_setter: Callable,
                 message_setter: Callable, **kwargs):
        """Create the container frame for the drawing_area.

        Args:
            master: The master widget
            codetab_setter: A callable that can be called to set the text in
                the CodeText frame.
            message_setter: A callable that can be called to set the text in
                the MessageBar frame.
            **kwargs: Passed to super().__init__

        """
        super().__init__(master, **kwargs)
        self.codetab_setter = codetab_setter
        self.message_setter = message_setter
        self.create_contents()
        self.display_contents()

    def create_contents(self):
        """Create the drawing area."""
        universal = UniversalDict()

        self._drawing_area = DrawingArea(master=self,
                                         root=universal['root'],
                                         scrollregion=(0, 0,
                                                       *DRAWING_AREA_SIZE),
                                         codetab_setter=self.codetab_setter,
                                         message_setter=self.message_setter,
                                         region_size=DRAWING_AREA_SIZE)

    def display_contents(self):
        """Display the drawing area."""
        self._drawing_area.grid(row=0, column=0, sticky="nwes")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    @property
    def drawing_area(self):
        """Return the tkinter canvas object in the drawing area."""
        return self._drawing_area.widget


class TabbedSidePanel(ttk.Notebook):
    """The tabbed side panel containing the code tab.

    The tabbed side panel contains tabbed panels for auxiliary
    interactions with the drawing area.

    """
    def __init__(self, master: tk.Widget, drawing_area: DrawingArea, *args,
                 **kwargs):
        """Create the TabbedSidePanel containing the codetab.

        Args:
            master: The master of the side panel
            drawing_area: The DrawingArea widget with code generation tools
            *args: Passed to super().__init__
            **kwargs: Passed to super().__init__

        """
        super().__init__(*args, **kwargs)
        self.codetab = CodeTab(master=self, drawing_area=drawing_area)
        self.add(self.codetab, text="Code")


class FsmVhdlGenerator(tk.Tk):
    """The application top-level window."""
    def __init__(self):
        """Launch the application in a full screen window."""
        logging.info('Application started')

        super().__init__()
        self.set_icon(ICON_PATH)
        self.title("FSM VHDL Generator")
        self.wm_attributes('-zoomed', 1)
        self.minsize(600, 600)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.run_app()
        logging.info('Application finished')

    def set_icon(self, icon_location):
        """Set the taskbar icon of the app.

        Set the app to the bitmap located at icon_location.

        Args:
            icon_location: The bitmap "xbm" file of the icon.

        """
        try:
            self.iconbitmap(f'@{icon_location}')
        except tk.TclError:
            logging.warning('Icon not found at %s', icon_location)

    def run_app(self):
        """Run the application."""
        logging.info('Using tkinter theme "%s"', ttk.Style().theme_use())
        universal = UniversalDict(root=self)
        logging.debug('Setting root as %s', universal['root'])
        app = Application(master=self)
        app.grid(row=0, column=0, sticky="nwes")
        app.mainloop()
