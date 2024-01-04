from . import config

class TraceFile:
    from .model import Mode
    from typing import List as _List

    def __init__(self, name: str, mode: Mode, dir: str=None, order: _List[str]=None):
        '''
        Creates a trace file to write stimuli/results for a potential hardware simulation.
        
        ### Parameters
        - The `name` argument sets the file's name. It is common to use a '.trace' file extension.
        - The `mode` argument determines which directional ports to capture when writing to the file.
        - The `dir` arguments specifies the directory to save the file to. If omitted, it will use the default
        working directory set by Veriti.
        - The `order` argument is the list of port names to write. It must include all ports that match the direction
        set by `mode`. This list determines the order in which to serialize the data when writing traces. If omitted,
        the port order is determined by the order found in the HDL top-level port interface.
        '''
        import os
        from .model import Mode

        self._name = name
        # try to decode str if provided as a string
        self._mode = mode if isinstance(mode, str) == False else Mode.from_str(mode)

        self._dir = dir if dir != None else config.Config()._working_dir

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
        from .coverage import CoverageNet

        port: Signal
        net: CoverageNet

        # ignore the name when collecting the ports for the given mode
        ports = [p[1] for p in get_ports(model, mode=self._mode)]

        # check if there are coverages to automatically update
        for net in CoverageNet._group:
            if net.is_observing() == True:
                # verify the observation involves only signals being written for this transaction
                subspace = net.get_watch_list()
                for signal in subspace:
                    # exit early if a signal being observed is not this transaction
                    if signal not in ports:
                        break
                # perform an observation if the signals are in this transaction
                else:
                    net.cover(net.get_observation())
            pass

        DELIM = ','
        NEWLINE = '\n'

        open_in_scope: bool = self._file == None
        fd = self._file if open_in_scope == False else open(self._path, 'a')
        
        for port in ports:
            fd.write(str(port.as_logic()) + DELIM)
        fd.write(NEWLINE)
        # close the file if it was opened in this current scope
        if open_in_scope == True:
            fd.close()
        pass

    pass