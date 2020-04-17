#!/usr/bin/env python3
#
#  check image count
#
#
#       Ver 1.0  2018/11/27 H. Akitaya
#

import sys,os
import argparse

from scrredmisc import *
import sacrafits as sfts
import sacrafile as sf

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Examine count of image', 
                                     prog='checkimgcount.py')
    parser.add_argument('filename', action='store', nargs=None, const=None,
                        default=None, type=str, choices=None, 
                        help='Image file name to be examined.', metavar=None)
    args = parser.parse_args()
    fn = args.filename
    sfl = sf.SacraFile()
    midpt = sfl.get_median(fn)
    print("Examining file: %s" % (fn))
    print("Median (ADU): %10.3f" % (midpt))
    

        

