# Project: veriti
# Module: model.py
#
# Defines various class and functions when working with a functional software 
# model for a hardware design.

import random as _random
from enum import Enum as _Enum
from .lib import to_logic, from_logic, pow2m1, pow2
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


class Strategy(_Enum):
    NORMAL = 0,

    @staticmethod
    def from_str(s: str):
        s = s.lower()
        if s == 'normal':
            return Strategy.NORMAL
        else:
            raise Exception('Failed to convert str '+s+' to type Strategy')
    pass


class Distribution:
    import random as _random

    def __init__(self, space, weights=None, partition: bool=True):
        '''
        If `weights` is set to None, then it is assumed to to be uniform distribution
        across the defined elements.

        If `partition` is set to true, it will divide up the total sample space `space`
        into evenly paritioned groups summing to the total number of provided weights.
        '''
        import math as _math

        self._sample_space = space
        self._weights = weights
        # determine if to group the items together in divisible bins w/ weights weights[i]
        self._partition = partition
        self._events_per_weight = 1
        # re-group the items
        self._partitioned_space = self._sample_space
        # print(self._partition)
        if self._partition == True and type(self._weights) != type(None):
            self._partitioned_space = []
            self._events_per_weight = int(_math.ceil(len(self._sample_space) / len(weights)))
            # initialize the bins
            for i, element in enumerate(self._sample_space):
                # group the items together based on a common index that divides them into groups
                i_macro = int(i / self._events_per_weight)
                #print(i_macro)
                if len(self._partitioned_space) <= i_macro:
                    self._partitioned_space.append([])
                    pass
                self._partitioned_space[i_macro] += [element]
                pass
        pass


    def samples(self, k=1):
        '''
        Produce a sample from the known distribution.
        '''
        outcomes = _random.choices(population=self._partitioned_space, weights=self._weights, k=k)
        results = []
        for event in outcomes:
            # unfold inner lists and ranges
            while type(event) == range or type(event) == list:
                event = _random.choice(event)
            results += [event]
        return results
    pass


class Signal:

    def __init__(self, width: int=None, mode: Mode=Mode.INFER, value=0, endianness: str='big', name: str=None, dist: Distribution=None):
        '''
        Create a new Signal instance.

        ### Parameters
        - The `width` parameter determines the number of bits in the signal. If set to None, then it will be 1 bit wide.

        - The `mode` parameter determines what type of direction the signal should be. When set to INFER, the mode is resolved
        based what mode the corresponding signal name is in the hardware language based on reading json data with this information.
        
        - The `value` parameter determines the initial value for the signal.

        - The `endianness` parameter can be set to 'big' or 'little' to determine the endianness of the data. Big endianness
        corresponds to having the most-significant bit be first in the sequence, while little endianness corresponds to
        having the least-significant bit be first in the sequence.

        - The `name` parameter can be used to explicitly set the signal's name when searching for the hardware language's equivalent signal.
        If this is set to None, then it uses this instance's name in the Python code as the name.

        - The `dist` parameter can either be a list of probabilities or a Distribution instance. When `dist` is
        a list, it will use this instance's minimum and maximum values as the range for the sample space and partition
        accordingly based on the number of weights.
        '''

        self._mode = mode if isinstance(mode, str) == False else Mode.from_str(mode)

        self._width = width if width != None else 1
        if self._width <= 0:
            raise Exception('Signal cannot have width less than or equal to 0')
        
        # specify the order of the bits (big-endian is MSB first)
        if endianness != 'big' and endianness != 'little':
            raise Exception("Signal must either have 'big' or 'little' endianness")
        
        self._big_endian = str(endianness).lower() == 'big'

        # provide an initialized value
        self._value = 0
        self.set(value, is_signed=False)

        # provide an explicit name to search up in design interface
        self._name = name

        # provide explicit distribution of values for sampling
        self._dist = dist
        if type(self._dist) == list:
            self._dist = Distribution(space=[*range(self.min(), self.max())], weights=dist, partition=True)
            pass
        pass


    def get_width(self) -> int:
        '''
        Accesses the number of bits set for this signal.
        '''
        return self._width
    

    def get_mode(self) -> Mode:
        '''
        Returns the type of port the signal is.
        '''
        return self._mode
    

    def get_range(self) -> range:
        '''
        Returns the range of possible values for the specified bit width.
        
        The start is inclusive and the end is exclusive.
        '''
        return range(self.min(), pow2(self.get_width()))


    def max(self) -> int:
        '''
        Returns the maximum possible integer value stored in the allotted bits
        (inclusive).
        '''
        return pow2m1(self.get_width())
    

    def min(self) -> int:
        '''
        Returns the minimum possible integer value stored in the allotted bits 
        (inclusive).
        '''
        return 0
    

    def rand(self):
        '''
        Sets the data to a random value based on its distribution.

        If no distribution was defined for the Signal, it wil use a uniform
        distribution across the minimum and maximum values, inclusively.
        '''
        # provide uniform distribution when no distribution is defined for the signal
        if self._dist == None:
            self._value = _random.randint(self.min(), self.max())
        else:
            self._value = self._dist.samples(k=1)[0]
        # ensure the selected data is allowed and in bounds
        if self._value < self.min() or self._value > self.max():
            raise Exception("Value out of bounds")
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
        return to_logic(self.as_int(), self.get_width(), big_endian=self._big_endian)
    

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
            # ensure the selected data is allowed and in bounds
            if int(num) < self.min() or int(num) > self.max():
                raise Exception("Value out of bounds")
            self._value = num % (self.max() + 1)
        elif type(num) == str:
            if len(str(num)) > self.get_width():
                raise Exception("Value out of bounds")
            # make sure to put into big-endianness first
            if self._big_endian == False:
                # reverse endianness to be MSB first
                num = num[::-1]
            if self.get_width() < len(num):
                # use the rightmost bits (if applicable)
                num = num[len(num)-self.get_width():]
            self._value = from_logic(num, is_signed)
        else:
            raise Exception("Cannot set signal with type "+str(type(num)))

    
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
    

    def __int__(self):
        return self.as_int()
    
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
        use_mode = Mode.from_str(config.Config().get_port(index)['mode']) if sig.get_mode() == Mode.INFER else sig.get_mode()
        if use_mode != mode:
            continue
        results += [(index, key, sig)]
        pass

    results.sort()
    # store tuple with (name, signal)
    results = [(x[1], x[2]) for x in results]
    return results


def randomize(model, strategy: str=None):
    '''
    Generates random input values for each attribute for the BFM. This is
    a convenience function for individually setting each signal randomly.

    This function mutates the object `model` and returns a reference to the same object.

    A strategy can be provided to provide coverage-driven input test vectors.
    '''
    sig: Signal
    for (_, sig) in get_ports(model, mode=Mode.IN):
        sig.rand()
        pass
    return model


import unittest as _ut

class __Test(_ut.TestCase):

    def test_new_dist(self):
        dist = Distribution([0, pow2m1(4), range(1, pow2m1(4)-1)], weights=[0.1, 0.1, 0.8])

        freqs = dict()
        for i in range(1_000):
            sample = dist.samples()[0]
            if sample == 0:
                if 'min' not in freqs.keys():
                    freqs['min'] = 0
                freqs['min'] += 1
            elif sample == pow2m1(4):
                if 'max' not in freqs.keys():
                    freqs['max'] = 0
                freqs['max'] += 1
            else:
                if 'middle' not in freqs.keys():
                    freqs['middle'] = 0
                freqs['middle'] += 1

        # Uncomment to view frequencies for manual verification
        # print(freqs)
        # self.assertEqual(1, 0)
        pass

    def test_uniform_dist(self):
        dist = Distribution([*range(2**4)], weights=[1/16] * 16)

        freqs = dict()
        for i in range(10_000):
            sample = dist.samples()[0]
            if sample not in freqs.keys():
                freqs[sample] = 0
            freqs[sample] += 1

        # Uncomment to view frequencies for manual verification
        # print(freqs)
        # self.assertEqual(1, 0)
        pass

    def test_as_logic(self):
        s = Signal(width=4, value="1000", endianness='big')
        self.assertEqual(s.as_logic(), "1000")

        s = Signal(width=4, value=2, endianness='big')
        self.assertEqual(s.as_logic(), "0010")

        s = Signal(width=4, value="1000", endianness='little')
        self.assertEqual(s.as_logic(), "1000")

        s = Signal(width=4, value=2, endianness='little')
        self.assertEqual(s.as_logic(), "0100")
        pass

    def test_index_bit(self):
        s = Signal(width=4, value="1000", endianness='big')
        self.assertEqual(s[0], '0')
        self.assertEqual(s[3], '1')

        s = Signal(width=4, value=2, endianness='big')
        self.assertEqual(s[1], '1')

        s = Signal(width=4, value="1000", endianness='little')
        self.assertEqual(s[0], '1')

        s = Signal(width=4, value=2, endianness='little')
        self.assertEqual(s[1], '1')
        pass

    def test_modify_index_bit(self):
        s = Signal(width=4, value="0000", endianness='big')
        s[3] = '1'
        self.assertEqual(s[3], '1')
        self.assertEqual(s.as_logic(), "1000")
        self.assertEqual(s.as_int(), 8)

        s = Signal(width=4, value=0, endianness='big')
        s[1] = '1'
        self.assertEqual(s.as_logic(), "0010")
        self.assertEqual(s.as_int(), 2)

        s = Signal(width=4, value="0000", endianness='little')
        s[3] = '1'
        self.assertEqual(s[3], '1')
        self.assertEqual(s.as_logic(), "0001")
        self.assertEqual(s.as_int(), 8)

        s = Signal(width=4, value=0, endianness='little')
        s[1] = '1'
        self.assertEqual(s.as_logic(), "0100")
        self.assertEqual(s.as_int(), 2)
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

        s = Signal(width=4, value="0000", endianness='big')
        s.set_bit(0, '1')
        self.assertEqual('1', s[0])
        s.set_bit(2, '1')
        self.assertEqual('1', s[2])
        self.assertEqual("0101", str(s))

        s = Signal(width=4, value="0000", endianness='little')
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