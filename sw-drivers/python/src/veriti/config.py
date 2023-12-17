# File: config.py
# Author: Chase Ruskin
# Created: 2023-12-17
# Details:
#   Stores constants used across the library.
#

__SEED: int = None

VHDL_DRIVER_PROC_NAME = 'drive'
VHDL_LOADER_PROC_NAME = 'load'
VHDL_ASSERT_PROC_NAME = 'assert_eq'

def TAB(n: int):
    return (' ' * 4) * n