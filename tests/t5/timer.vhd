library ieee;
use ieee.std_logic_1164.all;

library work;
use work.standard.all;
use work.math.all;

entity timer is
  generic (
    -- Common delay among all sub-counters for cycles
    BASE_DELAY: pve;
    -- Counters that increment off the base count overflowing. This value 
    -- effectively gets "multiplied" to the 'BASE_DELAY'.
    SUB_DELAYS: pves
  );
  port (
    rst: in  logic;
    clk: in  logic;
    base_tick: out logic;
    sub_ticks: out logics(SUB_DELAYS'left to SUB_DELAYS'right)
  );
end entity;

architecture rtl of timer is

  function maximum(arr: pves) return pve is
    variable max: int := arr'left;
  begin
    for i in arr'left to arr'right loop
      if arr(i) > max then
        max := arr(i);
      end if;
    end loop;   
    return max;
  end function;

  type logics2d is array (natural range SUB_DELAYS'left to SUB_DELAYS'right) of logics(clog2(maximum(SUB_DELAYS))-1 downto 0);

  signal sub_counts: logics2d;

  signal wake_from_rst: logic;

  -- must be able to wait 'BASE_DELAY' number of cycles
  signal base_count: logics(clog2(BASE_DELAY)-1 downto 0);

begin

  tick: process(rst, clk) is
    variable base_tick_v: logic;
  begin
    if rst = '1' then
      -- reset counters
      for i in sub_counts'range loop
        sub_counts(i) <= (others => '0');
      end loop;
      
      -- reset base counter
      base_count <= (others => '0');

      wake_from_rst <= '1';

      sub_ticks <= (others => '0');
      base_tick <= '0';

    elsif rising_edge(clk) then
      base_tick_v := '0';

      if wake_from_rst = '0' then
        -- increment the counter
        base_count <= base_count + '1';
        -- check if we have counted 'BASE_DELAY' clock cycles
        if base_count = BASE_DELAY-1 then
            base_tick_v := '1';
            base_count <= (others => '0');
        end if;
      end if;

      -- always start from cleared state
      sub_ticks <= (others => '0');

      -- only increment when the base counter has reached its limit
      if base_tick_v = '1' then
        -- visit every sub-counter
        for i in sub_counts'range loop
          -- increment the sub-counter
          sub_counts(i) <= sub_counts(i) + 1;
          -- check if the tick should overflow
          if sub_counts(i) = SUB_DELAYS(i)-1 then
            sub_ticks(i) <= '1';
            sub_counts(i) <= (others => '0');
          end if;
        end loop;
      end if;

      -- update signals at the end of process
      wake_from_rst <= '0';
      base_tick <= base_tick_v;
    end if;
  end process;

end architecture;