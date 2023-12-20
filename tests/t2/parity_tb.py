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
from veriti.coverage import Coverage, Covergroup, Coverpoint
from veriti.model import SuperBfm, Signal, Mode
import random

# --- Constants ----------------------------------------------------------------

# define the randomness seed
R_SEED = vi.get_seed(0)

# collect generics from command-line and HDL testbench
GENS = vi.get_generics()

WIDTH: int = vi.cast.from_vhdl_int(GENS['SIZE'])
EVEN_PARITY: bool = vi.cast.from_vhdl_bool(GENS['EVEN_PARITY'])

MAX_SIMS = 10_000

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
        self.data = Signal(Mode.INPUT, WIDTH)

        self.check_bit = Signal(Mode.OUTPUT)
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
i_file = vi.InputTrace()
o_file = vi.OutputTrace()

# generate test cases until total coverage is met or we reached max count
for _ in range(0, MAX_SIMS):
    # create a new input to enter through the algorithm
    txn = Bfm().rand()
    i_file.write(txn)
    o_file.write(txn.evaluate())
    pass