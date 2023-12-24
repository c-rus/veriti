# Project: veriti
# Script: parity_tb.py
#
# Implements a functional software model for a parity hardware module.
#
# The script's main role is to generate a series of input and output test vectors
# that will be read and processed during a hardware simulation.

import veriti as vi
from veriti.trace import InputTrace, OutputTrace
from veriti.model import SuperBfm, Signal
import random
import hamming

class Bfm(SuperBfm):

    def __init__(self, even_parity: bool, width: int):
        self._even_parity = even_parity
        # inputs
        self.data = Signal(width)
        # outputs
        self.check_bit = Signal()
        pass

    def evaluate(self):
        self.check_bit.set(0)
        # cast into a `List[int]` type
        vec = [int(x) for x in self.data.as_logic()]
        if hamming.set_parity_bit(vec, use_even=self._even_parity) == True:
            self.check_bit.set(1)
        return self
    pass

# realize a version of the model
model = Bfm(
    even_parity=vi.get_generic('EVEN_PARITY', type=bool),
    width=vi.get_generic('SIZE', type=int)
)

# create empty test vector files
i_file = InputTrace()
o_file = OutputTrace()

# set and get the rng seed
RNG_SEED = vi.rng_seed(0)
random.seed(RNG_SEED)

MAX_SIMS = 256

# generate test cases until total coverage is met or we reached max count
for _ in range(0, MAX_SIMS):
    # create a new input to enter through the algorithm
    txn = model.randomize()
    i_file.append(txn)
    # run the algorithm for the parity
    txn = model.evaluate()
    o_file.append(txn)
    pass
