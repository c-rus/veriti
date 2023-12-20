# File: main.py
# Author: Chase Ruskin
# Created: 2023-12-17
# Details:
#   Provides interface between client and veriti as a command-line application.
#

import argparse, json
from . import config
from . import log
from . import __version__


def main():
    parser = argparse.ArgumentParser(prog='veriti', allow_abbrev=False)
    parser.add_argument('--version', action='version', version=__version__.VERSION)

    sub_parsers = parser.add_subparsers(dest='subcommand', metavar='command')

    # subcommand: 'make'
    parser_make = sub_parsers.add_parser('make', help='create HDL code synchronized to the model')

    parser_make.add_argument('--bfm', action='store_true', default=False, help='generate the HDL bus functional model')
    parser_make.add_argument('--send', action='store_true', default=False, help='generate the HDL sending procedure')
    parser_make.add_argument('--score', action='store_true', default=False, help='generate the HDL scoring procedure')
    parser_make.add_argument('json', type=str, help='JSON data defining design-under-test\'s interface')

    # subcommand: 'read'
    parser_read = sub_parsers.add_parser('read', help='analyze post-simulation logged outcomes')

    parser_read.add_argument('--log', type=str, required=True, help='path to log file')
    parser_read.add_argument('--level', type=int, default=log.Level.WARN.value, help='severity level')

    # subcommand: 'check'
    parser_check = sub_parsers.add_parser('check', help='verify post-simulation logged outcomes')

    parser_check.add_argument('--log', type=str, help='path to log file')
    parser_check.add_argument('--cov', type=str, help='path to coverage file')
    
    args: argparse.Namespace = parser.parse_args()

    # branch on subcommand
    sc = args.subcommand
    if sc == 'make':
        make(args)
    elif sc == 'read':
        data = log.read(args.log, args.level)
        print(data)
    elif sc == 'check':
        result = log.check(args.log, args.cov)
        if result == True:
            print('Passed verification')
            exit(0)
        if result == False:
            print('Failed verification')
            exit(101)
        pass
    elif sc == None:
        parser.print_help()
        pass
    pass


def make(args: argparse.Namespace):
    # process the json data
    data = json.loads(args.json)

    # when creating driver and scorer, also grab list of port names (in their assembled order)
    # so it synchronizes with which bit is which each line
    # ... requires knowledge of the BFM defined in the SW model script
    # or when writing tests in SW model, load the json data so it can get proper order from file

    zero_raised = args.bfm == False and args.send == False and args.score == False
    # create a function/command to take in a log file and coverage file to perform post-simulation analysis
    # and provide a meaningful exit code and messages
    if args.bfm == True or zero_raised == True:
        print(get_vhdl_record_bfm(data['ports'], data['entity']))
    if args.send == True or zero_raised == True:
        print(get_vhdl_process_inputs(data['ports']))
    if args.score == True or zero_raised == True:
        print(get_vhdl_process_outputs(data['ports'], data['entity']))
    pass


def get_vhdl_process_inputs(ports):
    '''
    Generates valid VHDL code snippet for the reading procedure to parse the
    respective model and its signals in the correct order as they are going
    to be written to the corresponding test vector file.

    This procedure assumes the package veriti is already in scope.
    '''

    body = ''
    for p in ports:
        if p['mode'].lower() != 'in':
            continue
        body += config.TAB(2) + config.VHDL_DRIVER_PROC_NAME + '(row, bfm.'+p['name']+');\n'
        pass

    result = '''
procedure send_transaction(file fd: text) is
''' + config.TAB(1) + '''variable row: line;
begin
''' + config.TAB(1) + '''if endfile(fd) = false then
''' + config.TAB(2) + '''readline(fd, row);
''' + body + \
config.TAB(1) + '''end if;
end procedure;'''
    return result


def get_vhdl_process_outputs(ports, entity) -> str:
    '''
    Generates valid VHDL code snippet for the reading procedure to parse the
    respective model and its signals in the correct order as they are going
    to be written to the corresponding test vector file.

    This procedure assumes the package veriti is already in scope.
    '''
    body = ''
    for p in ports:
        if p['mode'].lower() != 'out':
            continue
        body += config.TAB(2) + config.VHDL_LOADER_PROC_NAME + '(row, expct.'+p['name']+');\n'
        body += config.TAB(2) + config.VHDL_ASSERT_PROC_NAME + '(events, bfm.'+p['name']+', expct.'+p['name']+', \"'+p['name']+'\");\n'
        pass

    result = '''
procedure score_transaction(file fd: text) is 
''' + config.TAB(1) + '''variable row: line;
''' + config.TAB(1) + '''variable expct: '''+entity+'''_bfm;
begin
''' + config.TAB(1) + '''if endfile(fd) = false then
''' + config.TAB(2) + '''readline(fd, row);
''' + body + \
config.TAB(1) + '''end if;
end procedure;'''

    return result
    

def get_vhdl_record_bfm(ports, entity) -> str:
    # determine spacing for neat alignment of signals
    longest_len = 0
    for item in ports:
        id = str(item['name'])
        if len(id) > longest_len:
            longest_len = len(id)
        pass

    body = ''
    # write each signal to the bfm record
    for item in ports:
        id = str(item['name'])
        dt = str(item['type'])
        _spacing = (' ' * (longest_len-len(id))) + ' '
        body += config.TAB(1) + id + ': ' + dt + ';\n'
        pass
    result = '''
type '''+entity+'''_bfm is record
''' + body + \
'''end record;

signal bfm: '''+entity+'''_bfm;
file events: text open write_mode is "events.log";
'''    

    return result


if __name__ == '__main__':
    main()
    pass