"""Tests VHDL generation from the hdl module."""
from fsmvhdlgenerator.finitestatemachine.hdl import \
    render_moore_finite_state_machine_vhdl

CORRECT_OUTPUT_FILE = 'tests/complete_fsm.vhd'

CORRECT_TESTBENCH_OUTPUT_FILE = 'tests/complete_fsm_testbench.vhd'


def test_vhdl_generation(complete_fsm):
    """Test if VHDL generation from fixture matches output."""
    output_text = render_moore_finite_state_machine_vhdl(complete_fsm)
    with open(CORRECT_OUTPUT_FILE) as vhd_file:
        assert output_text.strip() == vhd_file.read().strip()


def test_vhdl_testbench_generation(complete_fsm):
    """Test if VHDL generation from fixture matches output."""
    output_text = render_moore_finite_state_machine_vhdl(complete_fsm,
                                                         testbench=True)
    with open(CORRECT_TESTBENCH_OUTPUT_FILE) as vhd_file:
        assert output_text.strip() == vhd_file.read().strip()
