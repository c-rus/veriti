# Project: veriti
# Module: model.py
#
# Defines various class and functions when working with a functional software 
# model for a hardware design.

import random as _random
from enum import Enum as _Enum
from .lib import to_logic, from_logic, pow2m1
from . import config


class Mode(_Enum):
    IN  = 0
    OUT = 1
    INOUT  = 2
    LOCAL  = 3
    # allow the interface data to decide what mode this signal is
    INFER = 4

    @staticmethod
    def from_str(s: str):
        s = s.lower()
        if s == 'in':
            return Mode.IN
        elif s == 'out':
            return Mode.OUT
        elif s == 'inout':
            return Mode.INOUT
        elif s == 'local':
            return Mode.LOCAL
        else:
            raise Exception('Failed to convert str '+s+' to type Mode')
    pass


class Signal:

    def __init__(self, width: int=None, mode: Mode=Mode.INFER, value=0, big_endian:bool=True, name: str=None):
        self._mode = mode
        self._width = width if width != None else 1
        if self._width <= 0:
            print('warning: Signal cannot have width less than or equal to 0')
            self._width = 1
        # provide an initialized value
        self._value = 0
        # specify the order of the bits (big-endian is MSB first)
        self._big_endian = big_endian

        self.set(value, is_signed=False)
        # provide an explicit name to search up in design interface
        self._name = name
        pass


    def mode(self) -> Mode:
        '''
        Returns the type of port the signal is.
        '''
        return self._mode


    def max(self) -> int:
        '''
        Returns the maximum possible integer value stored in the allotted bits
        (inclusive).
        '''
        return pow2m1(self.width())
    

    def min(self) -> int:
        '''
        Returns the minimum possible integer value stored in the allotted bits 
        (inclusive).
        '''
        return 0
    

    def width(self) -> int:
        '''
        Accesses the number of bits set for this signal.
        '''
        return self._width
    

    def rand(self):
        '''
        Sets the data to a random value between 'min()' and 'max()', inclusively.
        '''
        self._value = _random.randint(self.min(), self.max())
        return self
    

    def as_int(self) -> int:
        '''
        Accesses the inner data value stored as an integer.
        '''
        return self._value
    

    def as_logic(self) -> str:
        '''
        Casts the data into a series of 1's and 0's in a string. 
        
        If the signal is 'big-endian', then the MSB is first in the sequence. 
        Otherwise, the LSB is first in the sequence.
        '''
        return to_logic(self.as_int(), self.width(), big_endian=self._big_endian)
    

    def set(self, num, is_signed=False):
        '''
        Sets the data to the specified 'num' and according to its data type. 
        
        - If the type is `int`: This function ensures the data is within the 
        'max()' value by using the modulo operator.
        - If the type is `str`: This function will truncate the MSB (left-side) 
        bits from the vector if necessary to make the conversion fit within the 
        'max()' value.
        - Otherwise: the function will print a warning statement
        '''
        if type(num) == int:
            self._value = num % (self.max() + 1)
        elif type(num) == str:
            # make sure to put into big-endianness first
            if self._big_endian == False:
                # reverse endianness to be MSB first
                num = num[::-1]
            if self.width() < len(num):
                # use the rightmost bits (if applicable)
                num = num[len(num)-self.width():]
            self._value = from_logic(num, is_signed)
        else:
            print('WARNING: Invalid type attempting to set signal value')

    
    def set_bit(self, index: int, bit):
        '''
        Modify the bit at `index` in the vector. 
        
        Signals that are not 'big-endian' will count the vector from left to right, 
        0 to len-1. Signals that are 'big-endian' will the count the vector right 
        to left.
        '''
        self.__setitem__(index, bit)
        pass


    def get_bit(self, index: int) -> str:
        '''
        Access the bit at `index` in the vector.

        Signals that are not 'big-endian' will count the vector from left to right, 
        0 to len-1. Signals that are 'big-endian' will the count the vector right 
        to left.
        '''
        return self[index]
        

    def __eq__(self, other):
        if isinstance(other, Signal):
            return self.__key() == other.__key()
        return NotImplemented
    

    def __key(self):
        return (self._width, self._value)


    def __hash__(self):
        return hash(self.__key())


    def __getitem__(self, key: int) -> str:
        vec = self.as_logic()
        # reverse to count from 0 to width-1
        if self._big_endian == True:
            vec = vec[::-1]
        return vec[key]
    

    def __setitem__(self, key: int, value: str):
        new_val: str = '1' if int(value) == 1 else '0'
        vec = self.as_logic()
        # reverse to count from 0 to width-1
        if self._big_endian == True:
            vec = vec[::-1]
        result = ''

        for i, bit in enumerate(vec):
            if key == i:
                result += new_val
            else:
                result += bit
        # reverse back
        if self._big_endian == True:
            result = result[::-1]
        self.set(result)
        pass


    def __str__(self):
        return self.as_logic()
    
    pass


def __compile_ports(model):
    '''
    Compiles the list of ports into a mapping where the 'key' is the defined name
    and the 'value' is a tuple (Signal, Dict).
    '''
    # save computations
    if hasattr(model, '__veriti_cached_ports') == True:
        return model.__veriti_cached_ports
    
    model.__veriti_cached_ports = dict()
    for (key, val) in vars(model).items():
        # only python variables declared as signals can be a port
        if isinstance(val, Signal) == False:
            continue
        # override variable name with explicit name provided
        defined_name = key if val._name == None else val._name
        # check if the name is in the port interface data
        loc = config.Config().locate_port(defined_name)
        if loc != -1:
            # store the interface data and the signal data together
            model.__veriti_cached_ports[defined_name] = (val, loc)
        pass
    return model.__veriti_cached_ports
    

def get_ports(model, mode: Mode):
    '''
    Collects the attributes defined in the `model` into a list storing
    the tuples of their (name, signal).
    '''
    results = []

    key: str
    sig: Signal
    index: int
    for (key, (sig, index)) in __compile_ports(model).items():
        use_mode = Mode.from_str(config.Config().get_port(index)['mode']) if sig.mode() == Mode.INFER else sig.mode()
        if use_mode != mode:
            continue
        results += [(index, key, sig)]
        pass

    results.sort()
    # store tuple with (name, signal)
    results = [(x[1], x[2]) for x in results]
    return results


def randomize(model):
    '''
    Generates random input values for each attribute for the BFM. This is
    a convenience function for individually setting each signal randomly.
    '''
    sig: Signal
    for (_, sig) in get_ports(model, mode=Mode.IN):
        sig.rand()
        pass
    return model


import unittest as _ut

class __Test(_ut.TestCase):


    def test_as_logic(self):
        s = Signal(width=4, value="1000", big_endian=True)
        self.assertEqual(s.as_logic(), "1000")

        s = Signal(width=4, value=2, big_endian=True)
        self.assertEqual(s.as_logic(), "0010")

        s = Signal(width=4, value="1000", big_endian=False)
        self.assertEqual(s.as_logic(), "1000")

        s = Signal(width=4, value=2, big_endian=False)
        self.assertEqual(s.as_logic(), "0100")
        pass


    def test_index_bit(self):
        s = Signal(width=4, value="1000", big_endian=True)
        self.assertEqual(s[0], '0')
        self.assertEqual(s[3], '1')

        s = Signal(width=4, value=2, big_endian=True)
        self.assertEqual(s[1], '1')

        s = Signal(width=4, value="1000", big_endian=False)
        self.assertEqual(s[0], '1')

        s = Signal(width=4, value=2, big_endian=False)
        self.assertEqual(s[1], '1')
        pass


    def test_modify_index_bit(self):
        s = Signal(width=4, value="0000", big_endian=True)
        s[3] = '1'
        self.assertEqual(s[3], '1')
        self.assertEqual(s.as_logic(), "1000")
        self.assertEqual(s.as_int(), 8)

        s = Signal(width=4, value=0, big_endian=True)
        s[1] = '1'
        self.assertEqual(s.as_logic(), "0010")
        self.assertEqual(s.as_int(), 2)

        s = Signal(width=4, value="0000", big_endian=False)
        s[3] = '1'
        self.assertEqual(s[3], '1')
        self.assertEqual(s.as_logic(), "0001")
        self.assertEqual(s.as_int(), 8)

        s = Signal(width=4, value=0, big_endian=False)
        s[1] = '1'
        self.assertEqual(s.as_logic(), "0100")
        self.assertEqual(s.as_int(), 2)
        pass


    def test_set_bit(self):

        pass

    def test_bit_access(self):
        s = Signal(width=4, value="1010")
        self.assertEqual('1', s[1])
        self.assertEqual('0', s[0])
        self.assertEqual('0', s[2])
        self.assertEqual('1', s[3])
        pass




    def test_bit_modify(self):
        s = Signal(width=4, value="1010")
        self.assertEqual('0', s[0])
        s[0] = '1'
        self.assertEqual('1', s[0])

        self.assertEqual('1', s[3])
        s[3] = '0'
        self.assertEqual('0', s[3])
        pass
    

    def test_set_bit(self):
        s = Signal(width=4, value="0000")
        s.set_bit(0, '1')
        self.assertEqual('0', s.as_logic()[0])
        self.assertEqual('1', s.as_logic()[3])
        s.set_bit(3, '1')
        self.assertEqual('1', s.as_logic()[3])
        self.assertEqual('1', s.as_logic()[0])

        s = Signal(width=4, value="0000", big_endian=True)
        s.set_bit(0, '1')
        self.assertEqual('1', s[0])
        s.set_bit(2, '1')
        self.assertEqual('1', s[2])
        self.assertEqual("0101", str(s))

        s = Signal(width=4, value="0000", big_endian=False)
        s.set_bit(0, '1')
        self.assertEqual('1', s[0])
        s.set_bit(2, '1')
        self.assertEqual('1', s[2])
        self.assertEqual("1010", str(s))
        pass

    def test_get_bit(self):
        s = Signal(width=4, value="0010")
        self.assertEqual('1', s.get_bit(1))

        s = Signal(width=4, value="1000")
        self.assertEqual('1', s.get_bit(3))

        s = Signal(width=5, value="11110")
        self.assertEqual('0', s.get_bit(0))
        self.assertEqual('1', s.get_bit(4))
        pass
    pass