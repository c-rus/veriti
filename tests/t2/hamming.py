import unittest
from typing import List

# --- Classes and Functions ----------------------------------------------------

def set_parity_bit(arr: List[int], use_even=True) -> bool:
    '''
    Checks if the `arr` has an odd amount of 0's in which case the parity bit
    must be set to '1' to achieve an even parity.

    If `use_even` is set to `False`, then odd parity will be computed and will
    seek to achieve an odd amount of '1's (including parity bit).
    '''
    # count the number of 1's in the list
    return (arr.count(1) % 2) ^ (use_even == False)


# --- Tests --------------------------------------------------------------------

# unit tests for various hamming functions
class TestHammingEcc(unittest.TestCase):
    def test_compute_parity(self):
        # even parity
        check = set_parity_bit([1, 0, 0])
        self.assertEqual(check, 1)

        check = set_parity_bit([1, 0, 0, 1])
        self.assertEqual(check, 0)

        # odd parity
        check = set_parity_bit([1, 0, 0, 1], use_even=False)
        self.assertEqual(check, 1)

        check = set_parity_bit([1, 0, 1, 1], use_even=False)
        self.assertEqual(check, 0)
        pass

    pass
