#!/usr/bin/env python
#
#  make dark file
#    (for FLI-CCDs)
#
#      usage: mkdark band exptime(msec)
#
#    Ver  1.0  2018/03/21  H. Akitaya
#


import os, sys
from preproc import *

def main():
    if len(sys.argv) < 3:
        exit(1)
    band=sys.argv[1]
    try:
        exptime=float(sys.argv[2])
    except:
        sys.stderr.write("Wrong exposure time")
        exit(1)
    #main
    sf=SacraFile(DT_DARK)
    sf.mkDark(band, exptime)
    
if __name__ == '__main__':
    main()
