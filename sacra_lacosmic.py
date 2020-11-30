#!/usr/bin/env python3
"""
    lacosmic for SaCRA images.
        Ver 1.0.0  2020/04/11 H. Akitaya
        Ver 1.1.0  2020/10/25 H. Akitaya (optparse)
"""

__author__ = 'Akitaya, H. (akitaya@hiroshima-u.ac.jp)'
__version__ = '1.1.0'
__date__ = '2020/10/25'

import sys
import glob
from optparse import OptionParser

from sacraccd import SacraCCD


def usage():
    print('Usage: %s (= fnpattern; (e.g) "*/*_wcs.fits")' % sys.argv[0])


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-g", "--gain", action="store", type="float",
                      dest="gain", default=1.0, help="gain of a detector")
    parser.add_option("-r", "--ronoise", action="store", type="float",
                      dest="ronoise", default=1.0,
                      help="readout noise")
    parser.add_option("-p", "--psf-fwhm", action="store", type="float",
                      dest="psffwhm", default=10.0,
                      help="PSF FWHM")
    parser.add_option("-s", "--sigclip", action="store", type="float",
                      dest="sigclip", default=3.0,
                      help="Clipping sigma")
    (options, args) = parser.parse_args()

    print(options.gain, options.ronoise, options.psffwhm)

    if len(args) < 2:
        exit(1)

    print(type(args))
    print(args)

    #files = glob.glob(args)
    files = args

    for fn in files:
        sccd = SacraCCD(fn=fn, overwrite=True)
        sccd.read()
        sccd.crrej_write(gain=options.gain, readnoise=options.ronoise,
                         psffwhm=options.psffwhm, sigclip=options.sigclip)
