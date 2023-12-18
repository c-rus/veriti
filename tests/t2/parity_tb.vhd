--------------------------------------------------------------------------------
--! Project: veriti
--! Author: Chase Ruskin
--! Created: 2022-10-07
--! Testbench: parity_tb
--! Details:
--!     Verifies the `parity` entity using file I/O transactions from a software
--!     model script 'parity_tb.py' with built-in assertions.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;

library work;
use std.textio.all;
use work.veriti;
use work.casting;

entity parity_tb is 
    generic (
        --! data width
        SIZE        : positive := 8;
        --! Determine to perform even or odd parity
        EVEN_PARITY : boolean := true
    );
end entity parity_tb;


architecture bench of parity_tb is
    --! unit-under-test (UUT) interface wires
    type parity_bfm is record
        data      : std_logic_vector(SIZE-1 downto 0);
        check_bit : std_logic;
    end record;

    signal bfm : parity_bfm;

    --! internal testbench signals
    constant DELAY: time := 10 ns;

    signal halt: boolean := false;

    file results : text open write_mode is "results.log";

begin
    --! UUT instantiation
    uut : entity work.parity
    generic map (
        SIZE        => SIZE,
        EVEN_PARITY => EVEN_PARITY
    ) port map (
        data      => bfm.data,
        check_bit => bfm.check_bit
    );

    --! assert the received outputs match expected model values
    bench: process
        file inputs  : text open read_mode is "inputs.dat";
        file outputs : text open read_mode is "outputs.dat";
        
        procedure drive_transaction(file fd: text) is 
            variable row : line;
        begin
            if endfile(fd) = false then
                -- drive a transaction
                readline(fd, row);
                veriti.drive(row, bfm.data);
            end if;
        end procedure;

        procedure log_transaction(file ld: text; file fd: text) is
            variable row: line;
            variable expct: parity_bfm;
        begin
            if endfile(fd) = false then
                -- compare received outputs with expected outputs
                readline(fd, row);
                veriti.load(row, expct.check_bit);
                veriti.log_assertion(results, bfm.check_bit, expct.check_bit, "check_bit");
            end if;
        end procedure;

    begin
        -- drive UUT and check circuit behavior
        while not endfile(inputs) loop
            drive_transaction(inputs);

            wait for DELAY;

            --! read expected outputs from file
            log_transaction(results, outputs);
        end loop;

        -- halt the simulation
        veriti.complete(halt);
    end process;

end architecture;