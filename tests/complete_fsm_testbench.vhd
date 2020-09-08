library IEEE;
  use IEEE.STD_LOGIC_1164.ALL;

entity testbed_MooreFSM is
end entity testbed_MooreFSM;

architecture behavior of testbed_MooreFSM is

  component MooreFSM is
    port (
      clk        : in    STD_LOGIC;
      clk_enable : in    STD_LOGIC;
      x          : in    STD_LOGIC;
      y          : in    STD_LOGIC;
      u          : out   STD_LOGIC;
      v          : out   STD_LOGIC
    );
  end component;

  -- Clock signals
  signal clk        : std_logic := '0';
  signal clk_enable : std_logic := '1';

  -- Input signals
  signal x : std_logic := '0';
  signal y : std_logic := '0';

  -- Output signals
  signal u : std_logic := '0';
  signal v : std_logic := '0';

  constant clk_period : time := 31.25 ns;
begin

  uut : MooreFSM
    port map (
      clk        => clk,
      clk_enable => clk_enable,
      x          => x,
      y          => y,
      u          => u,
      v          => v
    );

  clk_process: process is
  begin

    clk <= '0';
    wait for clk_period / 2;
    clk <= '1';
    wait for clk_period / 2;

  end process clk_process;

  stimulus_process : process is
  begin

    wait for 200 ns;

    -- Your tests here
    -- x <= '1';
    -- y <= '1';

    wait;

  end process stimulus_process;

end architecture behavior;
