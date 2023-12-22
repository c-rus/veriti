# ------------------------------------------------------------------------------
# Project: veriti
# Author: Chase Ruskin
# Created: 2022-10-07
# Script: parity_tb
# Details:
#   Implements behavioral software model for HDL testbench parity_tb.
#
#   Writes files to be used as input data and expected output data during the
#   HDL simulation.
# ------------------------------------------------------------------------------

import veriti as vi
from typing import List
from veriti.trace import InputTrace, OutputTrace
from veriti.model import SuperBfm, Signal
import random

# --- Constants ----------------------------------------------------------------

# define the randomness seed
R_SEED = vi.seed(0)

# collect generics
SIZE: int = vi.get_generic('SIZE', type=int)
EVEN_PARITY: bool = vi.get_generic('EVEN_PARITY', type=bool)

MAX_SIMS = 256

# --- Functions ----------------------------------------------------------------

def set_parity_bit(arr: List[int], use_even=True) -> bool:
    '''
    Checks if the `arr` has an odd amount of 0's in which case the parity bit
    must be set to '1' to achieve an even parity.

    If `use_even` is set to `False`, then odd parity will be computed and will
    seek to achieve an odd amount of '1's (including parity bit).
    '''
    # count the number of 1's in the list
    return (arr.count(1) % 2) ^ (use_even == False)


# --- Classes ------------------------------------------------------------------

# define the bus functional model
class Bfm(SuperBfm):
    entity = 'parity'

    def __init__(self):
        # inputs
        self.data = Signal(width=SIZE)
        # outputs
        self.check_bit = Signal()
        pass


    def evaluate(self):
        self.check_bit.set(0)
        # cast into a `List[int]` type
        vec = [int(x) for x in self.data.as_logic()]

        if set_parity_bit(vec, use_even=EVEN_PARITY) == True:
            self.check_bit.set(1)
            
        return self
    pass

# --- Script -------------------------------------------------------------------

random.seed(R_SEED)

# create empty test vector files
i_file = InputTrace()
o_file = OutputTrace()

# generate test cases until total coverage is met or we reached max count
for _ in range(0, MAX_SIMS):
    # create a new input to enter through the algorithm
    txn = Bfm().randomize()
    i_file.append(txn)
    o_file.append(txn.evaluate())
    pass