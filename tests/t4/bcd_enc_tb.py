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
from veriti.trace import TraceFile
from veriti.coverage import Coverage, Covergroup, Coverpoint
from veriti.model import Signal, Mode

# --- Constants ----------------------------------------------------------------

# define the randomness seed
R_SEED = vi.rng_seed(0)

# collect generics
DIGITS = vi.get_generic('DIGITS', type=int)
WIDTH  = vi.get_generic('LEN', type=int)

# LEN | CYCLES
# --- | ----------
#  3  | 7  = 3 + 4 
#  4  | 9  = 4 + 5
#  5  | 11 = 5 + 6
FSM_DELAY = WIDTH+WIDTH+1+1

MAX_SIMS = 10_000

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
class BcdEncoder:

    def __init__(self, width: int, digits: int):
        self.go = Signal(mode=Mode.IN)
        self.bin = Signal(mode=Mode.IN, width=width)

        self.bcd = Signal(mode=Mode.OUT, width=(4*digits))
        self.ovfl = Signal(mode=Mode.OUT)
        self.done = Signal(mode=Mode.OUT)
        pass


    def evaluate(self):
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
            pass
        
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
inputs = TraceFile('inputs', Mode.IN).open()
outputs = TraceFile('outputs', Mode.OUT).open()

# initialize the values with defaults
inputs.append(BcdEncoder(WIDTH, DIGITS))

# generate test cases until total coverage is met or we reached max count
while Coverage.all_passed(MAX_SIMS) == False:
    # create a new input to enter through the algorithm
    txn = BcdEncoder(
        width=WIDTH,
        digits=DIGITS
    )
    txn.go.set(1)
    txn.bin.rand()

    # prioritize reaching coverage for all possible inputs first
    if cg_unique_inputs.passed() == False:
        txn.bin.set(cg_unique_inputs.next(rand=True))

    # record the input if its unique and not been tried before
    cg_extreme_values.cover(txn.bin.as_int())
    cg_unique_inputs.cover(txn.bin.as_int())

    # write each transaction to the input file
    inputs.append(txn)

    # alter the input while the computation is running
    for _ in range(1, FSM_DELAY):
        bad = vi.randomize(BcdEncoder(WIDTH, DIGITS))
        cp_bin_while_active.cover(bad.bin.as_int() != txn.bin.as_int())
        cp_go_while_active.cover(bad.go.as_int() == 1)
        inputs.append(bad)

    # compute expected values to send to simulation
    outputs.append(txn.evaluate())
    pass

print()
print('Seed:', R_SEED)
print("Valid Transaction Count:", Coverage.count())
print("Coverage:", Coverage.percent(), "%")
# write/display coverage statistics
print(Coverage.report(False))
# write the full coverage stats to a text file
Coverage.save_report("coverage.txt")

inputs.close()
outputs.close()