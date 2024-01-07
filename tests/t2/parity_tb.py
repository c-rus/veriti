# Project: veriti
# Script: parity_tb.py
#
# Implements a functional software model for a parity hardware module.
#
# The script's main role is to generate a series of input and output test vectors
# that will be read and processed during a hardware simulation.

import veriti as vi
from veriti.trace import TraceFile
from veriti.model import Signal
from veriti.coverage import Coverage, CoverRange, CoverPoint
import random
import hamming

# Gaussian distribution with variance 9 (20 bins)
norm_probs = [0.0005389,  0.00153382, 0.00391032, 0.00892944, 0.0182647,  0.03346428,
 0.05492042, 0.08073691, 0.10631586, 0.12540449, 0.13250064, 0.12540449,
 0.10631586, 0.08073691, 0.05492042, 0.03346428, 0.0182647,  0.00892944,
 0.00391032, 0.00153382]

class Parity:

    def __init__(self, even_parity: bool, width: int):
        self._even_parity = even_parity
        # inputs
        self.data = Signal(width, dist=norm_probs)
        # outputs
        self.check_bit = Signal()
        pass

    def evaluate(self):
        self.check_bit.set(0)
        # cast into a `List[int]` type
        vec = [int(x) for x in self.data.to_logic()]
        if hamming.set_parity_bit(vec, use_even=self._even_parity) == True:
            self.check_bit.set(1)
        return self
    pass

# realize a version of the model
model = Parity(
    even_parity=vi.get_generic('EVEN_PARITY', type=bool),
    width=vi.get_generic('SIZE', type=int)
)

cr_data = CoverRange(
    name='data full',
    span=model.data.get_range(),
    max_steps=16,
    target=model.data
)

cp_check_bit_asserted = CoverPoint(
    name='check bit asserted',
    goal=20,
    cover=lambda x: int(x) == 1,
    target=model.check_bit,
)

cp_check_bit_deasserted = CoverPoint(
    name='check bit de-asserted',
    goal=20,
    cover=lambda x: int(x) == 0,
    target=model.check_bit,
)

# create empty test vector files
inputs = TraceFile('inputs.trace', mode='in').open()
outputs = TraceFile('outputs.trace', mode='out').open()

# set and get the rng seed
random.seed(vi.rng_seed(0))

MAX_SIMS = 1_000

data_values = []

# generate test cases until total coverage is met or we reached max count
while Coverage.all_passed(MAX_SIMS) == False:
    # create a new input to enter through the algorithm
    vi.randomize(model, strategy='linear')

    data_values += [int(model.data)]

    inputs.append(model)

    model.evaluate()

    outputs.append(model)
    pass

inputs.close()
outputs.close()

# import matplotlib.pyplot as plt
# plt.hist(data_values, bins=len(norm_probs))
# plt.show()