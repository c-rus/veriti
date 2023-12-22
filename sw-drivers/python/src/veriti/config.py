# File: config.py
# Author: Chase Ruskin
# Created: 2023-12-17
# Details:
#   Stores constants used across the library.
#

VHDL_DRIVER_PROC_NAME = 'drive'
VHDL_LOADER_PROC_NAME = 'load'
VHDL_ASSERT_PROC_NAME = 'log_assertion'

TRACE_FILE_EXT = '.trace'
LOG_FILE_EXT = '.log'

LOG_TIMESTAMP_L_TOKEN = '['
LOG_TIMESTAMP_R_TOKEN = ']'

LOG_CAUSE_L_TOKEN = '\"'
LOG_CAUSE_R_TOKEN = '\"'

TAB_SIZE = 2


def TAB(n: int):
    return (' ' * TAB_SIZE) * n


class Config:
    '''
    
    Implements the Singleton pattern.
    '''
    _instance = None

    _initialized = False
    _gens = dict()
    _ports = []
    _seed = None
    _working_dir = '.'

    def __new__(cls):
        if cls._instance is None:
            print('Initializing library...')
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    

    def read_bench_if(self, data: str):
        import json
        # Update the generics
        generics = json.loads(data)['generics']
        for g in generics:
            self._gens[g['name']] = g['default']
        pass


    def read_design_if(self, data: str):
        import json
        # updates the ports
        data = json.loads(data)
        self._ports = []
        # store the ports
        for port in data['ports']:
            self._ports += [port]
        pass


    def is_initialized(self) -> bool:
        '''
        Checks if veriti has already set its configuration values using `set(...)`.
        '''
        return self._initialized
    

    def locate_port(self, key: str) -> int:
        '''
        Finds the first index that has a port with a name equal to `key`.
        '''
        for (i, port) in enumerate(self._ports):
            if port['name'] == key:
                return i
        return -1
    
    def get_port(self, i: int) -> dict:
        '''
        Acces the port element at the `i`th index.
        '''
        return self._ports[i]
    pass
