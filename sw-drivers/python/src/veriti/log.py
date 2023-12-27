from enum import Enum as _Enum
from . import config


class Level(_Enum):
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5

    @staticmethod
    def from_str(s: str):
        # format
        s = s.strip().upper()
        # decide
        if s == 'TRACE':
            return Level.TRACE
        elif s == 'DEBUG':
            return Level.DEBUG
        elif s == 'INFO':
            return Level.INFO
        elif s == 'WARN':
            return Level.WARN
        elif s == 'ERROR':
            return Level.ERROR
        elif s == 'FATAL':
            return Level.FATAL
        else:
            print('failed to parse level')
            return -1
        
    
    def __str__(self):
        return self.name
        

    def is_fail(self) -> bool:
        '''
        Returns `True` if the outcome was ERROR or FATAL level.
        '''
        return self == Level.ERROR or self == Level.FATAL


    def is_pass(self) -> bool:
        '''
        Returns `True` if the outcome was INFO level.
        '''
        return self == Level.INFO
    
    pass


class Timeunit(_Enum):
    FS = 1
    PS = 2
    NS = 3
    US = 4
    MS = 5
    SEC = 6
    MIN = 7
    HR = 8

    @staticmethod
    def from_str(s: str):
        # format
        s = s.strip().upper()
        # decide
        if s == 'FS':
            return Timeunit.FS
        elif s == 'PS':
           return Timeunit.PS 
        elif s == 'NS':
           return Timeunit.NS 
        elif s == 'US':
           return Timeunit.US 
        elif s == 'MS':
           return Timeunit.MS 
        elif s == 'SEC':
           return Timeunit.SEC 
        elif s == 'MIN':
           return Timeunit.MIN 
        elif s == 'HR':
           return Timeunit.HR 
        else:
            print('failed to parse timeunit')
            return -1
        

    def __str__(self):
        return self.name.lower()
        

    def convert(self, unit):
        '''
        Returns the value necessary to convert to the new time unit `unit`.
        '''
        unit: Timeunit
        # store every neighboring computation to get to next/prev unit
        jumps = [1, 1_000, 1_000, 1_000, 1_000, 1_000, 60, 60]

        # slice which numbers are required to get to target timeunit 
        start: int = self.value
        delta: int = unit.value - self.value
       
        subs = jumps[start+delta:start] if delta < 0 else jumps[start:start+delta]
        
        # multiply all jumps together
        conversion = 1
        for s in subs:
            conversion *= s if delta < 0 else (1/s)
        return conversion
    
    pass


class Timestamp:
    
    def __init__(self, ticks: int, unit: Timeunit):
        self._ticks = ticks
        self._unit = unit
        pass


    @staticmethod
    def from_str(s: str):
        # format
        s = s.strip()
        # split on white space
        parts = s.split()
        if len(parts) != 2:
            print('failed to parse timestamp')
            return -1
        ts = Timestamp(ticks=int(parts[0]), unit=Timeunit.from_str(parts[1]))
        return ts
    

    def __str__(self):
        return str(self._ticks) + ' ' + str(self._unit)


    def __eq__(self, rhs):
        return self._ticks == rhs._ticks and \
            self._unit == rhs._unit

    pass


class Record:

    def __init__(self, timestamp: Timestamp, level: Level, topic: str, cause: str):
        self._timestamp: Timestamp = timestamp
        self._level: Level = level
        self._topic: str = topic
        self._cause: str = cause

        self._max_ts_str_len = -1
        pass


    @staticmethod
    def from_str(s: str):
        # slice and remove delimiters from timestamp break off into components
        timestamp: str = s[s.find(config.LOG_TIMESTAMP_L_TOKEN)+1:s.find(config.LOG_TIMESTAMP_R_TOKEN)]
        # slice and remove enclosing quotes around cause
        cause: str = s[s.find(config.LOG_CAUSE_L_TOKEN)+1:s.rfind(config.LOG_CAUSE_R_TOKEN)]
        # deal with remaining part of record
        parts = s[s.find(config.LOG_TIMESTAMP_R_TOKEN)+1:s.find(config.LOG_CAUSE_L_TOKEN)].split()

        level = parts[0]
        topic = parts[1]
        return Record(Timestamp.from_str(timestamp), Level.from_str(level), topic, cause)


    def __str__(self):
        return \
            config.LOG_TIMESTAMP_L_TOKEN + \
            str.ljust(str(self._timestamp), 15) + \
            config.LOG_TIMESTAMP_R_TOKEN + \
            ' ' + \
            str.ljust(str(self._level), 8) + \
            ' ' + \
            str.ljust(str(self._topic), 12) + \
            ' ' + \
            '"' + \
            str(self._cause) + \
            '"'


    def __eq__(self, rhs):
        return self._timestamp == rhs._timestamp and \
            self._level == rhs._level and \
            self._topic == rhs._topic and \
            self._cause == rhs._cause

    pass


class Log:

    def __init__(self, outcomes, max_ts_str_len=-1):
        '''
        Create a handler to a log file located at `path`.
        '''
        self._outcomes = outcomes

        # collect stats
        self._tests = 0
        self._passes = 0
        self._fails = 0
        for event in self._outcomes:
            event._max_ts_str_len = max_ts_str_len
            if event._level.is_fail() == True or event._level.is_pass() == True:
                self._tests += 1
            if event._level.is_fail() == True:
                self._fails += 1
            if event._level.is_pass() == True:
                self._passes += 1
        pass


    @staticmethod
    def from_str(s: str):
        outcomes = []
        # split on newlines
        max_ts_str_len = 0
        for line in s.splitlines():
            outcomes += [Record.from_str(line)]
            if len(str(outcomes[-1]._timestamp)) > max_ts_str_len:
                max_ts_str_len = len(str(outcomes[-1]._timestamp))
            pass
        return Log(outcomes, max_ts_str_len=max_ts_str_len)


    @staticmethod
    def load(path: str):
        '''
        Parses the provided file to store the collection of records.
        '''
        log = None
        with open(path, 'r') as f:
            log = Log.from_str(f.read())
        return log


    def is_success(self) -> bool:
        '''
        Determines if the log is successful (has 0 failures).
        '''
        return self._fails == 0
    

    def get_test_count(self) -> int:
        '''
        Reports number of test-able outcomes.
        '''
        return self._tests
    

    def get_pass_count(self) -> int:
        '''
        Reports the number of tests passed.
        '''
        return self._passes
    

    def get_fail_count(self) -> int:
        '''
        Reports the number of tests failed.
        '''
        return self._fails
    

    def get_outcomes(self):
        return self._outcomes
    
    
    def get_score(self):
        return round((self._passes/self._tests) * 100.0, 2) if self._tests > 0 else None
    
    pass


def read(logfile: str, level: int) -> str:
    # process the log file
    lg = Log.load(logfile)

    result: str = ''
    for event in lg.get_outcomes():
        event: Record
        # print all bad outcomes
        if event._level.value >= level:
            result += str(event) + '\n'
        pass
    
    return result


def check(threshold: float=1.0) -> bool:
    '''
    Determines if verification passed based on meeting or exceeding the threshold value.

    ### Parameters
    - `threshold` expects a floating point value [0, 1.0]
    '''
    lg = Log.load(get_event_log_path())
    if lg.get_test_count() <= 0:
        return True
    return float(lg.get_pass_count()/lg.get_test_count()) >= threshold


def get_event_log_path() -> str:
    '''
    Returns the absolute path to the log file.
    '''
    import os
    from . import config
    path = os.path.join(config.Config()._working_dir, config.Config().get_sim_log())
    return str(os.path.abspath(path))


def report_score() -> str:
    '''
    Formats the score as a `str`.
    '''
    lg = Log.load(get_event_log_path())
    return (str(lg.get_score()) + ' % ' if lg.get_score() != None else 'N/A ') + '(' + str(lg.get_pass_count()) + '/' + str(lg.get_test_count()) + ')'


def get_name() -> str:
    '''
    Access the name of the simulation log used to write events during a
    hardware simulation.
    '''
    return config.Config().get_sim_log()


import unittest as _ut


class __Test(_ut.TestCase):

    def test_timeunit_up_conversion(self):
        # increasing unit scale
        self.assertEqual(1/1_000, Timeunit.PS.convert(Timeunit.NS))
        self.assertEqual(1/1_000_000, Timeunit.PS.convert(Timeunit.US))
        self.assertEqual(1/1_000_000, Timeunit.US.convert(Timeunit.SEC))
        self.assertEqual(1.6666666666666667e-08, Timeunit.US.convert(Timeunit.MIN))
        self.assertEqual(2.7777777777777777e-10, Timeunit.US.convert(Timeunit.HR))
        self.assertEqual(2.7777777777777782e-19, Timeunit.FS.convert(Timeunit.HR))
        pass

    def test_timeunit_down_conversion(self):
        # decreasing unit scale
        self.assertEqual(60, Timeunit.HR.convert(Timeunit.MIN))
        self.assertEqual(3_600, Timeunit.HR.convert(Timeunit.SEC))
        self.assertEqual(3_600_000, Timeunit.HR.convert(Timeunit.MS))
        self.assertEqual(3_600_000_000, Timeunit.HR.convert(Timeunit.US))
        self.assertEqual(3_600_000_000_000, Timeunit.HR.convert(Timeunit.NS))
        self.assertEqual(3_600_000_000_000_000, Timeunit.HR.convert(Timeunit.PS))
        self.assertEqual(3_600_000_000_000_000_000, Timeunit.HR.convert(Timeunit.FS))

        self.assertEqual(1_000, Timeunit.NS.convert(Timeunit.PS))
        pass
    
    def test_timeunit_const_conversion(self):
        # unit scale constant
        self.assertEqual(1, Timeunit.HR.convert(Timeunit.HR))
        pass


    def test_parse_record(self):
        data = "[1040 ns        ] INFO     TIMEOUT      \"done being asserted - required 5 cycles\""
        rec = Record.from_str(data)
        self.assertEqual(rec, Record(Timestamp(1040, Timeunit.NS), Level.INFO, "TIMEOUT", "done being asserted - required 5 cycles"))
        pass


    def test_log_reading(self):
        path = './raw-data/outcomes.log'
        line_count = 0 
        with open(path, 'r') as f:
            line_count = len(f.readlines())

        log = Log.load(path)
        self.assertEqual(len(log._outcomes), line_count)

        self.assertEqual(log.get_pass_count(), 204)
        self.assertEqual(log.get_fail_count(), 0)
        self.assertEqual(log.get_test_count(), 204)

        self.assertEqual(log.is_success(), True)
        pass

    pass