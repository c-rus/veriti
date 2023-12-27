# Project: veriti
# Module: coverage
#
# This module handles coverage implementations to track coverage nets: 
# - coverpoints
# - coverranges
# - covergroups
# - CoverCrosses

from abc import ABC as _ABC
from enum import Enum as _Enum

def _find_longest_str_len(x) -> int:
    '''
    Given a list `x`, determines the longest length str.
    '''
    longest = 0
    for item in x:
        if len(str(item)) > longest:
            longest = len(str(item))
    return longest


class Status(_Enum):
    PASSED = 0
    SKIPPED = 1
    FAILED = 2
    pass


class Coverage(_ABC):
    from abc import abstractmethod as _abstractmethod

    _group = []
    _counter = 0

    def __init__(self, name: str, bypass: bool=False):
        self._name = name
        self._bypass = bypass
        Coverage._group += [self]
        pass


    @_abstractmethod
    def to_str(self, verbose: bool) -> str:
        '''
        Convert the coverage into a string for readibility to the end-user.
        '''
        pass


    @_abstractmethod
    def cover(self, item) -> bool:
        pass


    @_abstractmethod
    def passed(self) -> bool:
        '''
        Returns `True` if the coverage met its goal.
        '''
        pass


    def log(self, verbose: bool=True) -> str:
        '''
        Convert the coverage into a string for user logging purposes. Setting `verbose` to `True`
        will provide more details in the string contents.
        '''
        label = 'CoverPoint' 
        if issubclass(type(self), CoverGroup):
            label = 'CoverGroup'
        elif issubclass(type(self), CoverRange):
            label = 'CoverRange'
        elif issubclass(type(self), CoverCross):
            label = 'CoverCross'
        if verbose == False:
            return label + ": " + self._name + ': ' + self.to_str(verbose) + ' ...'+str(self.status().name)
        else:
            return label + ": " + self._name + ':' + ' ...'+str(self.status().name) + '\n    ' + self.to_str(verbose)


    def skipped(self) -> bool:
        '''
        Checks if this coverage is allowed to be bypassed during simulation due
        to an external factor making it impossible to pass.
        '''
        return self._bypass 
    

    def status(self) -> Status:
        '''
        Determine the status of the Coverage node.
        '''
        if self.skipped() == True:
            return Status.SKIPPED
        elif self.passed() == True:
            return Status.PASSED
        else:
            return Status.FAILED
        

    @staticmethod
    def all_passed(timeout: int=-1) -> bool:
        '''
        Checks if each coverage specification has met its goal.

        If a coverage specification is bypassed, it counts as meeting its
        goal. If the timeout is set to -1, it will be disabled and only return
        `True` once all cases are covered.
        '''
        # force the simulation to pass if enough checks are evaluated
        if timeout > 0 and Coverage._counter >= timeout:
            return True        
        # check every cover-node
        cov: Coverage
        for cov in Coverage._group:
            if cov.skipped() == False and cov.passed() == False:
                # increment the counter
                Coverage._counter += 1
                return False
        return True


    @staticmethod
    def report(verbose: bool=True) -> str:
        '''
        Compiles a report of the coverage statistics and details. Setting `verbose`
        to `False` will only provide minimal details to serve as a quick summary.
        '''
        contents = ''
        if verbose == True:
                contents += "Test Count: " + str(Coverage.count()) + '\n'
                contents += "Coverage: "   + str(Coverage.percent()) + ' %\n'
        cov: Coverage
        for cov in Coverage._group:
            contents += cov.log(verbose) + '\n'
        return contents
    

    @staticmethod
    def save_report(file=None):
        '''
        Writes the coverage report with verbosity to the file `file`.
        '''
        import os
        from . import config
        if file == None:
            file = os.path.join(config.Config()._working_dir, 'coverage.txt')
        with open(file, 'w') as cf:
            cf.write(Coverage.report(True))
    

    @staticmethod
    def count() -> int:
        '''
        Returns the number of times the Coverage class has called the 'all_passed'
        function. If 'all_passed' is called once every transaction, then it gives
        a sense of how many test cases were required in order to achieve full
        coverage.
        '''
        return Coverage._counter
    

    @staticmethod
    def percent() -> float:
        '''
        Return the percent of all coverages that met their goal. Each covergroup's bin
        is tallied individually instead of tallying the covergroup as a whole.

        Coverages that have a status of `SKIPPED` are not included in the tally.

        Returns `None` if there are no coverages to tally. The percent value is
        from 0.00 to 100.00 percent, with rounding to 2 decimal places.
        '''
        total_covers = 0
        covers_passed = 0
        cov: Coverage
        for cov in Coverage._group:
            if cov.status() == Status.SKIPPED:
                continue
            total_covers += 1
            if cov.status() == Status.PASSED:
                covers_passed += 1
            pass
        return round((covers_passed/total_covers) * 100.0, 2) if total_covers > 0 else None
    pass


class CoverGroup(Coverage):
    from typing import List as _List

    group = []

    def __init__(self, name: str, bins: _List, goal: int=1, bypass: bool=False, max_bins=64, mapping=None):
        '''
        Initialize by expliciting defining the bins.
        '''
        # stores the items per index for each bin group
        self._macro_bins = []
        # stores the count for each bin
        self._macro_bins_count = []
        # store a hash to the index in the set of bins list
        self._bins_lookup = dict()

        # defining a bin range is more flexible for defining a large space

        # store the function to map items into the coverage space
        self._map = mapping

        # determine the number of maximum bins
        self._max_bins = max_bins

        # store the actual values when mapped items cover toward the goal
        self._mapped_items = dict()

        # will need to provide a division operation step before inserting into
        if len(bins) > self._max_bins:
            self._items_per_bin = int(len(bins) / self._max_bins)
        else:
            self._items_per_bin = 1

        # initialize the bins
        for i, item in enumerate(set(bins)):
            # items are already in their 'true' from from given input
            self._bins_lookup[item] = i
            # group the items together based on a common index that divides them into groups
            i_macro = int(i / self._items_per_bin)
            if len(self._macro_bins) <= i_macro:
                self._macro_bins.append([])
                self._macro_bins_count.append(0)
                pass
            self._macro_bins[i_macro] += [item]
            pass

        # set the goal required for each bin
        self._goal = goal
        # initialize the total count of all covers
        self._total_count = 0
        super().__init__(name, bypass)
    pass


    def _is_possible_value(self, item) -> bool:
        '''
        Checks if the `item` is in the current possible list of all stored bins.

        Uses the raw unmapped value as the `item` and maps it.
        '''
        return self._bins_lookup.get(item if self._map == None else self._map(item)) != None
    

    def _map_value(self, item):
        '''
        Converts the raw value into the index in the given range of possible entries.
        '''
        mapped_item = item if self._map == None else self._map(item)
        return int(self._bins_lookup[mapped_item])
    

    def _get_macro_bin_index(self, item) -> int:
        '''
        Returns the macro index for the `item` according to the bin division.

        Returns -1 if the item does not exist. Takes the mapped input
        '''
        if self._is_possible_value(item) == False:
            return -1
        return int(self._bins_lookup[item] / self._items_per_bin)
    

    def get_range(self) -> range:
        return range(0, len(self._bins_lookup.keys()), self._items_per_bin)
    

    def get_step_count(self) -> int:
        return len(self._macro_bins)
    

    def cover(self, item):
        '''
        Return's true if it got the entire group closer to meeting coverage.

        This means that the item covered is under the goal.
        '''
        # use special mapping function if defined
        mapped_item = item if self._map == None else self._map(item)
        # got the item, but check its relative items under the same goal
        i_macro = self._get_macro_bin_index(mapped_item)
        # print(mapped_item, i_macro, item)
        # make the item exists as a possible entry and its macro goal is not met
        is_progress = self._is_possible_value(item) == True and self._macro_bins_count[i_macro] < self._goal
        # check if its in the covered bin
        if self._is_possible_value(item) == True:
            # update the map with the value
            self._macro_bins_count[i_macro] += 1
            # update the total count
            self._total_count += 1
            # record the actual value that initiated this coverage
            if self._map != None:
                if i_macro not in self._mapped_items.keys():
                    self._mapped_items[i_macro] = dict()
                if item not in self._mapped_items[i_macro].keys():
                   self._mapped_items[i_macro][item] = 0 
                # increment the count of this item being detected
                self._mapped_items[i_macro][item] += 1
            pass
        return is_progress
    

    def next(self, rand=False):
        '''
        Returns the next item currently not meeting the coverage goal.

        Enabling `rand` will allow for a random item to be picked, rather than
        sequentially.

        Returns `None` if no item is left (all goals are reached and coverage is
        passing).
        '''
        import random as _random

        # can only map 1-way (as of now)
        if self._map != None:
            raise Exception("Cannot map back to original values")
        available = []
        # filter out the elements who have not yet met the goal
        for i, count in enumerate(self._macro_bins_count):
            if count < self._goal:
                available += [i]
            pass
        if len(available) == 0:
            return None
        if rand == True:
            # pick a random macro bin
            i_macro = _random.choice(available)
            # select a random item from the bin
            return _random.choice(self._macro_bins[i_macro])

        # provide 1st available if random is disabled
        i_macro = available[0]
        return self._macro_bins[i_macro][0]

    
    def passed(self) -> bool:
        '''
        Checks if each bin within the `CoverGroup` has met or exceeded its goal. 
        If any of the bins has not, then whole function fails and returns `False`.
        '''
        for val in self._macro_bins_count:
            # fail on first failure
            if val < self._goal:
                return False
        return True
    

    def _macro_to_str(self, i) -> str:
        '''
        Write a macro_bin as a string.
        '''
        LIMITER = 7
        items = self._macro_bins[i]
        result = '['
        for i in range(0, 8):
            if i >= len(items):
                break
            result += str(items[i])
            if i < len(items)-1:
                result += ', '
            if i >= LIMITER:
                result += '...'
                break
            pass
        result += ']'
        return result


    def to_str(self, verbose: bool=False) -> str:
        result = ''
        # print each individual bin and its goal status
        if verbose == True:
            # determine the string formatting by identifying longest string
            longest_len = _find_longest_str_len([self._macro_to_str(i) for i, _ in enumerate(self._macro_bins)])
            is_first = True
            # print the coverage analysis
            for i, group in enumerate(self._macro_bins):
                if is_first == False:
                    result += '\n    '
                phrase = str(self._macro_to_str(i))
                count = self._macro_bins_count[i]
                result += str(phrase) + ': ' + (' ' * (longest_len - len(str(phrase)))) + str(count) + '/' + str(self._goal)
                # enumerate on all mapped values that were detected for this bin
                if self._map != None and i in self._mapped_items.keys():
                    # determine the string formatting by identifying longest string
                    sub_longest_len = _find_longest_str_len(self._mapped_items[i].keys())
                    seq = [(key, val) for key, val in self._mapped_items[i].items()]
                    seq.sort()
                    LIMITER = 20
                    for i, (key, val) in enumerate(seq):
                        result += '\n        '
                        if i > LIMITER:
                            result += '...'
                            break
                        result += str(key) + ': ' + (' ' * (sub_longest_len - len(str(key)))) + str(val)

                        pass
                is_first = False
        # print the number of bins that reached their goal
        else:
            bins_reached = 0
            for count in self._macro_bins_count:
                if count >= self._goal:
                    bins_reached += 1
                pass
            result += str(bins_reached) + '/' + str(len(self._macro_bins_count))
        return result
    pass


class CoverRange(Coverage):
    '''
    CoverRanges are designed to track a span of integer numbers, which can divided up among steps.
    This structure is similar to a CoverGroup, however, the bins defined in a CoverRange are implicitly defined
    along the set of integers.
    '''

    def __init__(self, name: str, span: range, goal: int=1, bypass: bool=False, max_steps: int=64, mapping=None):
        '''
        Initialize a CoverRange. 
        
        The `mapping` argument is a callable function that expects to return an `int`, 
        which effectively takes some outside input(s) and maps it to a number within 
        the specified range.
        '''
        import math

        domain = span
        self._goal = goal
        # domain = range
        # determine the step size
        self._step_size = domain.step
        self._max_steps = max_steps
        num_steps_needed = len(domain)
        # limit by computing a new step size
        self._step_size = domain.step
        self._num_of_steps = num_steps_needed
        if self._max_steps != None and num_steps_needed > self._max_steps:
            # update instance attributes
            self._step_size = int(math.ceil(abs(domain.start - domain.stop) / self._max_steps))
            self._num_of_steps = self._max_steps
            pass

        self._table = [[]] * self._num_of_steps
        self._table_counts = [0] * self._num_of_steps

        self._start = domain.start
        self._stop = domain.stop

        # initialize the total count of all covers
        self._total_count = 0

        # store a potential custom mapping function
        self._map = mapping

        # store the actual values when mapped items cover toward the goal
        self._mapped_items = dict()

        super().__init__(name, bypass)
        pass


    def get_range(self) -> range:
        '''
        Returns the range struct for the CoverRange.
        '''
        return range(self._start, self._stop, self._step_size)
    

    def get_step_count(self) -> int:
        '''
        Returns the number of steps necessary to span the entire range.
        '''
        return self._num_of_steps
    

    def passed(self) -> bool:
        '''
        Checks if each bin within the `CoverGroup` has met or exceeded its goal. 
        If any of the bins has not, then whole function fails and returns `False`.
        '''
        for entry in self._table_counts:
            # exit early on first failure for not meeting coverage goal
            if entry < self._goal:
                return False
        return True
    

    def _is_possible_value(self, item) -> bool:
        '''
        Checks if the mapping was legal and within the bounds.
        '''
        mapped_item = self._map_value(item)
        return mapped_item >= self._start and mapped_item < self._stop
    

    def _map_value(self, item) -> int:
        return int(item) if self._map == None else int(self._map(item))


    def cover(self, item) -> bool:
        '''
        Return's true if it got the entire group closer to meeting coverage.

        This means that the item covered is under the goal.
        '''
        # convert item to int
        mapped_item = self._map_value(item)
        # transform into coverage domain
        index = int(mapped_item / self._step_size)
        # check if it improves progessing by adding to a mapping that has not met the goal yet
        is_progress = self._is_possible_value(item) == True and self._table_counts[index] < self._goal
        # update the coverage for this value
        if self._is_possible_value(item) == True:
            self._table[index] += [mapped_item]
            self._table_counts[index] += 1
            self._total_count += 1
            # track original items that count toward their space of the domain
            if index not in self._mapped_items.keys():
                self._mapped_items[index] = dict()
            if item not in self._mapped_items[index].keys():
                self._mapped_items[index][mapped_item] = 0 
            # increment the count of this item being detected
            self._mapped_items[index][mapped_item] += 1
            pass
        return is_progress
    

    def next(self, rand: bool=False):
        '''
        Returns the next item currently not meeting the coverage goal.

        Enabling `rand` will allow for a random item to be picked, rather than
        sequentially.

        Returns `None` if no item is left (all goals are reached and coverage is
        passing).
        '''
        import random as _random

        # can only map 1-way (as of now)
        if self._map != None:
            raise Exception("Cannot map back to original values")
        available = []
        # filter out the elements who have not yet met the goal
        for i, count in enumerate(self._table_counts):
            if count < self._goal:
                available += [i]
            pass
        if len(available) == 0:
            return None
        if rand == True:
            j = _random.choice(available)
            # transform back to the selection of the expanded domain space
            expanded_space = [(j * self._step_size) + x for x in range(0, self._step_size)]
            # select a random item from the bin
            return _random.choice(expanded_space)
        # provide 1st available if random is disabled
        expanded_space = [(available[0] * self._step_size) + x for x in range(0, self._step_size)]
        return expanded_space[0]
    

    def to_str(self, verbose: bool) -> str:
        result = ''
        # print each individual bin and its goal status
        if verbose == True:
            # determine the string formatting by identifying longest string
            if self._step_size > 1:
                longest_len = len(str((len(self._table)-2) * self._step_size) + '..=' + str((len(self._table)-1) * self._step_size))
            else:
                longest_len = len(str(self._stop-1))
            is_first = True
            # print the coverage analysis
            for i, _group in enumerate(self._table):
                if is_first == False:
                    result += '\n    '
                if self._step_size > 1:
                    step = str(i * self._step_size) + '..=' + str(((i+1) * self._step_size)-1)
                else:
                    step = i
                count = self._table_counts[i]
                result += str(step) + ': ' + (' ' * (longest_len - len(str(step)))) + str(count) + '/' + str(self._goal)
                # determine the string formatting by identifying longest string
                if self._step_size > 1 and i in self._mapped_items.keys():
                    sub_longest_len = _find_longest_str_len(self._mapped_items[i].keys())
                    seq = [(key, val) for key, val in self._mapped_items[i].items()]
                    seq.sort()
                    LIMITER = 20
                    for i, (key, val) in enumerate(seq):
                        result += '\n        '
                        if i > LIMITER:
                            result += '...'
                            break
                        result += str(key) + ': ' + (' ' * (sub_longest_len - len(str(key)))) + str(val)
                        pass
                is_first = False
            pass
        # print the number of bins that reached their goal
        else:
            goals_reached = 0
            for count in self._table_counts:
                if count >= self._goal:
                    goals_reached += 1
                pass
            result += str(goals_reached) + '/' + str(len(self._table_counts))
        return result


class CoverPoint(Coverage):
    '''
    CoverPoints are designed to track when a single particular event occurs.
    '''

    def __init__(self, name: str, goal: int, bypass=False, mapping=None):
        '''
        Initialize a CoverPoint. 
        
        The `mapping` argument is a callable function that
        expects to return a `bool`, which effectively takes some outside input(s) and
        maps it to the user-defined coverage point.
        '''
        self._count = 0
        self._goal = goal
        # define a custom function that should return a boolean to define the targeted point
        self._mapping = mapping
        super().__init__(name, bypass)
        pass


    def _is_possible_value(self, item) -> bool:
        '''
        Checks if the mapping was legal and within the bounds.
        '''
        mapped_item = int(self._map_value(item))
        return mapped_item >= 0 and mapped_item < 2
    

    def _map_value(self, item) -> int:
        return int(item) if self._mapping == None else int(self._mapping(item))


    def cover(self, item):
        '''
        Returns `True` if the `cond` was satisfied and updates the internal count
        as the coverpoint tries to met or exceed its goal.
        '''
        cond = self._map_value(item)
        if cond == True:
            self._count += 1
        return cond


    def passed(self):
        return self._count >= self._goal
    

    def to_str(self, verbose: bool):
        return str(self._count) + '/' + str(self._goal)
    

    def get_range(self) -> range:
        return range(0, 2)
    

    def get_step_count(self) -> int:
        return 2
    
    pass


class CoverCross(Coverage):
    '''
    CoverCrosses are designed to track cross products between two or more coverage nets.

    Internally, a CoverCross stores a CoverRange for the 1-dimensional flatten version of
    the N-dimensional cross product across the different coverage nets.
    '''
    from typing import List as _List

    def __init__(self, name: str, nets: _List[CoverRange], goal: int=1, bypass=False):
        self._nets = nets[::-1]
        self._crosses = len(self._nets)
        
        combinations = 1
        for n in nets:
            combinations *= n.get_step_count()
            pass

        self._inner = CoverRange(
            name,
            span=range(combinations),
            goal=goal,
            bypass=bypass,
            max_steps=None,
            mapping=None,
        )
        # remove that entry and use this instance
        self._group.pop()
        # overwrite the entry with this instance in the class-wide data structure
        super().__init__(name, bypass)
        pass


    def _flatten(self, pair):
        '''
        Flattens a N-dimensional item into a 1-dimensional index.

        Reference: 
        - https://stackoverflow.com/questions/7367770/how-to-flatten-or-index-3d-array-in-1d-array
        '''
        if len(pair) != self._crosses:
            raise Exception("Expects "+str(self._crosses)+" values in pair")
        index = 0
        # dimensions go: x, y, z... so reverse the tuple/list
        for i, p in enumerate(pair[::-1]):
            # exit if an element was not a possible value
            if self._nets[i]._is_possible_value(p) == False:
                return None
            mapped_element = self._nets[i]._map_value(p)
            # collect all above step counts
            acc_step_counts = 1
            for j in range(i+1, self._crosses):
                acc_step_counts *= self._nets[j].get_step_count()
            index += acc_step_counts * int(mapped_element / self._nets[i].get_range().step)
        return index


    def cover(self, pair):
        index = self._flatten(pair)
        if index == None:
            return False
        return self._inner.cover(index)


    def passed(self):
        return self._inner.passed()
    

    def to_str(self, verbose: bool):
        return self._inner.to_str(verbose)

    pass


import unittest as _ut

class __Test(_ut.TestCase):

    def test_cross_flatten_2d(self):
        cross = CoverCross('test', [CoverRange('a', span=range(0, 4)), CoverRange('b', span=range(0, 4))])
        self.assertEqual(0, cross._flatten((0, 0)))
        self.assertEqual(3, cross._flatten((3, 0)))
        self.assertEqual(4, cross._flatten((0, 1)))
        self.assertEqual(5, cross._flatten((1, 1)))
        self.assertEqual(15, cross._flatten((3, 3)))
        pass

    def test_cross_flatten_3d(self):
        cross = CoverCross('test', [CoverRange('a', span=range(0, 2)), CoverRange('b', span=range(0, 3)), CoverRange('c', span=range(0, 4))])
        self.assertEqual(0, cross._flatten((0, 0, 0)))
        self.assertEqual(1, cross._flatten((1, 0, 0)))
        self.assertEqual(2*1, cross._flatten((0, 1, 0)))
        self.assertEqual(2*2, cross._flatten((0, 2, 0)))
        self.assertEqual(6, cross._flatten((0, 0, 1)))
        self.assertEqual(1 + 2 + 6, cross._flatten((1, 1, 1)))
        self.assertEqual(1 + 2*2 + 3*6, cross._flatten((1, 2, 3)))
        pass

    pass