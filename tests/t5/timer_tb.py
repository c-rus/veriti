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

# collect generics
SUB_DELAYS  = vi.get_generic('SUB_DELAYS', type=[int])
BASE_DELAY  = vi.get_generic('BASE_DELAY', type=int)

MAX_SIMS = 100_000

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
                self.sub_ticks.set_bit(i, '1')
                counts[i] = 0
            else:
                self.sub_ticks.set_bit(i, '0')
                counts[i] += 1
        return self
    pass


model = Timer()

# Define coverage goals

# verify each tick is enabled at least 3 times
for i, tick in enumerate(SUB_DELAYS):
    CoverPoint(
        name='tick '+str(tick)+' triggered',
        goal=3,
        # capture `i` by value not by reference
        mapping=lambda x, i=i: int(x[i]) == 1,
        read_interface=model.sub_ticks
    )

# verify the common delay is enabled
cp_base = CoverPoint(
    name="base tick triggered", 
    goal=3,
    read_interface=model.base_tick
)

# set the randomness seed
random.seed(vi.rng_seed(0))

# create empty test vector files
inputs = TraceFile('inputs.trace', mode='in').open()
outputs = TraceFile('outputs.trace', mode='out').open()

base_count = 0
counts = [0] * len(SUB_DELAYS)

# generate test cases until total coverage is met or we reached max count
while Coverage.all_passed(MAX_SIMS) == False:
    model.base_tick.set(0)
    model.sub_ticks.set(0)

    # write each transaction to the input file
    inputs.append(model)

    base_count += 1
    if base_count == BASE_DELAY:
        base_count = 0
        # compute expected values to send to simulation
        model.eval(counts)
        pass
    
    outputs.append(model)
    pass

inputs.close()
outputs.close()
