# Project: veriti
# Script: timer_tb.py
#   
# This script generates the I/O test vector files to be used with the 
# timer_tb.vhd testbench. It also states a coverage report to indicate the 
# robust of the tests.

import random
import veriti as vi
from veriti.coverage import Coverage, CoverPoint
from veriti.model import Signal, Mode
from veriti.trace import TraceFile

# define the randomness seed
R_SEED = vi.rng_seed(0)

# collect generics
SUB_DELAYS  = vi.get_generic('SUB_DELAYS', type=[int])
BASE_DELAY  = vi.get_generic('BASE_DELAY', type=int)

MAX_SIMS = 100_000

# Define coverage goals

cp_map: dict = {}
# verify each tick is enabled at least 3 times
for tick in SUB_DELAYS:
    cp_map[tick] = \
        CoverPoint(
            name='tick '+str(tick)+' triggered',
            goal=3
        )
    pass
# verify the common delay is enabled
cp_base = CoverPoint(name="base tick triggered", goal=3)

# Define functional model

class Timer:
    def __init__(self):
        self.sub_ticks = Signal(width=len(SUB_DELAYS), mode=Mode.OUT, endianness='little')
        self.base_tick = Signal(mode=Mode.OUT)
        pass

    def eval(self, counts):
        self.base_tick.set(1)
            
        for i, delay in enumerate(SUB_DELAYS):
            time = counts[i]
            if time == delay-1:
                cp_map[delay].cover(True)
                self.sub_ticks.set_bit(i, '1')
                counts[i] = 0
            else:
                counts[i] += 1
        return self
    pass

random.seed(R_SEED)

# create empty test vector files
inputs = TraceFile('inputs', mode='in').open()
outputs = TraceFile('outputs', mode='out').open()

base_count = 0
counts = [0] * len(SUB_DELAYS)

# generate test cases until total coverage is met or we reached max count
while Coverage.all_passed(MAX_SIMS) == False:
    # create a new input to enter through the algorithm
    model = Timer()

    # write each transaction to the input file
    inputs.append(model)

    base_count += 1
    if base_count == BASE_DELAY:
        # compute expected values to send to simulation
        outputs.append(model.eval(counts))
        base_count = 0
        cp_base.cover(True)
    else:
        outputs.append(model)
    pass

inputs.close()
outputs.close()
