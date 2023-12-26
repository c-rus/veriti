# Project  : add
# Engineer : Chase Ruskin
# Created  : 2023-06-17
# Details  :
#   This script generates the I/O test vector files to be used with the 
#   add_tb.vhd testbench. Generic values for `LEN` can be passed through the 
#   command-line. 
#
#   Generates a coverage report as well to indicate the robust of the test.

import random
from veriti.prelude import *

# initialize the randomness seed
random.seed(rng_seed(0))
# collect generics
WIDTH = get_generic(key='LEN', type=int)

MAX_SIMS = 5_000

# Specify coverage areas

# Cover the case that cin is asserted at least 100 times.
cp_cin_asserted = Coverpoint(
    "cin asserted", 
    goal=100,
    mapping=lambda x: int(x) == 1
)

# Cover the case that the carry out is generated at least 10 times.
cp_cout_gen = Coverpoint(
    "cout generated", 
    goal=10,
    mapping=lambda x: int(x) == 1
)

# Cover the extreme edge cases for in0 (min and max) at least 10 times.
cg_in0_extremes = Covergroup(
    "in0 extremes",
    bins=[0, pow2m1(WIDTH)],
    goal=10,
)

# Cover the extreme edge cases for in1 (min and max) at least 10 times.
cg_in1_extremes = Covergroup(
    "in1 extremes",
    bins=[0, pow2m1(WIDTH)],
    goal=10,
)

# Cover the entire range for in0 into at most 16 bins and make sure
# each bin is tested at least once.
cg_in0_full = Coverrange(
    "in0 full",
    span=range(0, pow2(WIDTH)),
    goal=1,
    max_steps=16
)

# Cover the entire range for in1 into at most 16 bins and make sure 
# each bin is tested at least once.
cg_in1_full = Coverrange(
    "in1 full",
    span=range(0, pow2(WIDTH)),
    goal=1,
    max_steps=16
)

# Make sure all combinations of input bins are tested at least once. It is possible
# to define this cross coverage as a Coverrange.
cg_in0_cross_in1 = Coverrange(
    "in0 cross in1",
    span=range(cg_in0_full.get_step_count() * cg_in1_full.get_step_count()),
    goal=1,
    max_steps=None,
    mapping=lambda pair: (cg_in0_full.get_step_count() * int(int(pair[0]) / cg_in0_full.get_range().step)) + int(int(pair[1]) / cg_in1_full.get_range().step),
)

# Check to make sure both inputs are 0 at the same time at least once.
cp_in0_in1_eq_0    = Coverpoint(
    "in0 and in1 equal 0", 
    goal=1,
    mapping=lambda pair: int(pair[0]) == 0 and int(pair[1]) == 0
)

# Check to make sure both inputs are the maximum value at the same time at least once.
cp_in0_in1_eq_max  = Coverpoint(
    "in0 and in1 equal max", 
    goal=1,
    mapping=lambda pair: int(pair[0]) == pair[0].max() and int(pair[1]) == pair[1].max()
)

# Define the functional model
class Adder:

    def __init__(self, width: int):
        # inputs
        self.in0 = Signal(width=width)
        self.in1 = Signal(width=width)
        self.cin = Signal()
        # outputs
        self.sum = Signal(width=width)
        self.cout = Signal()
        pass

    def evaluate(self):
        result = self.in0.as_int() + self.in1.as_int() + self.cin.as_int()
        temp = Signal(width=self.in0.width()+1, value=result, big_endian=True).as_logic()
        # slice and dice
        self.sum.set(temp[1:])
        self.cout.set(temp[0])

        cp_cout_gen.cover(self.cout)
        return self
    pass

# Prepare the traces for simulation

# create empty test vector files
inputs = TraceFile('inputs', Mode.IN).open()
outputs = TraceFile('outputs', Mode.OUT).open()

model = Adder(width=WIDTH)

# generate test cases until total coverage is met or we reached max count
while Coverage.all_passed(MAX_SIMS) == False:
    # create a new input to enter through the algorithm
    txn = randomize(model)

    # prioritize reaching coverage for all possible inputs first
    if cg_in0_full.passed() == False:
        txn.in0.set(int(cg_in0_full.next(rand=True)))
    elif cg_in1_full.passed() == False:
        txn.in1.set(int(cg_in1_full.next(rand=True)))
    # generate random numbers that exceed sum vector
    elif cp_cout_gen.passed() == False:
        txn.in0.set(random.randint(1, txn.in0.max()))
        txn.in1.set(pow2m1(WIDTH) + random.randint(1, WIDTH) - txn.in0.as_int())
    # provide an extreme value for in0
    elif cg_in0_extremes.passed() == False:
        txn.in0.set(random.choice([txn.in0.min(), txn.in0.max()]))
    # provide an extreme value for in1
    elif cg_in1_extremes.passed() == False:
        txn.in1.set(random.choice([txn.in1.min(), txn.in1.max()]))
    # assert cin on this test case
    elif cp_cin_asserted.passed() == False:
        txn.cin.set(1)
    # make both in0 and in1 equal to 0 (minimum edge case)
    elif cp_in0_in1_eq_0.passed() == False:
        txn.in0.set(0)
        txn.in1.set(0)
    # make both in0 and in1 equal to max (maximum edge case)
    elif cp_in0_in1_eq_max.passed() == False:
        txn.in0.set(txn.in0.max())
        txn.in1.set(txn.in1.max())
        pass

    input_pair = (txn.in0, txn.in1)

    # update coverages
    cg_in0_full.cover(txn.in0)
    cg_in1_full.cover(txn.in1)
    cg_in0_extremes.cover(int(txn.in0))
    cg_in1_extremes.cover(int(txn.in1))
    cg_in0_cross_in1.cover(input_pair)
    cp_in0_in1_eq_0.cover(input_pair)
    cp_in0_in1_eq_max.cover(input_pair)
    cp_cin_asserted.cover(txn.cin)

    # write each incoming transaction to the DUT
    inputs.append(txn)
    # compute expected values to send to simulation
    txn = model.evaluate()
    # write each expected outgoing transaction from the DUT
    outputs.append(txn)
    pass

inputs.close()
outputs.close()

print()
print('Seed:', rng_seed())
print("Valid Transaction Count:", Coverage.count())
print("Coverage:", Coverage.percent(), "%")
# display quick summary coverage statistics
print(Coverage.report(verbose=False))

# write the full coverage stats to a text file
Coverage.save_report()

