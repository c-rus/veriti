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
use ieee.numeric_std.all;

library std;
use std.textio.all;

package casting is

    --! Returns a string representation of logic vector to output to console.
    function logics_to_str(slv: std_logic_vector) return string;

    --! Returns a string representation of logic bit to output to console.
    function logic_to_str(sl: std_logic) return string;

    --! Casts a character `c` to a logical '1' or '0'. Anything not the character
    --! '1' maps to a logical '0'.
    function char_to_logic(c: character) return std_logic;

    --! Consumes a single line in file `f` to cast from numerical value to a 
    --! logic vector of size `len` consisting of logical '1' and '0's.
    --!
    --! Note: Integers cannot be read as 'negative' with a leading '-' sign.
    impure function read_int_to_logics(file f: text; len: positive) return std_logic_vector;

    --! Consumes a single line in file `f` to cast from numerical value to logical
    --! '1' or '0'.
    impure function read_int_to_logic(file f: text) return std_logic;

    --! Consumes a single line in file `f` to be a logic vector of size `len`
    --! consisting of logical '1' and '0's.
    impure function read_str_to_logics(file f: text; len: positive) return std_logic_vector;

    --! Consumes a single line in file `f` to be a logical '1' or '0'.
    impure function read_str_to_logic(file f: text) return std_logic;

end package;


package body casting is

    
    function to_sl(i: integer) return std_logic is
    begin
        if(i = 0) then
            return '0';
        else
            return '1';
        end if;
    end function;


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


    impure function read_int_to_logics(file f: text; len: positive) return std_logic_vector is
        variable text_line : line;
        variable text_int  : integer;
    begin
        readline(f, text_line);
        read(text_line, text_int);
        return std_logic_vector(to_unsigned(text_int, len));
    end function;


    impure function read_int_to_logic(file f: text) return std_logic is
        variable text_line : line;
        variable text_int  : integer;
    begin
        readline(f, text_line);
        read(text_line, text_int);
        return to_sl(text_int);
    end function;


    function char_to_logic(c: character) return std_logic is
    begin
        if(c = '1') then
            return '1';
        else
            return '0';
        end if;
    end function;


    impure function read_str_to_logics(file f: text; len: positive) return std_logic_vector is
        variable text_line : line;
        variable text_str  : string(len downto 1);
        variable slv       : std_logic_vector(len-1 downto 0);
    begin
        readline(f, text_line);
        read(text_line, text_str);

        for ii in len-1 downto 0 loop
            slv(ii) := char_to_logic(text_str(ii+1));
        end loop;

        return slv;
    end function;


    impure function read_str_to_logic(file f: text) return std_logic is
        variable text_line : line;
        variable text_str  : string(1 downto 1);
    begin
        readline(f, text_line);
        read(text_line, text_str);
        return char_to_logic(text_str(1));
    end function;

end package body;