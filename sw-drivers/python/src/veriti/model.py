from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
import random as _random
from typing import Tuple as _Tuple
from enum import Enum as _Enum
from .lib import to_logic, from_logic, pow2m1

class Mode(_Enum):
    INPUT  = 0
    OUTPUT = 1
    INOUT  = 2
    LOCAL  = 3
    pass


class Signal:

    def __init__(self, mode: Mode=Mode.LOCAL, width: int=None, value=0, downto: _Tuple[str, str]=None, to: _Tuple[str, str]=None):
        self._mode = mode
        self._is_single = True if width == None else False
        self._width = width if width != None else 1
        if self._width <= 0:
            print('WARNING: Signal cannot have width less than or equal to 0')
        self._value = 0
        self.set(value)
        # store values for writing the VHDL record
        self._downto = downto
        self._to = to
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
    

    def is_single_ended(self):
        '''
        Checks if the signal is not an array-type.
        '''
        return self._is_single
    

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
        Casts the data into a series of 1's and 0's in a string. The MSB
        is represented on the LHS (index 0).
        '''
        return to_logic(self.as_int(), self.width())
    

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
            if self.width() < len(num):
                # use the rightmost bits (if applicable)
                num = num[len(num)-self.width():]
            self._value = from_logic(num, is_signed)
        else:
            print('WARNING: Invalid type attempting to set signal value')

    
    def set_bit(self, index: int, bit, downto: bool=True):
        '''
        Modify the bit at `index` in the vector. 
        
        Setting `downto` to false will count the vector from left to right, 
        0 to len-1. Setting `downto` to true will the count the vector right 
        to left.
        '''
        diff: int = 2*index if downto == False else self.width()-1
        bit: str = '1' if int(bit) == 1 else '0'

        result = ''
        for i, elem in enumerate(self.as_logic()):
            if diff-index == i:
                result += bit
            else:
                result += elem
        self.set(result)
        pass


    def get_bit(self, index: int, downto: bool=True) -> str:
        '''
        Access the bit at `index` in the vector.

        Setting `downto` to false will count the vector from left to right, 
        0 to len-1. Setting `downto` to true will the count the vector right 
        to left.
        '''
        diff: int = 2*index if downto == False else self.width()-1
        return self.as_logic()[diff-index]
        

    def __eq__(self, other):
        if isinstance(other, Signal):
            return self.__key() == other.__key()
        return NotImplemented
    

    def __key(self):
        return (self._width, self._value, self._is_single)


    def __hash__(self):
        return hash(self.__key())


    def __getitem__(self, key: int) -> str:
        return self.as_logic()[self.width()-key-1]
    

    def __setitem__(self, key: int, value: str):
        result = ''
        for i, bit in enumerate(self.as_logic()):
            if self.width()-key-1 == i:
                result += value
            else:
                result += bit
        self.set(result)
        pass

    pass


class SuperBfm(_ABC):        
    '''
    Returns the name for the entity being tested. 
    
    This name will appear in the generated VHDL code. By default it is `uut`.
    '''
    entity = None

    @_abstractmethod
    def __init__(self):
        '''
        Defines the available signals along with their widths and default values.

        The order the signals are specified is not necessarily the order they
        are written/read to/from the test vector files.
        '''
        pass


    def send(self, fd, mode: Mode):
        '''
        Format the signals as logic values in the file `fd` to be read in during
        simulation.

        The format uses commas (`,`) to separate different signals and the order of signals
        written matches the order of instance variables in the declared class.

        Each value is written with a ',' after the preceeding value in the 
        argument list. A newline is formed after all arguments
        '''
        DELIM = ','
        port: Signal
        for _key, port in self.get_ports(mode=mode):
            # write to the file
            fd.write(port.as_logic()+DELIM)
        # finish the transaction with a newline
        fd.write('\n')
        pass


    def get_ports(self, mode: Mode):
        '''
        Collects the attributes defined in the subclass into a list storing
        the tuples.

        Collects all signals tied to the Bfm if `mode` is set to `None`.
        '''
        result = []
        for (key, val) in vars(self).items():
            # filter out items to be left with only the defined attributes
            if key.startswith('_') == True or isinstance(val, Signal) == False:
                continue
            val: Signal
            # only add signals with the correct direction
            if val.mode() == mode or mode is None:
                result += [(key, val)]
        return result
    

    def _get_entity(self) -> str:
        return 'uut' if self.entity is None else str(self.entity)
    

    def _identify_port_types(self, top: str=None):
        '''
        Calls 'Orbit' to get the list of ports as signals to generate record.

        Returns a dictionary of the list of ports and their respective VHDL types.
        '''
        import subprocess, os
        sigs = dict()
        TOP = top if top != None else os.environ.get('ORBIT_TOP')
        # check if a testbench is provided
        if TOP == None:
            print('WARNING: No signals to extract because no entity is set')
        
        # grab default values from testbench
        command_success = True
        try:
            signals = subprocess.check_output(['orbit', 'get', TOP, '--signals']).decode('utf-8').strip()
        except:
            print('WARNING: Failed to extract signals from entity \''+TOP+'\'')
            command_success = False

        # act on the data returned from `Orbit` if successfully ran
        if command_success == True:
            # filter for signals
            sig_code = []
            line: str
            for line in signals.splitlines():
                i = line.find('signal ')
                if i > -1 :
                    sig_code += [line[i+len('signal '):line.find(';')]]

            # extract the constant name
            sig: str
            for sig in sig_code:
                # identify name
                name = sig[:sig.find(' ')]
                sigs[name] = None
                # identify the datatype
                d_type = sig.find(':')
                if d_type > -1:
                    sigs[name] = sig[d_type:sig.find(':=')+1 if sig.find(':=') > -1 else len(sig)]
            pass
        return sigs


    def rand(self):
        '''
        Generates random input values for each attribute for the BFM. This is
        a convenience function for individually setting each signal randomly.
        '''
        port: Signal
        for (id, port) in self.get_ports(mode=Mode.INPUT):
            self.__dict__[id] = Signal(port.mode(), port.width() if port.is_single_ended() == False else None).rand()
        return self
    

    @_abstractmethod
    def model(self, *args):
        pass

    pass


class InputFile:
    def __init__(self, fname: str='inputs.dat', mode='w', verbose=False):
        '''
        Creates an input test vector file in write mode.
        '''
        self._file = open(fname, mode)
        self._verbose = verbose
        self._empty = True
        pass


    def write(self, bfm: SuperBfm):
        '''
        Writes the inputs of the bus functional model to the input test vector file.
        '''
        if issubclass(type(bfm), SuperBfm) == True:
            if self._verbose == True and self._empty == True:
                self._file.write('# ')
                for io in bfm.get_ports(mode=Mode.INPUT):
                    self._file.write(str(io[0]) + ', ')
                self._file.write('\n')
                pass
            bfm.send(self._file, mode=Mode.INPUT)
            self._empty = False
        else:
            print('WARNING: Tried to write invalid type to input test vector file')
    pass


class OutputFile:
    def __init__(self, fname: str='outputs.dat', mode='w', verbose=False):
        '''
        Creates an output test vector file in write mode.
        '''
        self._file = open(fname, mode)
        self._verbose = verbose
        self._empty = True


    def write(self, bfm: SuperBfm):
        '''
        Writes the outputs of the bus funcitonal model to the output test vector file.
        '''
        if issubclass(type(bfm), SuperBfm):
            if self._verbose == True and self._empty == True:
                self._file.write('# ')
                for io in bfm.get_ports(mode=Mode.OUTPUT):
                    self._file.write(str(io[0]) + ', ')
                self._file.write('\n')
                pass
            bfm.send(self._file, mode=Mode.OUTPUT)
        else:
            print('WARNING: Tried to write invalid type to output test vector file')
    pass


# --- Tests --------------------------------------------------------------------
import unittest as _ut

class __Test(_ut.TestCase):

    def test_bit_access(self):
        s = Signal(width=4, value="1010")

        self.assertEqual('1', s[1])
        self.assertEqual('0', s[0])
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
        self.assertEqual('1', s.as_logic()[3])
        s.set_bit(3, '1')
        self.assertEqual('1', s.as_logic()[0])

        s = Signal(width=4, value="0000")
        s.set_bit(0, '1', downto=False)
        self.assertEqual('1', s.as_logic()[0])
        s.set_bit(3, '1', downto=False)
        self.assertEqual('1', s.as_logic()[3])
        pass

    def test_get_bit(self):
        s = Signal(width=4, value="0010")
        self.assertEqual('1', s.get_bit(1, downto=True))
        self.assertEqual('1', s.get_bit(2, downto=False))

        s = Signal(width=4, value="1000")
        self.assertEqual('1', s.get_bit(3, downto=True))
        self.assertEqual('1', s.get_bit(0, downto=False))

        s = Signal(width=5, value="11110")
        self.assertEqual('0', s.get_bit(0, downto=True))
        self.assertEqual('0', s.get_bit(4, downto=False))
        pass
    pass