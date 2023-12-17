--------------------------------------------------------------------------------
--* Project  : std-lib
--* Engineer : Chase Ruskin
--* Created  : 2023-06-11
--* Library  : core
--* Package  : math
--* Details  :
--*     Helper functions to calculate parameters and perform common mathematical
--*     equations.
--*
--*     NAME            PARAMETERS         RETURN VALUE
--*     clog2           (positive)              -> positive
--*     flog2p1         (positive)              -> positive
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;

package math is
    --* Mathematical constant pi
    constant PI: real := 3.141592653589793;

    --* Mathematical constant e
    constant E: real := 2.718281828459045;

    --* Mathematical constant tau - the ratio of a circle's circumference to its
    --* radius.
    constant TAU: real := 6.283185307179586;
    
    --* Computes the logarithmic (base 2) for 'enums' and takes the ceiling
    --* value. Determines the minimum number of bits required to represent 
    --* 'num' possible values.
    --*
    --* Equation: ceil(log2(num))
    function clog2(num: positive) return positive;

    --* Determines the minimum number of bits required to represent the 'num'
    --* decimal number in standard binary representation.
    --*
    --* Equation: floor(log2(num) + 1)
    function flog2p1(num: positive) return positive;

    --* Computes 2 raised to the 'num'.
    --*
    --* This effectively computes the maximum number of possible values
    --* represented in a vector with 'num' width.
    function pow2(num: natural) return natural;

    --* Computes 2 raised to the 'num' minus 1.
    --*
    --* This effectively determines the maximum represented number for a vector
    --* with 'num' width.
    function pow2m1(num: natural) return natural;

    --* Determines if a number is a power of 2.
    function is_pow2(num: natural) return boolean;

end package;


package body math is

    function clog2(num: positive) return positive is
        variable count : positive := 1;
        variable total : positive := 1;
    begin
        if num = 1 then
            return 1;
        end if;
        -- count number of powers of 2 until matching or exceeding number
        loop 
            total := total * 2;
            if total >= num then
                exit;
            end if;
            count := count + 1;
        end loop;

        return count;
    end function;


    function flog2p1(num: positive) return positive is
        variable count : positive := 1;
        variable total : positive := 1;
    begin
        if num = 1 or num = 2 then
            return num;
        end if;
        -- count number of powers of 2 until exceeding number
        loop 
            total := total * 2;
            if total > num then
                exit;
            end if;
            count := count + 1;
        end loop;

        return count;
    end function;


    function pow2(num: natural) return natural is
    begin
        if num = 0 then
            return 1;
        else
            return 2 ** num;
        end if;
    end function;


    function pow2m1(num: natural) return natural is 
    begin
        if num = 0 then
            return 1-1;
        else
            return (2 ** num) - 1;
        end if;
    end function;


    function is_pow2(num: natural) return boolean is
        variable temp: natural;
    begin
        temp := num;
        while temp > 2 loop 
            if temp rem 2 /= 0 and temp > 2 then
                return false;
            end if;
            temp := temp / 2;
        end loop;
        return true;
    end function;

end package body;