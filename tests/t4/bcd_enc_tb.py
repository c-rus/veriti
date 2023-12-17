# Project  : bcd-encoder
# Engineer : Chase Ruskin
# Created  : 2021/10/17
# Details  :
#   This script generates the I/O test vector files to be used with the 
#   bcd_enc_tb.vhd testbench. Generic values for `DIGITS`` and `LEN` can be 
#   passed through the command-line. 
#
#   Generates a coverage report as well to indicate the robust of the test.
#
import random
import veriti as vi
from veriti.coverage import Coverage, Covergroup, Coverpoint
from veriti.model import SuperBfm, Signal, Mode, InputFile, OutputFile

# --- Constants ----------------------------------------------------------------

# define the randomness seed
R_SEED = vi.get_seed(0)

# collect generics from command-line and HDL testbench
GENS = vi.get_generics()

MAX_SIMS = 10_000

# set/collect generics
DIGITS = int(GENS['DIGITS'])
WIDTH  = int(GENS['LEN'])

# LEN | CYCLES
# --- | ----------
#  3  | 7  = 3 + 4 
#  4  | 9  = 4 + 5
#  5  | 11 = 5 + 6
FSM_DELAY = WIDTH+WIDTH+1+1

# --- Coverage Goals -----------------------------------------------------------

# specify coverage areas
cp_go_while_active = Coverpoint(
    "go while active", 
    goal=100
)
cp_overflow_en = Coverpoint(
    "overflow enabled", 
    goal=50, 
    bypass=(vi.pow2m1(WIDTH) < (10**DIGITS))
)
cp_bin_while_active = Coverpoint(
    "input changes while active", 
    goal=100
)
cg_unique_inputs = Covergroup(
    "binary value variants", 
    bins=[i for i in range(0, pow(2, WIDTH))]
)
cg_overflow = Covergroup(
    "overflow variants", 
    bins=[0, 1], 
    bypass=(vi.pow2m1(WIDTH) < (10**DIGITS))
)
cg_extreme_values = Covergroup(
    "extreme inputs", 
    bins=[0, vi.pow2m1(WIDTH)]
)

# --- Models -------------------------------------------------------------------

# define the bus-functional-model
class Bfm(SuperBfm):
    entity = 'bcd_enc'

    def __init__(self):
        self.go = Signal(mode=Mode.INPUT)
        self.bin = Signal(mode=Mode.INPUT, width=WIDTH)

        self.bcd = Signal(mode=Mode.OUTPUT, width=(4*DIGITS))
        self.ovfl = Signal(mode=Mode.OUTPUT)
        self.done = Signal(mode=Mode.OUTPUT)
        pass


    def model(self, *args):
        # separate each digit
        digits = []
        word = self.bin.as_int()
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

        cg_overflow.cover(self.ovfl.as_int())
        cp_overflow_en.cover(self.ovfl.as_int() == 1)

        # write each digit to output file
        bin_digits: str = ''
        for d in digits:
            bin_digits += vi.to_logic(d, 4)
        self.bcd.set(bin_digits)

        self.done.set(1)
        return self

    pass


# --- Logic --------------------------------------------------------------------

random.seed(R_SEED)

# create empty test vector files
i_file = InputFile()
o_file = OutputFile()

# initialize the values with defaults
i_file.write(Bfm())

# generate test cases until total coverage is met or we reached max count
while Coverage.all_passed(MAX_SIMS) == False:
    # create a new input to enter through the algorithm
    txn = Bfm()
    txn.go.set(1)
    txn.bin.rand()

    # prioritize reaching coverage for all possible inputs first
    if cg_unique_inputs.passed() == False:
        txn.bin.set(cg_unique_inputs.next(rand=True))

    # record the input if its unique and not been tried before
    cg_extreme_values.cover(txn.bin.as_int())
    cg_unique_inputs.cover(txn.bin.as_int())

    # write each transaction to the input file
    i_file.write(txn)

    # alter the input while the computation is running
    for _ in range(1, FSM_DELAY):
        bad = Bfm().rand()
        cp_bin_while_active.cover(bad.bin.as_int() != txn.bin.as_int())
        cp_go_while_active.cover(bad.go.as_int() == 1)
        i_file.write(bad)

    # compute expected values to send to simulation
    o_file.write(txn.model())
    pass

print()
print('Seed:', R_SEED)
print("Test Count:", Coverage.count())
print("Coverage:", Coverage.percent(), "%")
# write/display coverage statistics
print(Coverage.report(False))
# write the full coverage stats to a text file
Coverage.save_report("coverage.txt")
