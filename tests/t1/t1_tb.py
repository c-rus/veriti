# hard-code the raw data layer for testing hardware driver functions
DATA: str = '''\
100010101001,100110011001,1,0,
100010101001,100110011001,1,1,
100010101001,100110011001,1,0,
100010101001,100110011001,1,0,
'''

with open('inputs.trace', 'w') as f:
    f.write(DATA)
    pass


DATA: str = '''\
1,
1,
0,
1,
'''

with open('outputs.trace', 'w') as f:
    f.write(DATA)
    pass