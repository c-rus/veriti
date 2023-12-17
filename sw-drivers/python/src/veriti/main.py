# File: main.py
# Author: Chase Ruskin
# Created: 2023-12-17
# Details:
#   Provides interface between client and veriti as a command-line application.
#


from .lib import to_logic
from .model import SuperBfm as __SuperBfm

def parse_args(bfm: __SuperBfm):
    '''
    Checks the command-line for any args.
    '''
    import argparse

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--code', action='store_true', default=False)
    args, _unknown = parser.parse_known_args()
   
    # print code and exit
    if args.code == True:
        # print the VHDL code for the bfm record type to connect to UUT
        print(bfm.get_vhdl_record_bfm())
        # print VHDL code to make procedure in DRIVER stage
        print(bfm.get_vhdl_process_inputs())
        # print VHDL code to make procedure in the CHECKER stage
        print(bfm.get_vhdl_process_outputs())
        exit(0)
    pass


def do():
    parser = argparse.ArgumentParser(allow_abbrev=False)


import argparse

def main():
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--code', action='store_true', default=False)
    parser.add_argument('-g', '--generic', action='append', nargs='*', type=str)

    num = to_logic(21)
    print('hello world', num)


if __name__ == '__main__':
    main()
    pass