"""The main entry point for the program."""
import logging
import sys

from fsmvhdlgenerator.mainapplication.fsmvhdlgenerator import FsmVhdlGenerator

logging.basicConfig(level=logging.DEBUG)


def main(args):
    """Launch the application by creating an instance of it."""
    app = FsmVhdlGenerator()
    sys.exit(app or 0)


def gui_entry():
    """Launch the application as the main entry point for launchers."""
    logging.basicConfig(level=logging.CRITICAL)
    main(None)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
