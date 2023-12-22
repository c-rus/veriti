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
import hamming
import sys
print(sys.version_info)
print(sys.path)
# --- Constants ----------------------------------------------------------------

# define the randomness seed
R_SEED = vi.seed(0)

# collect generics
SIZE: int = vi.get_generic('SIZE', type=int)
EVEN_PARITY: bool = vi.get_generic('EVEN_PARITY', type=bool)

MAX_SIMS = 256

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

        if hamming.set_parity_bit(vec, use_even=EVEN_PARITY) == True:
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