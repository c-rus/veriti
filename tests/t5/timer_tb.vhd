library ieee;
use ieee.std_logic_1164.all;

library std;
use std.textio.all;

library work;
use work.standard.all;

library veriti;
use veriti.veriti.all;

entity timer_tb is
  generic (
    BASE_DELAY: pve := 4;
    SUB_DELAYS: pves := (2, 4, 10, 19, 32)
  );
end entity;


architecture sim of timer_tb is

  type timer_bfm is record
    base_tick: logic;
    sub_ticks: logics(SUB_DELAYS'left to SUB_DELAYS'right);
  end record;
  
  signal bfm: timer_bfm;

  signal clk: logic;
  signal rst: logic;
  signal halt: bool := false;

  -- declare internal required testbench signals
  constant TIMEOUT_LIMIT: nat := 1_000;

  file events: text open write_mode is "events.log";

begin

  -- instantiate UUT
  uut: entity work.timer
    generic map (
      BASE_DELAY => BASE_DELAY,
      SUB_DELAYS => SUB_DELAYS
    ) 
    port map (
      rst => rst,
      clk => clk,
      base_tick => bfm.base_tick,
      sub_ticks => bfm.sub_ticks
    );

  -- generate a 50% duty cycle for 25 MHz
  spin_clock(clk, 40 ns, halt);

  -- test reading a file filled with test vectors
  producer: process
      file inputs: text open read_mode is "inputs.trace";

      procedure send_transaction(file fd: text) is 
        variable row: line;
      begin
        if endfile(fd) = false then
          -- drive a transaction
          readline(fd, row);
        end if;
      end procedure;

  begin  
    -- power-on reset
    reset_system(clk, rst, 2);

    -- drive transactions
    while endfile(inputs) = false loop
      send_transaction(inputs);
      wait until rising_edge(clk);
    end loop;

    -- wait for all outputs to be checked
    wait;
  end process;

  consumer: process
    file outputs: text open read_mode is "outputs.trace";
    variable timeout: bool;

    procedure score_transaction(file fd: text) is 
      variable row: line;
      variable expct: timer_bfm;
    begin
      if endfile(fd) = false then
        -- compare received outputs with expected outputs
        readline(fd, row);
        load(row, expct.base_tick);
        log_assertion(events, bfm.base_tick, expct.base_tick, "base_tick");
        load(row, expct.sub_ticks);
        log_assertion(events, bfm.sub_ticks, expct.sub_ticks, "sub_ticks");
      end if;
    end procedure;

  begin
    wait until rst = '0' and rising_edge(clk);
    -- wait an additional initial cycle due to wake-from-reset logic
    wait until rising_edge(clk);

    while endfile(outputs) = false loop
      -- wait for a valid time to check
      wait until rising_edge(clk);
      -- compare outputs
      score_transaction(outputs);
    end loop;

    -- halt the simulation
    complete(halt);
  end process;

end architecture;