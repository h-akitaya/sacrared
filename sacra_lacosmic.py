#!/usr/bin/env python3
"""
    lacosmic for SaCRA images.
"""

__author__ = 'Akitaya, H. (akitaya@hiroshima-u.ac.jp)'
__version__ = '1.0.0'
__date__ = '2020/04/11'

import sys
import glob

from sacraccd import SacraCCD

def usage():
    print('Usage: %s "(fnpattern)"' % sys.argv[0])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit(1)

    files = glob.glob(sys.argv[1])
        
    for fn in files:
        sccd = SacraCCD(fn=fn, overwrite=True)
        sccd.read()
        sccd.crrej_write()
