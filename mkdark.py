#!/usr/bin/env python
#
#  make dark file
#    (for FLI-CCDs)
#
#      usage: mkdark band exptime(msec)
#
#    Ver  1.0  2018/03/21  H. Akitaya
#    Ver  2.0  2018/08/28  H. Akitaya; rename package name
#


import os, sys
import sacrafits as sf

if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit(1)
    band=sys.argv[1]
    try:
        exptime=float(sys.argv[2])
    except:
        sys.stderr.write("Wrong exposure time")
        exit(1)
    #main
    sfdk = sf.SacraFile(DT_DARK)
    sfdk.mkDark(band, exptime)
