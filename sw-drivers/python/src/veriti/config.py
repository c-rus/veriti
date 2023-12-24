# Project: veriti
# File: config.py
#
# Stores constants used across the library.

LOG_TIMESTAMP_L_TOKEN = '['
LOG_TIMESTAMP_R_TOKEN = ']'

LOG_CAUSE_L_TOKEN = '\"'
LOG_CAUSE_R_TOKEN = '\"'


class Config:
    '''
    Implements the Singleton pattern for library-wide state and settings.
    '''
    _instance = None

    _LOG_FILE_EXT = '.log'
    _TRACE_FILE_EXT = '.trace'

    _initialized = False
    _gens = dict()
    _ports = []
    _seed = None
    _working_dir = '.'
    _sim_log = 'events' + _LOG_FILE_EXT

    def __new__(cls):
        if cls._instance is None:
            # print('Initializing library...')
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
        Access the port element at the `i`th index.
        '''
        return self._ports[i]
    

    def get_sim_log(self) -> str:
        '''
        Access the name of the simulation log used to write events during a
        hardware simulation.
        '''
        return self._sim_log
    pass


def set(design_if: str=None, bench_if: str=None, work_dir: str=None, seed: int=None, generics=[], sim_log: str=None):
    # grab singleton object
    state = Config()

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
    if sim_log != None:
        state._sim_log = str(sim_log)

    # update to generics mapping
    for g in generics:
        state._gens[g.key] = g.val
    
    state._initialized = True
    pass


def get_generic(key: str, type=None):
    '''
    Accesses the generic based upon the provided `key`.

    Define a type to help with converting to a Python-friendly datatype, as all
    generics are initially stored as `str`.
    '''
    from . import cast
    # verify the key exists
    if key in Config()._gens:
        value = Config()._gens[key]
    else:
        all_keys = ''
        for g in Config()._gens.keys():
            all_keys += str(g) + ', '
        if len(all_keys) > 0:
            all_keys = all_keys[:len(all_keys)-2]
        raise Exception('Unknown generic "'+key+'" (possible values: ' + all_keys + ')')
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
        raise Exception('Unsupported casting for generic "'+key+'" to type: ' + str(type))
    return value


def rng_seed(default: int=None) -> int:
    '''
    Set and get a seed integer value and initializes the random number generator.

    Parses command-line arguments for '--seed' [SEED]. If [SEED] is not given, then
    `None` will be returned. If '--seed' is not given, then the `default` will be
    returned.

    Once the seed as been set (by this function call), it cannot be overridden.
    '''
    import sys, random
    if Config()._seed == None:
        Config()._seed = default
    # set the seed value
    if Config()._seed == None:
        Config()._seed = random.randrange(sys.maxsize)
    # initialize the random state
    return Config()._seed
