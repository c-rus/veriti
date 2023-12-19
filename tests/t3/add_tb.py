# Project  : add
# Engineer : Chase Ruskin
# Created  : 2023-06-17
# Details  :
#   This script generates the I/O test vector files to be used with the 
#   add_tb.vhd testbench. Generic values for `LEN` can be passed through the 
#   command-line. 
#
#   Generates a coverage report as well to indicate the robust of the test.
#
import random
import veriti as vi
from veriti.coverage import Coverage, Covergroup, Coverpoint
from veriti.model import SuperBfm, Signal, Mode

# --- Constants ----------------------------------------------------------------

# define the randomness seed
R_SEED = vi.get_seed(0)

# collect generics from command-line and HDL testbench
GENS = vi.get_generics()

MAX_SIMS = 10_000

# set/collect generics
WIDTH  = int(GENS['LEN'])

# --- Coverage Goals -----------------------------------------------------------

# specify coverage areas

# make sure cin is asserted at least 100 times
cp_cin_asserted = Coverpoint(
    "cin asserted", 
    goal=100
)
# make sure the carry out is generated at least 10 times
cp_cout_gen = Coverpoint(
    "cout generated", 
    goal=10
)
# make sure that in0 has 0 and max value tested at least 10 times
cg_in0_extremes = Covergroup(
    "in0 extremes",
    bins=[0, vi.pow2m1(WIDTH)],
    goal=10,
)
cg_in1_extremes = Covergroup(
    "in1 extremes",
    bins=[0, vi.pow2m1(WIDTH)],
    goal=10,
)
# divide up input space into 16 bins and make sure all bins are tested at least once
# @todo: use 'max_bins' arg to limit bin counting (%)
cg_in0_full = Covergroup(
    "in0 full",
    bins=[i for i in range(0, 16)],
    goal=1,
)
cg_in1_full = Covergroup(
    "in1 full",
    bins=[i for i in range(0, 16)],
    goal=1,
)
# make sure all combinations of input bins are tested at least once
cg_in0_cross_in1 = Covergroup(
    "in0 cross in1",
    bins=[(x, y) for x in range(0, 16) for y in range(0, 16)],
    goal=1,
)
# Check to make sure both inputs are 0 or the max value at the same time.
# It would be more readable to use cover properties here, but if we
# want this included in the coverage reporting for the group, we need it
# here.
cp_in0_in1_eq_0    = Coverpoint(
    "in0 and in1 equal 0", 
    goal=1
)
cp_in0_in1_eq_max  = Coverpoint(
    "in0 and in1 equal max", 
    goal=1
)

# --- Model --------------------------------------------------------------------

# define the bus functional model
class Bfm(SuperBfm):
    entity = 'add'

    def __init__(self):
        self.in0 = Signal(Mode.INPUT, WIDTH)
        self.in1 = Signal(Mode.INPUT, WIDTH)
        self.cin = Signal(Mode.INPUT)

        self.sum = Signal(Mode.OUTPUT, WIDTH)
        self.cout = Signal(Mode.OUTPUT)
        pass


    def evaluate(self):
        result = self.in0.as_int() + self.in1.as_int() + self.cin.as_int()
        temp = Signal(width=WIDTH+1, value=result).as_logic()
        self.sum.set(temp[1:])
        self.cout.set(temp[0])

        cp_cout_gen.cover(self.cout.as_int() == 1)
        return self
    pass


# --- Logic --------------------------------------------------------------------

random.seed(R_SEED)

# create empty test vector files
i_file = vi.InputFile()
o_file = vi.OutputFile()

# generate test cases until total coverage is met or we reached max count
while Coverage.all_passed(MAX_SIMS) == False:
    # create a new input to enter through the algorithm
    txn = Bfm().rand()

    # prioritize reaching coverage for all possible inputs first
    if cg_in0_full.passed() == False:
        txn.in0.set(int(cg_in0_full.next(rand=True) % 16))
    elif cg_in1_full.passed() == False:
        txn.in1.set(int(cg_in1_full.next(rand=True) % 16))
    # generate random numbers that exceed sum vector
    elif cp_cout_gen.passed() == False:
        txn.in0.set(random.randint(1, txn.in0.max()))
        txn.in1.set(vi.pow2m1(WIDTH)+random.randint(1, WIDTH) - txn.in0.as_int())
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

    # update coverages
    cg_in0_cross_in1.cover((int(txn.in0.as_int() % 16), int(txn.in1.as_int() % 16)))
    cg_in0_full.cover(txn.in0.as_int())
    cg_in1_full.cover(txn.in1.as_int())
    cg_in0_extremes.cover(txn.in0.as_int())
    cg_in1_extremes.cover(txn.in1.as_int())
    
    cp_in0_in1_eq_0.cover(txn.in1.as_int() == 0 and txn.in0.as_int() == 0)
    cp_in0_in1_eq_max.cover(txn.in1.as_int() == txn.in1.max() and txn.in0.as_int() == txn.in0.max())
    cp_cin_asserted.cover(txn.cin.as_int() == 1)

    # write each transaction to the input file
    i_file.write(txn)

    # compute expected values to send to simulation
    o_file.write(txn.evaluate())
    pass

print()
print('Seed:', R_SEED)
print("Valid Transaction Count:", Coverage.count())
print("Coverage:", Coverage.percent(), "%")
# display quick summary coverage statistics
print(Coverage.report(False))

# write the full coverage stats to a text file
Coverage.save_report("coverage.txt")