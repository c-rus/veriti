--------------------------------------------------------------------------------
--! Project: veriti
--! Author: Chase Ruskin
--! Created: 2023-12-16
--! Package: casting
--! Details:
--!     Conversion functions between data types in VHDL. These functions
--!     are called in higher-level hardware driver layer functions.
--------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

package casting is

    --! Returns a string representation of logic vector to output to console.
    function logics_to_str(slv: std_logic_vector) return string;

    --! Returns a string representation of logic bit to output to console.
    function logic_to_str(sl: std_logic) return string;

    --! Casts a character `c` to a logical '1' or '0'. Anything not the character
    --! '1' maps to a logical '0'.
    function char_to_logic(c: character) return std_logic;

end package;


package body casting is

    function logics_to_str(slv: std_logic_vector) return string is
        variable str : string(1 to slv'length);
        variable str_index : positive := 1;
        variable sl_bit : std_logic;
    begin
        for ii in slv'range loop
            sl_bit := slv(ii);
            if sl_bit = '1' then
                str(str_index) := '1';
            elsif sl_bit = '0' then
                str(str_index) := '0';
            else
                str(str_index) := '?';
            end if;
            str_index := str_index + 1;
        end loop;

        return integer'image(slv'length) & "b'" & str;
    end function;


    function logic_to_str(sl: std_logic) return string is
    begin
        return std_logic'image(sl);
    end function;


    function char_to_logic(c: character) return std_logic is
    begin
        if(c = '1') then
            return '1';
        else
            return '0';
        end if;
    end function;

end package body;