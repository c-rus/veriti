# hard-code the raw data layer for testing hardware driver functions
DATA: str = '''\
100010101001
100110011001
21
4
0
1
'''

with open('numbers.dat', 'w') as f:
    f.write(DATA)
    pass
