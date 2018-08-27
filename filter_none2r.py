#!/usr/bin/env python
#
#  modify FILTER header value from NONE to r
#    (for MuSaSHI r-band arm)
#
#      usage: filter_none2r.py r*.fits
#
#    Ver  1.0  2018/03/21  H. Akitaya
#


import os,sys
from sacrafits import *

def main():
    if len(sys.argv) == 1:
        exit
    fnin=sys.argv
    del fnin[0]
    for fn in fnin:
        name, ext = os.path.splitext(fn)
        if ext != ".fits":
            continue
        ftsf=SacraFits(fn)
        fltr = ftsf.getHeaderValue('FILTER')
#        print fltr
        if fltr == 'NONE':
            ftsf.setHeaderValue('FILTER', 'r', 'filtername')
            print('%s FILTER header NONE -> r\n' % fn)
            ftsf.addHistory('%s FILTER header NONE -> r' % fn)
            ftsf.updateFitsFile()
        ftsf.close()
        
if __name__ == '__main__':
    main()
