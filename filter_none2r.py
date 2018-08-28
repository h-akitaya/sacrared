#!/usr/bin/env python
#
#  modify FILTER header value from NONE to r
#    (for MuSaSHI r-band arm)
#
#      usage: filter_none2r.py r*.fits
#
#    Ver  1.0  2018/03/21  H. Akitaya
#    Ver  2.0  2018/08/28  H. Akitaya; change import style
#


import os,sys
import sacrafits import as sfts

if __name__ == '__main__':
    if len(sys.argv) == 1:
        exit
    fnin = sys.argv
    del fnin[0]
    for fn in fnin:
        name, ext = os.path.splitext(fn)
        if ext != ".fits":
            continue
        img = SacraFits(fn)
        img = ftsf.getHeaderValue('FILTER')
#        print fltr
        if img == 'NONE':
            img.setHeaderValue('FILTER', 'r', 'filtername')
            print('%s FILTER header NONE -> r\n' % fn)
            img.addHistory('%s FILTER header NONE -> r' % fn)
            img.updateFitsFile()
        img.close()
