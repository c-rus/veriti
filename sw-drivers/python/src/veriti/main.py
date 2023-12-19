# File: main.py
# Author: Chase Ruskin
# Created: 2023-12-17
# Details:
#   Provides interface between client and veriti as a command-line application.
#

import argparse, json
from . import config

def main():
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--bfm', action='store_true', default=False, help='generate the HDL bus functional model')
    parser.add_argument('--driver', action='store_true', default=False, help='generate the HDL driving procedure')
    parser.add_argument('--scorer', action='store_true', default=False, help='generate the HDL scoring procedure')
    parser.add_argument('json', help='JSON data defining design-under-test\'s interface')

    args = parser.parse_args()

    # process the json data
    data = json.loads(args.json)

    # when creating driver and scorer, also grab list of port names (in their assembled order)
    # so it synchronizes with which bit is which each line
    # ... requires knowledge of the BFM defined in the SW model script
    # or when writing tests in SW model, load the json data so it can get proper order from file

    # create a function/command to take in a log file and coverage file to perform post-simulation analysis
    # and provide a meaningful exit code and messages
    if args.bfm == True:
        print(get_vhdl_record_bfm(data['ports'], data['entity']))
    if args.driver == True:
        print(get_vhdl_process_inputs(data['ports']))
    if args.scorer == True:
        print(get_vhdl_process_outputs(data['ports'], data['entity']))

    pass


def get_vhdl_process_inputs(ports):
    '''
    Generates valid VHDL code snippet for the reading procedure to parse the
    respective model and its signals in the correct order as they are going
    to be written to the corresponding test vector file.

    This procedure assumes the package veriti is already in scope.
    '''
    result = '''
-- This procedure is auto-generated by veriti. DO NOT EDIT.
procedure drive_transaction(file fd: text) is 
    variable row : line;
begin
    if endfile(fd) = false then
        -- drive a transaction
        readline(fd, row);
'''
    for p in ports:
        if p['mode'].lower() != 'in':
            continue
        result += config.TAB(2) + config.VHDL_DRIVER_PROC_NAME + '(row, bfm.'+p['name']+');\n'
    result += '''    end if;
end procedure;
'''
    return result


def get_vhdl_process_outputs(ports, entity) -> str:
    '''
    Generates valid VHDL code snippet for the reading procedure to parse the
    respective model and its signals in the correct order as they are going
    to be written to the corresponding test vector file.

    This procedure assumes the package veriti is already in scope.
    '''
    result = '''
-- This procedure is auto-generated by veriti. DO NOT EDIT.
procedure score(file fd: text; file logfile: text) is 
    variable row : line;
    variable expct : '''+entity+'''_bfm;
begin
    if endfile(fd) = false then
        -- compare measured outputs with expected outputs
        readline(fd, row);
'''
    for p in ports:
        if p['mode'].lower() != 'out':
            continue
        result += config.TAB(2) + config.VHDL_LOADER_PROC_NAME + '(row, expct.'+p['name']+');\n'
        result += config.TAB(2) + config.VHDL_ASSERT_PROC_NAME + '(logfile, bfm.'+p['name']+', expct.'+p['name']+', \"'+p['name']+'\");\n'
        pass
    result += config.TAB(1) + '''end if;
end procedure;
'''
    return result
    

def get_vhdl_record_bfm(ports, entity) -> str:
    result = '''
-- This record is auto-generated by veriti. DO NOT EDIT.
type '''+entity+'''_bfm is record
'''
    # determine spacing for neat alignment of signals
    longest_len = 0
    for item in ports:
        id = str(item['name'])
        if len(id) > longest_len:
            longest_len = len(id)
        pass

    # write each signal to the bfm record
    for item in ports:
        id = str(item['name'])
        dt = str(item['type'])
    
        result += config.TAB(1) + id + ' ' + (' ' * (longest_len-len(id))) + ' : ' + dt + ';\n'
        pass
    
    result += '''end record;

signal bfm : '''+entity+'''_bfm;
'''
    return result


if __name__ == '__main__':
    main()
    pass