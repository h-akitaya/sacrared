#!/usr/bin/env python
#
#  make flat file
#    (for FLI-CCDs)
#
#      usage: mkflat band exptime(msec)
#
#    Ver  1.0  2018/03/22  H. Akitaya
#    Ver  1.1  2018/08/21  H. Akitaya
#    Ver  2.0  2018/08/28  H. Akitaya; rename reference package
#


import os, sys
import sacrafile as sf
from scrredmisc import *
MKFLAT_MODE = MOD_MIMG

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
    sffl = sf.SacraFile(DT_FLAT)
    sffl.make_flat(band, exptime, MKFLAT_MODE)
