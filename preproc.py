#!/usr/bin/env python
#
# preprocessing for MuSaSHI image data
#
#    2017/xx/xx  Ver 1.0  H. Akitaya
#    2018/08/21  Ver 1.1  H. Akitaya
#    2018/08/28  Ver 2.0  H. Akitaya; sacrafile separated


import sys,os,re,tempfile, time
import astropy.io.fits as fits
from subprocess import Popen, PIPE
from scrredmisc import *
import sacrafile as sf

if __name__ == "__main__":
    def usage():
        print("Usage: preproc.py object_name filter [exp_time (optional)]")
    if len(sys.argv) < 3:
        usage()
        exit(1)
    
    if len(sys.argv) == 4:
        exptime = float(sys.argv[3])
    else:
        exptime = 5.0
    objname = sys.argv[1]
    band = sys.argv[2]

    sf1 = sf.SacraFile(DT_DARK)
#    print exptime
    sf1.mkDark(band, exptime)
    sf1.mkDark(band, 5.0)
    
    sf2 = sf.SacraFile(DT_FLAT)
   #    band="i"
    exptime_flat = 5.0
    sf2.mkFlat(band, exptime_flat, MOD_MIMG)

    sf3 = sf.SacraFile(DT_OBJ)
    sf3.objDsubFlatten(objname, band, MOD_MIMG)

#    fi = sf.FitsInfo(band=band, datatype=DT_FLAT)
#    lst=sf.getFnList('flat', fi)
#    print(lst)
#    fn_list=sf.getFlatList( band )
#    sf.flatCombine(band, fn_list)
#    liststr=sf.getFnsStr(fn_list)
#    print(liststr)
#    print(sf.getDarkFn(band, 5000.0))
#    print(sf.getFlatFn(band, "img"))
