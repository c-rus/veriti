# File: lib.py
# Author: Chase Ruskin
# Created: 2023-12-17
# Details:
#   Implements basic functions re-used across the library and throughout
#   software modelling.
#

import math as _math
import argparse as _argparse
from . import config

# --- Classes and Functions ----------------------------------------------------

def set(design_if: str=None, bench_if: str=None, work_dir: str=None, seed: int=None, generics=[]):
    # grab singleton object
    state = config.Config()

    # read from testbench interface data
    if bench_if != None:
        state.read_bench_if(bench_if)
    # read from design interface data
    if design_if != None:
        state.read_design_if(design_if)

    if seed != None:
        state._seed = int(seed)
    if work_dir != None:
        state._working_dir = str(work_dir)

    # update to generics mapping
    for g in generics:
        state._gens[g.key] = g.val
    
    state._initialized = True
    pass


def get_generic(key: str, type=None, default=None):
    '''
    Accesses the generic based upon the provided `key`.

    Define a type to help with converting to a Python-friendly datatype, as all
    generics are initially stored as `str`.
    '''
    from . import cast
    # verify the key exists
    if key in config.Config()._gens:
        value = config.Config()._gens[key]
    else:
        return default
    if type == int:
        value = cast.from_vhdl_int(value)
    elif type == bool:
        value = cast.from_vhdl_bool(value)
    elif type == str:
        value = cast.from_vhdl_str(value)
    elif type == [int]:
        value = cast.from_vhdl_ints(value)
    elif type == [bool]:
        value = cast.from_vhdl_bools(value)
    elif type == [str]:
        value = cast.from_vhdl_strs(value)
    else:
        print('warning: Unsupported casting to type:', type)
        # do nothing
        pass
    return value


def seed(default: int=None) -> int:
    '''
    Set and get a seed integer value and initializes the random number generator.

    Parses command-line arguments for '--seed' [SEED]. If [SEED] is not given, then
    `None` will be returned. If '--seed' is not given, then the `default` will be
    returned.

    Once the seed as been set (by this function call), it cannot be overridden.
    '''
    import sys, random
    if config.Config()._seed == None:
        config.Config()._seed = default
    # set the seed value
    if config.Config()._seed == None:
        config.Config()._seed = random.randrange(sys.maxsize)
    # initialize the random state
    return config.Config()._seed


def pow2m1(width: int):
    '''
    Computes the following formula: `2^(width)-1`   
    '''
    return (2**width)-1


def pow(base: int, exp: int):
    '''
    Computes the followng formula: `base^exp`
    '''
    return base**exp


def to_logic(n, width: int=None, trunc: bool=True, big_endian=True) -> str:
    '''
    Converts the integer `n` to a binary string.

    If `n` is negative, the two's complement representation will be returned.
    When translating a list, the 0th index corresponds to the LSB when `big_endian`
    is set to true. In other words, big-endianness will assume the `n[0]` is the LSB.

    ### Parameters
    - `n`: integer number or list of 1s and 0s to transform
    - `width`: specify the number of bits (never truncates) 
    - `trunc`: trim upper-most bits if width is less than required bit count
    - `big_endian`: if true, store MSB bit first (LHS) in the sequence

    ### Returns
    - `str` of 1's and 0's
    '''
    logic_vec = ''
    # handle vector of ints (1s and 0s)
    if isinstance(n, list) == True:
        for bit in n: logic_vec += str(bit)
        # flip to default big-endianness
        logic_vec = logic_vec[::-1]
        if width is None:
            width = len(n)
    # handle pure integer values
    elif isinstance(n, int) == True:
        bin_str = bin(n)
        is_negative = bin_str[0] == '-'
        # auto-define a width
        if width == None:
            width = 1 if n == 0 else _math.ceil(_math.log(abs(n) + 0.5, 2))
            # extend to use negative MSB
            if is_negative == True:
                width += 1
        # compute 2's complement representation
        if is_negative == True:
            bin_str = bin(2**width + n)
        # assign to outer variable
        logic_vec = bin_str[2:]
        pass
    
    # fill with zeros on the left depending on 'width' (never truncates)
    logic_vec = logic_vec.zfill(width)

    # truncate upper bits
    if trunc == True and width < len(logic_vec):
        logic_vec = logic_vec[len(logic_vec)-width:]

    # flip based on endianness
    if big_endian == False:
        logic_vec = logic_vec[::-1]

    return logic_vec


def from_logic(b: str, signed: bool=False) -> int:
    '''
    Converts the binary string `b` to an integer representation.
    
    ### Parameters
    - `b`: binary string to convert (example: '011101')
    - `signed`: apply two's complement when MSB = '1' during conversion

    ### Returns
    - `b` as integer form (decimal)
    '''
    if signed == True and b[0] == '1':
        # flip all bits
        flipped = ''
        for bit in b: flipped += str(int(bit, base=2) ^ 1)
        return (int('0b'+flipped, base=2)+1) * -1
    else:
        return int('0b'+b, base=2)


# --- Tests --------------------------------------------------------------------
import unittest as _ut

class __Test(_ut.TestCase):

    def test_to_logic_using_int(self):
        self.assertEqual('001', to_logic(1, width=3))

        self.assertEqual('10', to_logic(2))

        self.assertEqual('1011', to_logic(-5))

        self.assertEqual('101', to_logic(5))

        self.assertEqual('0', to_logic(0))

        self.assertEqual('11', to_logic(-1))

        self.assertEqual('01111', to_logic(15, 5))
        # truncate upper bits to keep lower 2 bits
        self.assertEqual('11', to_logic(15, width=2, trunc=True))
        # keep upper two bits
        self.assertEqual('00', to_logic(3, width=4)[:2])
        # represent a number that requires more than 32 bits
        self.assertEqual('100000000000000000000000000000000', to_logic(2**32))

        self.assertEqual('011', to_logic(6, big_endian=False))

        self.assertEqual('110', to_logic(6, big_endian=True))

        self.assertEqual('01', to_logic(6, width=2, big_endian=False))
        pass


    def test_to_logic_using_list(self):
        vec = [0, 1, 1, 0]
        self.assertEqual(to_logic(vec), '0110')

        vec = [1, 1, 1, 0, 0, 0]
        self.assertEqual(to_logic(vec), '000111')

        vec = [1, 1, 1, 0, 0, 0]
        self.assertEqual(to_logic(vec, big_endian=False), '111000')

        vec = [1, 0, 1, 0]
        self.assertEqual(to_logic(vec, width=3), '101')

        vec = [1, 1, 0, 0, 1]
        self.assertEqual(to_logic(vec, width=2, big_endian=False), '11')
        pass


    def test_from_logic(self):
        self.assertEqual(10, from_logic('1010'))

        self.assertEqual(-6, from_logic('1010', signed=True))

        self.assertEqual(5, from_logic('00000101'))
        pass


    def test_pow2m1(self):
        self.assertEqual(pow2m1(0), 0)

        self.assertEqual(pow2m1(1), 1)

        self.assertEqual(pow2m1(3), 7)

        self.assertEqual(pow2m1(4), 15)

        self.assertEqual(pow2m1(8), 255)
        pass


    def test_pow(self):
        self.assertEqual(pow(3, 4), 81)
        pass

    pass
