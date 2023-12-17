--* Project  : standard
--* Engineer : Chase Ruskin
--* Created  : 2023-06-11
--* Library  : core
--* Package  : standard
--* Details  :
--*     Standard package for shorter type names, common overloaded operators,
--*     and common type casting/conversion.
--*     
--*     By default, all functions operate on logic vectors as unsigned types.
--*
--*     NAME            PARAMETERS         RETURN VALUE
--*     +               (logics, logics)   -> logics
--*     -               (logics, logics)   -> logics
--*     *               (logics, logics)   -> logics
--*     +               (logics, nat)      -> logics
--*     -               (logics, nat)      -> logics
--*     =               (logics, nat)      -> bool
--*     /=              (logics, nat)      -> bool

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package standard is
    -- New types
    type option is (enable, disable);
    type negative is range -1 downto integer'low;

    -- Shorthand subtypes
    subtype pve is positive;
    subtype nve is negative;
    subtype int is integer;
    subtype nat is natural;
    subtype str is string;
    subtype bool is boolean;
    subtype char is character;
    subtype sevl is severity_level;

    subtype bits is bit_vector;

    subtype logic is std_logic;
    subtype logics is std_logic_vector;

    subtype ulogic is std_ulogic;
    subtype ulogics is std_ulogic_vector;

    -- New unconstrained array types
    type ints is array (natural range <>) of integer;
    type bools is array (natural range <>) of boolean;
    type nats is array (natural range <>) of natural;
    type pves is array (natural range <>) of positive;
    type nves is array (natural range <>) of negative;

    --* Adds 'lhs' and 'rhs' vectors using unsigned notation (lhs + rhs). 
    --*
    --* The resulting vector has a width matching the widest input vector.
    function "+"(lhs: logics; rhs: logics) return logics;

    --* Subtracts 'rhs' from 'lhs' using unsigned notation (lhs - rhs).
    --*
    --* The resulting vector has a width matching the widest input vector.
    function "-"(lhs: logics; rhs: logics) return logics;

    --* Multiplies 'lhs' by 'rhs' using unsigned notation (lhs * rhs).
    --*
    --* The resulting vector has a width of lhs'length + rhs'length bits wide.
    function "*"(lhs: logics; rhs: logics) return logics;

    --* Adds a decimal numbber to a vector using unsigned casting and unsigned
    --* addition.
    --*
    --* The resulting vector has a width matching lhs'length.
    function "+"(lhs: logics; rhs: nat) return logics;

    --* Subtracts a decimal number from a vector using unsigned casting and
    --* unsigned substraction.
    --*
    --* The resulting vector has a width matching lhs'length.
    function "-"(lhs: logics; rhs: nat) return logics;

    --* Checks the equality between the vector and a decimal number interpreted
    --* as an unsigned vector.
    --*
    --* Returns TRUE if the vector is equivalent to the decimal value.
    function "="(lhs: logics; rhs: nat) return bool;

    --* Checks the inequality between the vector and a decimal number interpreted
    --* as an unsigned vector.
    --*
    --* Returns TRUE if the vector is not equivalent to the decimal value.
    function "/="(lhs: logics; rhs: nat) return bool;

    function ">="(lhs: logics; rhs: nat) return bool;
    -- function "<="(lhs: logics; rhs: nat) return bool;
    -- function ">"(lhs: logics; rhs: nat) return bool;
    -- function "<"(lhs: logics; rhs: nat) return bool;

    function "+"(lhs: logics; rhs: logic) return logics;
    function "-"(lhs: logics; rhs: logic) return logics;

    function "sll"(vec: logics; amt: pve) return logics;
    function "srl"(vec: logics; amt: pve) return logics;
    function "sla"(vec: logics; amt: pve) return logics;
    function "sra"(vec: logics; amt: pve) return logics;

    -- Casting Types/Conversions

    function to_int(vec: logics) return nat;
    function to_logics(num: nat; len: pve) return logics;

    function as_logics(b: logic) return logics;

    --* Casts an [int] to a [logic] bit. 
    --* 
    --* Any number other than 0 corresponds to a [logic] value of '1'.
    function to_logic(num: int) return logic;

    -- function to_signed_logics(num: int; len: pve) return logics;
    -- function to_signed_int(vec: logics) return int;

    --* Resizes the vector by padding zeros.
    --*
    --* If the 'size' is less than the current size of 'vec', it will
    --* truncate the upper bits.
    function zero_extend(vec: logics; size: nat) return logics;

    --* Resizes the vector by sign extending (padding with MSB).
    --*    
    --* If the 'size' is less than the current size of 'vec', it will
    --* truncate the upper bits.
    function sign_extend(vec: logics; size: nat) return logics;

    --* Selects a slice of the 1D vector 'vec' with words of size 'len'.
    function get_slice(vec: logics; i: nat; len: pve; offset: nat := 0) return logics;

    --* Assigns the slice of the 1D vector 'vec' with words of slice'length size.
    function set_slice(vec: logics; i: nat; slice: logics; offset: nat := 0) return logics;

end package;


package body standard is


    function "+"(lhs: logics; rhs: logics) return logics is
        variable max_size : nat;
    begin
        -- take the maximum resize between the two vectors
        max_size := lhs'length;
        if rhs'length > max_size then max_size := rhs'length; end if;
        return logics(resize(unsigned(lhs), max_size) + resize(unsigned(rhs), max_size));
    end function;


    function "-"(lhs: logics; rhs: logics) return logics is
        variable max_size : nat;
    begin
        -- take the maximum resize between the two vectors
        max_size := lhs'length;
        if rhs'length > max_size then max_size := rhs'length; end if;
        return logics(resize(unsigned(lhs), max_size) - resize(unsigned(rhs), max_size));
    end function;


    function "*"(lhs: logics; rhs: logics) return logics is
        variable prod_size : nat;
    begin
        -- returns a vector that is (n+m) bits wide
        return logics(unsigned(lhs) * unsigned(rhs));
    end function;


    function "+"(lhs: logics; rhs: nat) return logics is 
    begin
        return logics(unsigned(lhs) + to_unsigned(rhs, lhs'length));
    end function;


    function "-"(lhs: logics; rhs: nat) return logics is
    begin
        return logics(unsigned(lhs) - to_unsigned(rhs, lhs'length));
    end function;


    function "="(lhs: logics; rhs: nat) return bool is
    begin
        return lhs = logics(to_unsigned(rhs, lhs'length));
    end function;


    function "/="(lhs: logics; rhs: nat) return bool is
    begin
        return lhs /= logics(to_unsigned(rhs, lhs'length));
    end function;

    function ">="(lhs: logics; rhs: nat) return bool is
    begin
        return lhs >= logics(to_unsigned(rhs, lhs'length));
    end function;


    function "+"(lhs: logics; rhs: logic) return logics is
        variable s_vec : logics(0 downto 0);
    begin
        s_vec(0) := rhs;
        return logics(unsigned(lhs) + resize(unsigned(s_vec), lhs'length));
    end function;


    function "-"(lhs: logics; rhs: logic) return logics is
        variable s_vec : logics(0 downto 0);
    begin
        s_vec(0) := rhs;
        return logics(unsigned(lhs) - resize(unsigned(s_vec), lhs'length));
    end function;


    function "sll"(vec: logics; amt: pve) return logics is
        variable vec_v: logics(vec'range);
    begin
        if vec'length = 1 then
            return "0";
        end if;

        vec_v := vec;
        -- shift left logical 'amt' times
        for i in 1 to amt loop
            -- provided with 'to'
            if vec'ascending = true then
                vec_v := vec_v(vec'left+1 to vec'right) & "0";
            -- provided with 'downto'
            else 
                vec_v := vec_v(vec'left-1 downto vec'right) & "0";
            end if;
        end loop;

        return vec_v;
    end function;


    function "srl"(vec: logics; amt: pve) return logics is
        variable vec_v: logics(vec'range);
    begin
        if vec'length = 1 then
            return "0";
        end if;

        vec_v := vec;
        -- shift right logical 'amt' times
        for i in 1 to amt loop
            -- provided with 'to'
            if vec'ascending = true then
                vec_v := "0" & vec_v(vec'left to vec'right-1);
            -- provided with 'downto'
            else 
                vec_v := "0" & vec_v(vec'left downto vec'right+1);
            end if;
        end loop;

        return vec_v;
    end function;


    function "sla"(vec: logics; amt: pve) return logics is
        variable vec_v: logics(vec'range);
    begin
        if vec'length = 1 then
            if vec(0) = '1' then
                return "1";
            else 
                return "0";
            end if;
        end if;

        vec_v := vec;
        -- shift right logical 'amt' times
        for i in 1 to amt loop
            -- provided with 'to'
            if vec'ascending = true then
                vec_v(vec'left to vec'right-1) := vec_v(vec'left+1 to vec'right);
            -- provided with 'downto'
            else 
                vec_v(vec'left downto vec'right+1) := vec_v(vec'left-1 downto vec'right);
            end if;
        end loop;

        return vec_v;
    end function;


    function "sra"(vec: logics; amt: pve) return logics is
        variable vec_v: logics(vec'range);
    begin
        if vec'length = 1 then
            if vec(0) = '1' then
                return "1";
            else 
                return "0";
            end if;
        end if;

        vec_v := vec;
        -- shift right logical 'amt' times
        for i in 1 to amt loop
            -- provided with 'to'
            if vec'ascending = true then
                vec_v(vec'left+1 to vec'right) := vec_v(vec'left to vec'right-1);
            -- provided with 'downto'
            else 
                vec_v(vec'left-1 downto vec'right) := vec_v(vec'left downto vec'right+1);
            end if;
        end loop;

        return vec_v;
    end function;


    function sign_extend(vec: logics; size: nat) return logics is
    begin
        return logics(resize(signed(vec), size));
    end function;


    function zero_extend(vec: logics; size: nat) return logics is
    begin
        return logics(resize(unsigned(vec), size));
    end function;


    function to_int(vec: logics) return nat is
    begin
        return to_integer(unsigned(vec));
    end function;


    function to_logics(num: nat; len: pve) return logics is
    begin
        return logics(to_unsigned(num, len));
    end function;

    
    function to_logic(num: int) return logic is
    begin
        if num = 0 then
            return '0';
        else
            return '1';
        end if;
    end function;


    function as_logics(b: logic) return logics is
        variable vec: logics(0 downto 0);
    begin
        vec(0) := b;
        return vec;
    end function;


    function get_slice(vec: logics; i: nat; len: pve; offset: nat := 0) return logics is
        variable shift    : natural := offset + vec'low;
    begin
        if vec'ascending = true then
            return vec((i*len)+shift to ((i+1)*len)-1+shift);
        end if;
        return vec(((i+1)*len)-1+shift downto (i*len)+shift);
    end function;


    function set_slice(vec: logics; i: nat; slice: logics; offset: nat := 0) return logics is
        variable len       : natural := slice'length;
        variable inner_vec : logics(vec'range) := vec;
        variable shift    : natural := offset + vec'low;
    begin
        if inner_vec'ascending = true then
            inner_vec((i*len)+shift to ((i+1)*len)-1+shift) := slice;
        else 
            inner_vec(((i+1)*len)-1+shift downto (i*len)+shift) := slice;
        end if;
        return inner_vec;
    end function;

    -- function to_signed_int(vec: logics) return nat is
    -- begin
    --     return to_integer(signed(vec));
    -- end function;


    -- function to_signed_logics(num: int; len: pve) return logics is
    -- begin
    --     return logics(to_signed(num, len));
    -- end function;

end package body;