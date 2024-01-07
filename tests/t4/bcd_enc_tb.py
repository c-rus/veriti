# Project: veriti
# Script: bcd_enc_tb.py
#
# This script generates the I/O test vector files to be used with the 
# bcd_enc_tb.vhd testbench. It also produces a coverage report to indicate the 
# robust of the tests.

import random
import veriti as vi
from veriti.trace import TraceFile
from veriti.coverage import Coverage, CoverGroup, CoverPoint
from veriti.model import Signal, Mode

# Declare test-wide constants

RNG_SEED = vi.rng_seed(0)

# collect generics
DIGITS = vi.get_generic('DIGITS', type=int)
WIDTH  = vi.get_generic('LEN', type=int)

# LEN | CYCLES
# --- | ----------
#  3  | 7  = 3 + 4 
#  4  | 9  = 4 + 5
#  5  | 11 = 5 + 6
FSM_DELAY = WIDTH+WIDTH+1+1

MAX_SIMS = 1_000

# Define the bus-functional model

class BcdEncoder:

    def __init__(self, width: int, digits: int):
        self.go = Signal(mode=Mode.IN, dist=[0.3, 0.7])
        self.bin = Signal(mode=Mode.IN, width=width)

        self.bcd = Signal(mode=Mode.OUT, width=(4*digits))
        self.ovfl = Signal(mode=Mode.OUT)
        self.done = Signal(mode=Mode.OUT)
        pass


    def evaluate(self):
        # separate each digit
        digits = []
        word = self.bin.to_int()
        while word >= 10:
            digits.insert(0, (word % 10))
            word = int(word/10)
        digits.insert(0, word)
        
        self.ovfl.set(0)
        # check if an overflow exists on conversion given digit constraint
        diff = DIGITS - len(digits)
        if(diff < 0):
            self.ovfl.set(1)
            # trim off left-most digits
            digits = digits[abs(diff):]
        # pad left-most digit positions with 0's
        elif(diff > 0):
            for _i in range(diff):
                digits.insert(0, 0)
            pass

        # write each digit to output file
        bin_digits: str = ''
        for d in digits:
            bin_digits += vi.to_logic(d, 4)
        self.bcd.set(bin_digits)

        self.done.set(1)
        return self

    pass

model = BcdEncoder(width=WIDTH, digits=DIGITS)
fake_model = BcdEncoder(width=WIDTH, digits=DIGITS)

# Coverage Goals - specify coverage areas

cg_unique_inputs = CoverGroup(
    "binary value variants", 
    bins=[i for i in model.bin.get_range()],
    target=model.bin,
)

cp_go_while_active = CoverPoint(
    "go while active", 
    goal=100,
    target=fake_model.go,
    cover=lambda x: int(x) == 1,
)

cp_overflow_en = CoverPoint(
    "overflow enabled", 
    goal=10, 
    bypass=model.bin.max() < (10**DIGITS),
    target=model.ovfl,
    cover=lambda x: int(x) == 1,
)

cp_bin_while_active = CoverPoint(
    "input changes while active", 
    goal=100
)

cg_overflow = CoverGroup(
    "overflow variants", 
    bins=[0, 1], 
    bypass=model.bin.max() < (10**DIGITS),
    target=model.ovfl,
)

cg_extreme_values = CoverGroup(
    "extreme inputs", 
    bins=[model.bin.min(), model.bin.max()],
    target=model.bin
)

# Generate the test vectors

random.seed(RNG_SEED)

# create empty test vector files
inputs = TraceFile('inputs.trace', Mode.IN).open()
outputs = TraceFile('outputs.trace', Mode.OUT).open()

# initialize the values with defaults
inputs.append(BcdEncoder(WIDTH, DIGITS))

# generate test cases until total coverage is met or we reached max count
while Coverage.all_passed(MAX_SIMS) == False:
    # create a new input to enter through the algorithm
    vi.randomize(model, strategy='linear')
    model.go.set(1)

    # write each transaction to the input file
    inputs.append(model)

    # alter the input while the computation is running
    for _ in range(1, FSM_DELAY):
        vi.randomize(fake_model)
        cp_bin_while_active.cover(fake_model.bin.to_int() != model.bin.to_int())
        inputs.append(fake_model)

    # compute expected values to send to simulation
    model.evaluate()
    # write expected outputs for the input transaction
    outputs.append(model)
    pass

inputs.close()
outputs.close()