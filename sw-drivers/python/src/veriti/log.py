from enum import Enum as _Enum
from .config import LOG_CAUSE_L_TOKEN, LOG_CAUSE_R_TOKEN, LOG_TIMESTAMP_L_TOKEN, LOG_TIMESTAMP_R_TOKEN


class Level(_Enum):
    TRACE = 0,
    DEBUG = 1,
    INFO = 2,
    WARN = 3,
    ERROR = 4,
    FATAL = 5,

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
        pass


    @staticmethod
    def from_str(s: str):
        # slice and remove delimiters from timestamp break off into components
        timestamp: str = s[s.find(LOG_TIMESTAMP_L_TOKEN)+1:s.find(LOG_TIMESTAMP_R_TOKEN)]
        # slice and remove enclosing quotes around cause
        cause: str = s[s.find(LOG_CAUSE_L_TOKEN)+1:s.rfind(LOG_CAUSE_R_TOKEN)]
        # deal with remaining part of record
        parts = s[s.find(LOG_TIMESTAMP_R_TOKEN)+1:s.find(LOG_CAUSE_L_TOKEN)].split()

        level = parts[0]
        topic = parts[1]
        return Record(Timestamp.from_str(timestamp), Level.from_str(level), topic, cause)


    def __eq__(self, rhs):
        return self._timestamp == rhs._timestamp and \
            self._level == rhs._level and \
            self._topic == rhs._topic and \
            self._cause == rhs._cause

    pass


class Log:

    def __init__(self, outcomes):
        '''
        Create a handler to a log file located at `path`.
        '''
        self._outcomes = outcomes
        pass


    @staticmethod
    def from_str(s: str):
        outcomes = []
        # split on newlines
        for line in s.splitlines():
            outcomes += [Record.from_str(line)]
            pass
        return Log(outcomes)


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
        out: Record
        for out in self._outcomes:
            if out._level.is_fail() == True:
                return False
        return True
    

    def get_test_count(self) -> int:
        '''
        Reports number of test-able outcomes.
        '''
        tests: int = 0
        for out in self._outcomes:
            out: Record
            if out._level.is_fail() or out._level.is_pass():
                tests += 1
        return tests
    

    def get_pass_count(self) -> int:
        '''
        Reports the number of tests passed.
        '''
        passes: int = 0
        for out in self._outcomes:
            out: Record
            if out._level.is_pass() == True:
                passes += 1
        return passes
    

    def get_fail_count(self) -> int:
        '''
        Reports the number of tests failed.
        '''
        fails: int = 0
        for out in self._outcomes:
            out: Record
            if out._level.is_fail() == True:
                fails += 1
        return fails
    
    pass


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