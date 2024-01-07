# Project: veriti
# Script: timer_tb.py
#   
# This script generates the I/O test vector files to be used with the 
# timer_tb.vhd testbench. It also states a coverage report to indicate the 
# robust of the tests.
#
# This script generate tests cycle-by-cycle for the HDL simulation.

import random
from veriti.prelude import *

# collect generics
SUB_DELAYS  = get_generic('SUB_DELAYS', type=[int])
BASE_DELAY  = get_generic('BASE_DELAY', type=int)

MAX_SIMS = 1_000

# Define functional model

class Timer:
    def __init__(self):
        self.sub_ticks = Signal(width=len(SUB_DELAYS), mode=Mode.OUT, endianness='little')
        self.base_tick = Signal(mode=Mode.OUT)

        self.base_count = 0
        self.counts = [0] * len(SUB_DELAYS)
        pass

    def evaluate(self):
        self.base_count += 1

        if self.base_count < BASE_DELAY:
            self.base_tick.set(0)
            self.sub_ticks.set(0)
            return self
        
        # base count has reached the number of expected delays
        self.base_count = 0
        self.base_tick.set(1)

        # check if any subtick counts have reached their delay times
        for i, delay in enumerate(SUB_DELAYS):
            time = self.counts[i]
            if time == delay-1:
                self.sub_ticks.set_bit(i, '1')
                self.counts[i] = 0
            else:
                self.sub_ticks.set_bit(i, '0')
                self.counts[i] += 1
            pass
        return self
    pass


model = Timer()

# Define coverage goals

# verify each tick is enabled at least 3 times
for i, tick in enumerate(SUB_DELAYS):
    CoverPoint(
        name='tick '+str(tick)+' targeted',
        goal=3,
        sink=model.sub_ticks,
        # capture `i` by value not by reference
        cover=lambda x, i=i: int(x[i]) == 1,
    )

# verify the common delay is enabled
cp_base = CoverPoint(
    name="base tick targeted", 
    goal=3,
    sink=model.base_tick
)

# set the randomness seed
random.seed(rng_seed(0))

# create empty test vector files
inputs = TraceFile('inputs.trace', mode='in').open()
outputs = TraceFile('outputs.trace', mode='out').open()

# generate test cases until total coverage is met or we reached max count
while Coverage.all_passed(MAX_SIMS) == False:
    # write each transaction to the input file
    inputs.append(model)
    # compute expected values to send to simulation
    model.evaluate()
    # write each expected output of the transaction to the output file
    outputs.append(model)
    pass

inputs.close()
outputs.close()
