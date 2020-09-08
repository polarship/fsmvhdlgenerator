library IEEE;
  use IEEE.STD_LOGIC_1164.ALL;

entity MooreFSM is
  port (
    clk        : in    STD_LOGIC;
    clk_enable : in    STD_LOGIC;
    x          : in    STD_LOGIC;
    y          : in    STD_LOGIC;
    u          : out   STD_LOGIC;
    v          : out   STD_LOGIC
  );
end entity MooreFSM;

architecture behavioral of MooreFSM is
  type state_type is (s0, s1);
  signal state, next_state : state_type := s0;
begin

  clk_process : process (clk) is
  begin
    if (rising_edge(clk)) then
      if (clk_enable='1') then
        state <= next_state;
      end if;
    end if;

  end process clk_process;

  state_process : process (state, x, y) is
  begin
    case state is

      when s0 =>
        u <= '0';
        v <= '0';

        if (x='1') then
          next_state <= s0;
        elsif (x='0') then
          next_state <= s1;
        end if;
        
      when s1 =>
        u <= '1';
        v <= '0';

        if (x='1' and y='0') then
          next_state <= s0;
        elsif (x='0' or y='1') then
          next_state <= s1;
        end if;
        
    end case;

  end process state_process;

end architecture behavioral;
