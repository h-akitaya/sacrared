#!/usr/bin/env python3

__author__ = 'H. Akitaya'
__version__ = '1.00'

import sys
import os
from datetime import datetime 

from astropy.nddata import CCDData
from astropy import units as u
from ccdproc import cosmicray_lacosmic
import numpy as np

import scrredmisc as scrm
from sacrafits import SacraFits

class SacraCCD(object):
    UNIT_GAIN = u.electron / u.adu  # Unit of gain (e-/ADU).
    UNIT_CFACTOR = u.adu / u.electron  # Unit of conversion factor (ADU/e-)
    def __init__(self, fn=None, ccddata=None, verbose=True, overwrite=False):
        self.fn = fn
        self.ccddata = ccddata
        self.verbose = verbose
        self.overwrite = overwrite

    def read(self, unit='adu'):
        """
        Read CCDData from FITS file.
        """
        try:
            self.ccddata = CCDData.read(self.fn, unit=unit)
        except:
            sys.stderr.write('File %s read error.\n' % self.fn)
            exit(1)

    def write(self, fn):
        """
        Write CCDData to FITS file.
        """
        try:
            self.ccddata.write(fn)
        except:
            sys.stderr.write('File %s write error.\n' % fn)
            exit(1)
        if self.verbose:
            print('Output: %s' % (fn))

        return crrej_ccd  # CCDData (w/o mask)

    def crrej_write(self, sigclip=5, gain=1.0, readnoise=15.0,
                    psffwhm=5.0, subext='_cr'):
        """
        Cosmic-ray rejection using lacosmic, and write new file.
        """
        crrej_ccd = cosmicray_lacosmic(self.ccddata, sigclip=sigclip,
                                       readnoise=readnoise, psffwhm=psffwhm).multiply(1.0/gain*SacraCCD.UNIT_CFACTOR)
        rejected_pixel = np.count_nonzero(crrej_ccd.mask)
        
        crrej_ccd.mask = None
        newfn = self.get_subext_fn(subext=subext)
        newscrf = SacraFits(newfn, hdul=crrej_ccd.to_hdu())
        if os.path.exists(newfn):
            if not self.overwrite:
                sys.stderr.write('File %s exists. Abort.\n' % (newfn))
                exit(1)
            else:
                try:
                    os.remove(newfn)
                except:
                    sys.stderr.write('File %s remove error.\n' % (newfn))
                    exit(1)
                print('File %s removed.' % (newfn))
        
        history_strs = [datetime.utcnow().strftime('# %Y-%m-%d %H:%M:%S UTC'),
                        'sacraccd cosmicray rejection (lacosmic)',
                        '%s: %i pixels rejected.' \
                        % (self.fn, rejected_pixel)]
        for history_str in history_strs:
            if self.verbose:
                print(history_str)
            newscrf.add_history(history_str)
        newscrf.writeto(newfn)

    def get_subext_fn(self, subext='_cr'):
        """
        Return filename with sub-extention.
        """
        return scrm.make_subextfn(self.fn, subext)

"""
Test code for SacraCCD.
"""

if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit(1)
    sccd = SacraCCD(fn=sys.argv[1], overwrite=True)
    sccd.read()
    sccd.crrej_write()
