#! /usr/bin/env python
#
#   testtool1
#      testtool1.py
#
#     Ver 1.0 2018/05/08   H. Akitaya
#

import sys,os,re,tempfile, time, shutil
import astropy.io.fits as fits
from pyraf import iraf
from pyds9 import *
from subprocess import Popen, PIPE
from scrredmisc import *
from sacrafits import *
from preproc import *

TestNum = 1

def main():
    if TestNum == 0:
        imstatTest(sys.argv[1])
    elif TestNum == 1:
        imcentroidTest(sys.argv[1], sys.argv[2])
        
    
def imstatTest(fn_in):
    sf=SacraFile()
    print(sf.getMedian(fn_in))

def imcentroidTest(fn_in, fn_coord):
    sf=SacraFile()
    result = sf.getCentroid2(fn_in, fn_coord)
    print analyseImcentroidShift(result, mode='median')

if __name__ == "__main__":
    main()
