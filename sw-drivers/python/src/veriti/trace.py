from . import model
from . import config


class InputTrace:

    def __init__(self, fname: str='inputs'+config.TRACE_FILE_EXT, mode='w', verbose=False):
        '''
        Creates an input test vector file in write mode.
        '''
        import os
        self._path = os.path.join(config.Config()._working_dir, fname)
        # create a new file
        open(self._path, 'w').close()
        self._verbose = verbose
        self._empty = True
        pass


    def append(self, bfm: model.SuperBfm):
        '''
        Writes the inputs of the bus funcitonal model to the output test vector file.

        Format each signals as logic values in the file to be read in during
        simulation.

        The format uses commas (`,`) to separate different signals and the order of signals
        written matches the order of ports in the interface json data.

        Each value is written with a ',' after the preceeding value in the 
        argument list. A newline is formed after all arguments
        '''
        DELIM = ','
        NEWLINE = '\n'
        if issubclass(type(bfm), model.SuperBfm):
            with open(self._path, 'a') as fd:
                ports = bfm.get_ports(mode=model.Mode.INPUT)
                for (_name, port) in ports:
                    fd.write(str(port.as_logic()) + DELIM)
                fd.write(NEWLINE)
                pass
            pass
        else:
            print('warning: Tried to write invalid type to output test vector file')
        pass

    pass


class OutputTrace:
    def __init__(self, fname: str='outputs'+config.TRACE_FILE_EXT, mode='w', verbose=False):
        '''
        Creates an output test vector file in write mode.
        '''
        import os
        self._path = os.path.join(config.Config()._working_dir, fname)
        # create a new file
        open(self._path, 'w').close()
        self._verbose = verbose
        self._empty = True
        pass


    def append(self, bfm: model.SuperBfm):
        '''
        Writes the outputs of the bus funcitonal model to the output test vector file.

        Format each signals as logic values in the file to be read in during
        simulation.

        The format uses commas (`,`) to separate different signals and the order of signals
        written matches the order of ports in the interface json data.

        Each value is written with a ',' after the preceeding value in the 
        argument list. A newline is formed after all arguments
        '''
        DELIM = ','
        NEWLINE = '\n'
        if issubclass(type(bfm), model.SuperBfm):
            with open(self._path, 'a') as fd:
                ports = bfm.get_ports(mode=model.Mode.OUTPUT)
                for (_name, port) in ports:
                    fd.write(str(port.as_logic()) + DELIM)
                fd.write(NEWLINE)
                pass
            pass
        else:
            print('warning: Tried to write invalid type to output test vector file')
        pass

    pass