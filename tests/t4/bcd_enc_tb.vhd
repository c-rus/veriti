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
    constant TIMEOUT_LIMIT: natural := 1000;

    file results: text open write_mode is "results.log";

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
        file inputs: text open read_mode is "inputs.dat";

        -- This procedure is auto-generated by veriti. DO NOT EDIT.
        procedure drive_transaction(file fd: text) is 
            variable row: line;
        begin
            if endfile(fd) = false then
                -- drive a transaction
                readline(fd, row);
                veriti.drive(row, bfm.go);
                veriti.drive(row, bfm.bin);
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
        file outputs: text open read_mode is "outputs.dat";
        variable timeout: boolean;

        procedure score(file ld: text; file fd: text) is
            variable row: line;
            variable expct: bcd_enc_bfm;
        begin
            if endfile(fd) = false then
                -- compare received outputs with expected outputs
                readline(fd, row);
                veriti.load(row, expct.bcd);
                veriti.log_assertion(ld, bfm.bcd, expct.bcd, "bcd");

                veriti.load(row, expct.ovfl);
                veriti.log_assertion(ld, bfm.ovfl, expct.ovfl, "ovfl");

                veriti.load(row, expct.done);
                veriti.log_assertion(ld, bfm.done, expct.done, "done");
            end if;
        end procedure;
        
    begin
        wait until rst = '0';

        while endfile(outputs) = false loop
            -- wait for a valid time to check
            wait until rising_edge(bfm.done);
            -- @note: should monitor detect rising edge or when = '1'?
            veriti.log_monitor(results, clk, bfm.done, TIMEOUT_LIMIT, timeout, "done");

            -- compare outputs
            score(results, outputs);
            wait until rising_edge(clk);
        end loop;

        -- halt the simulation
        veriti.complete(halt);
    end process;

    -- concurrent assertions


    -- capture_stability(...)
    -- veriti.assert_stability(clk, bfm.done, bfm.bcd, "bcd");
    veriti.log_stability(results, clk, bfm.done, bfm.bcd, "bcd switches while done remains asserted");

    -- experimental code
    --- verity.assert_stability(clk, bfm.done, as_logics(bfm.ovfl), "ovfl");

    -- procedure assert_stability(clk: logic; cond: bool; vec: logics; halt: bool; comment: string) is
    -- concurrent assertions
    -- assert_stability: process
    --     variable bcd_delta: logics(bfm.bcd'range);
    --     variable ovfl_delta: logic;
    -- begin
    --     wait until rising_edge(bfm.done);
    --     bcd_delta := bfm.bcd;
    --     ovfl_delta := bfm.ovfl;
    --     while bfm.done = '1' and halt = false loop
    --         -- check if its been stable since the rising edge of done
    --         assert bcd_delta = bfm.bcd report "Output 'bcd' unstable" severity error;
    --         assert ovfl_delta = bfm.ovfl report "Output 'ovfl' unstable" severity error;
    --         wait until rising_edge(clk);
    --     end loop;
    --     verity.check(halt);
    -- end process;

end architecture;