"""Module for hardware definition language (HDL) components.

This module contains tools for working with and generating VHDL code

Classes:
    VHDLIdentifier: A string-like class for VHDL identifiers

Functions:
    render_moore_finite_state_machine_vhdl

"""

import collections

import jinja2


class VHDLIdentifier(collections.UserString):
    """A class for string-like VHDL identifiers.

    Objects can be used like strings in most ways, but will not accept values
    that are not valid VHDL identifiers

    Raises:
        ValueError: The value was not a valid VHDL identifier

    """
    def __init__(self, iterable):
        """Create a string-like VHDL identifier."""
        if not self.check(iterable):
            raise ValueError("{} is not a valid VHDL identifier".format(
                str(iterable)))
        super().__init__(iterable)

    @staticmethod
    def check(iterable) -> bool:
        """Checks that iterable is a valid VHDL identifier.

        An identifier is valid if it's first character is a letter and
        other characters are letters, numbers, or underscores

        """
        return str(iterable)[0].isalpha() and str(iterable).replace(
            "_", "").isalnum()


def render_moore_finite_state_machine_vhdl(finite_state_machine,
                                           name: str = "MooreFSM",
                                           testbench: bool = False) -> str:
    """Render a Moore finite state machine with the jinja2 template.

    An appropriate testbench can also be generated with the testbench option.
    The jinja2 templates are stored in templates/ and control the generation of
    the VHDL code for the finite state machine.

    Args:
        finite_state_machine: The Moore finite state machine to render VHDL
        name: The name of the finite state machine to use in the VHDL

    Returns:
        The VHDL code

    """
    template_loader = jinja2.PackageLoader('fsmvhdlgenerator')

    template_env = jinja2.Environment(loader=template_loader,
                                      trim_blocks=True,
                                      lstrip_blocks=True)
    if not testbench:
        template_file = "moore_finite_state_machine.vhd.j2"
    else:
        template_file = "testbed_finite_state_machine.vhd.j2"
    template = template_env.get_template(template_file)
    output_text = template.render(fsm_name=name, fsm=finite_state_machine)
    return output_text
