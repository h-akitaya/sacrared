#!/usr/bin/env python
#
#  make flat file
#    (for FLI-CCDs)
#
#      usage: mkflat band exptime(msec)
#
#    Ver  1.0  2018/03/22  H. Akitaya
#    Ver  1.1  2018/08/21  H. Akitaya
#


import os, sys
from preproc import *
from scrredmisc import *
MKFLAT_MODE=MOD_MIMG

if __name__ == '__main__':
    mode = MOD_MIMG
    if len(sys.argv) < 3:
        exit(1)
    band=sys.argv[1]
    try:
        exptime=float(sys.argv[2])
    except:
        sys.stderr.write("Wrong exposure time")
        exit(1)
    #main
    sf=SacraFile(DT_FLAT)
    sf.mkFlat(band, exptime, MKFLAT_MODE)
