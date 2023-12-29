from . import config

class TraceFile:
    from .model import Mode

    def __init__(self, name: str, mode: Mode, dir: str=None):
        '''
        Creates a trace file to write stimuli/results for a potential hardware simulation.
        
        The .trace file extension will be automatically appended to the provided `name`.
        '''
        import os
        from .model import Mode

        self._name = name
        # try to decode str if provided as a string
        if isinstance(mode, str) == True:
            self._mode = Mode.from_str(mode)
        else:
            self._mode = mode

        if dir != None:
            self._dir = dir
        else:
            self._dir = config.Config()._working_dir

        self._path = os.path.join(self._dir, self._name)
        
        self._exists = os.path.exists(self._path)
        # clear the existing file
        if self._exists == True:
            open(self._path, 'w').close()
        # create the file if it does not exist
        elif self._exists == False:
            os.makedirs(self._dir, exist_ok=True)
            open(self._path, 'w').close()
            self._exists = True

        self._file = None
        pass


    def __del__(self):
        if self._file != None:
            self._file.close()
        pass


    def open(self):
        '''
        Explicit call to obtain ownership of the file. It is the programmer's
        responsibility to close the file when done.

        Calling this function and leaving the file open while appending traces
        to the test vector files can improve performance when many writes are
        required.
        '''
        # open the file in append mode
        if self._file == None:
            self._file = open(self._path, 'a')
        return self
    

    def close(self):
        '''
        Explicit call to release ownership of the file. This operation is
        idempotent.
        '''
        if self._file != None:
            self._file.close()
            self._file = None
        return self


    def append(self, model):
        '''
        Writes the directional ports of the bus funcitonal model to the test vector file.

        Format each signal as logic values in the file to be read in during
        simulation.

        The format uses commas (`,`) to separate different signals and the order of signals
        written matches the order of ports in the interface json data.

        Each value is written with a ',' after the preceeding value in the 
        argument list. A newline is formed after all arguments
        '''
        from .model import Signal, get_ports
        DELIM = ','
        NEWLINE = '\n'

        open_in_scope: bool = self._file == None
        fd = self._file if open_in_scope == False else open(self._path, 'a')
        
        ports = get_ports(model, mode=self._mode)
        port: Signal
        for (_name, port) in ports:
            fd.write(str(port.as_logic()) + DELIM)
        fd.write(NEWLINE)
        # close the file if it was opened in this current scope
        if open_in_scope == True:
            fd.close()
        pass

    pass