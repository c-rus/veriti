# File: config.py
# Author: Chase Ruskin
# Created: 2023-12-17
# Details:
#   Stores constants used across the library.
#

__SEED: int = None

VHDL_DRIVER_PROC_NAME = 'drive'
VHDL_LOADER_PROC_NAME = 'load'
VHDL_ASSERT_PROC_NAME = 'log_assertion'

TRACE_FILE_EXT = '.trace'
LOG_FILE_EXT = '.log'

LOG_TIMESTAMP_L_TOKEN = '['
LOG_TIMESTAMP_R_TOKEN = ']'

LOG_CAUSE_L_TOKEN = '\"'
LOG_CAUSE_R_TOKEN = '\"'

TAB_SIZE = 2

def TAB(n: int):
    return (' ' * TAB_SIZE) * n