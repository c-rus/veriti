library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity add is
    generic (
        LEN: positive
    );
    port (
        cin: in std_logic;
        in0: in std_logic_vector(LEN-1 downto 0);
        in1: in std_logic_vector(LEN-1 downto 0);
        sum: out std_logic_vector(LEN-1 downto 0);
        cout: out std_logic
    );
end entity;

architecture rtl of add is
    signal result: std_logic_vector(LEN-1+1 downto 0);

    signal cin_i : std_logic_vector(LEN-1 downto 0) := (others => '0');
    signal temp : std_logic_vector(LEN-1+1 downto 0);
begin
    cin_i(0) <= cin;

    -- result <= ("0" & in0) + ("0" & in1);
    -- result <= zero_extend(in0, result'length) + zero_extend(in1, result'length);
    temp <= std_logic_vector(unsigned("0" & in0) + unsigned("0" & in1));
    result <= std_logic_vector(unsigned(temp) + unsigned("0" & cin_i));

    cout <= result(LEN);
    sum <= result(LEN-1 downto 0);

end architecture;