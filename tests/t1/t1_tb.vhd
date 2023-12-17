library ieee;
use ieee.std_logic_1164.all;

entity t1 is 
port (
    data: out std_logic
);
end entity;

architecture rtl of t1 is
begin
    data <= '1';
end architecture rtl;


library work;
library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;
use ieee.numeric_std.all;

use work.casting;
use work.veriti.all;

entity t1_tb is
end entity;

architecture sim of t1_tb is

    constant WIDTH_A : positive := 12;

    --! internal test signals
    signal slv0 : std_logic_vector(WIDTH_A-1 downto 0) := (others => '0');
    signal slv1 : std_logic_vector(WIDTH_A-1 downto 0) := (others => '0');
    signal slv2 : std_logic_vector(7 downto 0);

    signal sl0 : std_logic;

    signal w_data : std_logic;

begin
    -- unit-under-test
    uut : entity work.t1 
    port map(
        data => w_data
    );

    --! test reading a file filled with test vectors
    io: process
        file numbers: text open read_mode is "numbers.dat";
    begin
        -- read 1s and 0s into logic vectors
        slv0 <= casting.read_str_to_logics(numbers, WIDTH_A);
        slv1 <= casting.read_str_to_logics(numbers, WIDTH_A);
        wait for 10 ns;
        report "slv0: " & casting.logics_to_str(slv0);
        report "slv1: " & casting.logics_to_str(slv1);
        assert_eq(slv0, slv1, "data");
        
        log(error, "slv0");

        -- read integers into logic vectors
        slv0 <= casting.read_int_to_logics(numbers, slv0'length);
        slv2 <= casting.read_int_to_logics(numbers, slv2'length);
        wait for 10 ns;
        report "slv0: " & casting.logics_to_str(slv0);
        report "slv2: " & casting.logics_to_str(slv1);


        -- read characters into logic bits
        sl0 <= casting.read_str_to_logic(numbers);
        wait for 10 ns;
        report "sl0: " & casting.logic_to_str(sl0);

        sl0 <= casting.read_str_to_logic(numbers);
        wait for 10 ns;
        report "sl0: " & casting.logic_to_str(sl0);

        assert_ne(w_data, sl0, "data");
        -- halt the simulation
        report "Simulation complete.";

        wait;
    end process;

end architecture sim;
