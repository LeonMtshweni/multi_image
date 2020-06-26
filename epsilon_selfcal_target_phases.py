from __future__ import print_function
import sys

myms = sys.argv[3]
myuvrange = sys.argv[4]

# fix the white space problem
if myuvrange == 'nill':
    myuvrange = ''

gtab = myms + '_.GP0'
ref_ant = 'm010'

# solve for the gain phases
gaincal(vis=myms,
    field='0',
    uvrange=myuvrange,
    caltable=gtab,
    refant = ref_ant,
    solint='120s',
    solnorm=False,
    combine='',
    minsnr=3,
    calmode='p',
    parang=False,
    gaintable=[],
    gainfield=[],
    interp=[],
    append=False)


# apply gain phase solutions
applycal(vis=myms,
    gaintable=[gtab],
    field='0',
    calwt=False,
    parang=False,
    applymode='calonly',
    gainfield='0',
    interp = ['nearest'])
