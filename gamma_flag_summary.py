import sys


myms = sys.argv[3]
log_file = 'flag_sum_' + myms[:-3] + '_.log'

# get flag summart from CASA flagdata
flagdata(vis = myms, mode = 'summary')


