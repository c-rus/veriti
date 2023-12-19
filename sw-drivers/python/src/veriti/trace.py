from .model import SuperBfm as _SuperBfm
from .model import Mode as _Mode
from .config import TRACE_FILE_EXT

class InputFile:

    def __init__(self, fname: str='inputs'+TRACE_FILE_EXT, mode='w', verbose=False):
        '''
        Creates an input test vector file in write mode.
        '''
        self._file = open(fname, mode)
        self._verbose = verbose
        self._empty = True
        pass


    def write(self, bfm: _SuperBfm):
        '''
        Writes the inputs of the bus functional model to the input test vector file.
        '''
        if issubclass(type(bfm), _SuperBfm) == True:
            if self._verbose == True and self._empty == True:
                self._file.write('# ')
                for io in bfm.get_ports(mode=_Mode.INPUT):
                    self._file.write(str(io[0]) + ', ')
                self._file.write('\n')
                pass
            bfm.send(self._file, mode=_Mode.INPUT)
            self._empty = False
        else:
            print('WARNING: Tried to write invalid type to input test vector file')
    pass


class OutputFile:
    def __init__(self, fname: str='outputs'+TRACE_FILE_EXT, mode='w', verbose=False):
        '''
        Creates an output test vector file in write mode.
        '''
        self._file = open(fname, mode)
        self._verbose = verbose
        self._empty = True


    def write(self, bfm: _SuperBfm):
        '''
        Writes the outputs of the bus funcitonal model to the output test vector file.
        '''
        if issubclass(type(bfm), _SuperBfm):
            if self._verbose == True and self._empty == True:
                self._file.write('# ')
                for io in bfm.get_ports(mode=_Mode.OUTPUT):
                    self._file.write(str(io[0]) + ', ')
                self._file.write('\n')
                pass
            bfm.send(self._file, mode=_Mode.OUTPUT)
        else:
            print('WARNING: Tried to write invalid type to output test vector file')
    pass