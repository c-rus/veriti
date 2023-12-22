library ieee;
use ieee.std_logic_1164.all;

library std;
use std.textio.all;

library work;

entity bcd_enc_tb is
    generic (
        LEN: positive := 4;
        DIGITS: positive := 2
    );
end entity;

architecture sim of bcd_enc_tb is
    use work.veriti;
    use work.casting;

    -- This record is auto-generated by veriti. DO NOT EDIT.
    type bcd_enc_bfm is record
        go: std_logic;
        bin: std_logic_vector(LEN-1 downto 0);
        bcd: std_logic_vector((4*DIGITS)-1 downto 0);
        ovfl: std_logic;
        done: std_logic;
    end record;

    signal bfm: bcd_enc_bfm;

    signal clk: std_logic;
    signal rst: std_logic;
    signal halt: boolean := false;

    --! declare internal required testbench signals
    constant TIMEOUT_LIMIT: natural := 1_000;

    file events: text open write_mode is "events.log";

begin
    -- instantiate UUT
    UUT: entity work.bcd_enc
    generic map (
        LEN   => LEN,
        DIGITS => DIGITS
    ) port map (
        rst   => rst,
        clk   => clk,
        go    => bfm.go,
        bin   => bfm.bin,
        bcd   => bfm.bcd,
        done  => bfm.done,
        ovfl  => bfm.ovfl
    );

    --! generate a 50% duty cycle for 25 Mhz
    veriti.spin_clock(clk, 40 ns, halt);

    --! test reading a file filled with test vectors
    driver: process
        file inputs: text open read_mode is "inputs.trace";

        -- This procedure is auto-generated by veriti. DO NOT EDIT.
        procedure drive_transaction(file fd: text) is 
            variable row: line;
        begin
            if endfile(fd) = false then
                -- drive a transaction
                readline(fd, row);
                veriti.drive(row, bfm.go);
                -- veriti.log_event(events, veriti.TRACE, "DRIVE", "go - " & casting.to_str(bfm.go));
                veriti.drive(row, bfm.bin);
                -- veriti.log_event(events, veriti.TRACE, "DRIVE", "bin - " & casting.to_str(bfm.bin));
            end if;
        end procedure; 

    begin  
        -- initialize input signals      
        drive_transaction(inputs);
        veriti.reset_system(clk, rst, 3);
        wait until rising_edge(clk);

        -- drive transactions
        while endfile(inputs) = false loop
            drive_transaction(inputs);
            wait until rising_edge(clk);
        end loop;

        -- wait for all outputs to be checked
        wait;
    end process;

    monitor: process
        file outputs: text open read_mode is "outputs.trace";
        variable timeout: boolean;

        procedure score(file fd: text; file ld: text) is
            variable row: line;
            variable expct: bcd_enc_bfm;
        begin
            if endfile(fd) = false then
                -- compare received outputs with expected outputs
                readline(fd, row);
                veriti.load(row, expct.bcd);
                veriti.log_assertion(ld, bfm.bcd, expct.bcd, "bcd");

                veriti.load(row, expct.done);
                veriti.log_assertion(ld, bfm.done, expct.done, "done");
                
                veriti.load(row, expct.ovfl);
                veriti.log_assertion(ld, bfm.ovfl, expct.ovfl, "ovfl");
            end if;
        end procedure;
        
    begin
        wait until rising_edge(clk) and rst = '0';

        while endfile(outputs) = false loop
            -- @note: should monitor detect rising edge or when = '1'? ... when = '1' will delay by a cycle, which could not be the intention
            -- @todo: have better handling of monitor process (WIP, might be good now)

            -- wait for a valid time to check
            veriti.log_monitor(events, clk, bfm.done, TIMEOUT_LIMIT, timeout, "done being asserted");

            -- compare outputs
            score(outputs, events);
            -- wait for done to be lowered before starting monitor
            wait until falling_edge(bfm.done);
        end loop;

        -- halt the simulation
        veriti.complete(halt);
    end process;

    -- concurrent captures of simulation
    veriti.log_stability(events, clk, bfm.done, bfm.bcd, "bcd depending on done");

end architecture;