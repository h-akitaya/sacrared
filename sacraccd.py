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
            sys.exit(1)

    def add_scalar(self, value):
        unit = self.ccddata.unit
        self.ccddata.data = CCDData(np.asarray(self.ccddata.data)
                                    + value, unit=unit)

    def sub_scalar(self, value):
        unit = self.ccddata.unit
        self.ccddata.data = CCDData(np.asarray(self.ccddata.data)
                                    - value, unit=unit)
        
    def multiply_scalar(self, value):
        unit = self.ccddata.unit
        self.ccddata.data = CCDData(np.asarray(self.ccddata.data)
                                    * value, unit=unit)        

    def divide_scalar(self, value):
        unit = self.ccddata.unit
        self.ccddata.data = CCDData(np.asarray(self.ccddata.data)
                                    / value, unit=unit)        
        
    def write(self, fn):
        """
        Write CCDData to FITS file.
        """
        self.ccddata.mask = None
        print(type(self.ccddata))
        sys.exit(1)
        newscrf = SacraFits(fn, hdul = self.ccddata.to_hdu())
        newscrf.hdul[0].header = self.ccddata.to_hdu()[0].header
        if os.path.exists(fn):
            if not self.overwrite:
                sys.stderr.write('File %s exists. Abort.\n' % (fn))
                sys.exit(0)
            else:
                try:
                    os.remove(fn)
                    print('File %s removed.' % (fn))
                except:
                    sys.stderr.write('File %s remove error.\n' % (fn))
                    sys.exit(1)
        #history_strs = [datetime.utcnow().strftime('# %Y-%m-%d %H:%M:%S UTC'),
        #                'sacraccd cosmicray rejection (lacosmic)',
        #                '%s: %i pixels rejected.' \
        #                % (self.fn, rejected_pixel)]
        #for history_str in history_strs:
        #    if self.verbose:
        #        print(history_str)
        #    newscrf.add_history(history_sr)
        newscrf.writeto()

    def crrej_write(self, sigclip=5, gain=1.0, readnoise=15.0,
                    psffwhm=5.0, subext='_cr'):
        """
        Cosmic-ray rejection using lacosmic, and write new file.
        """
        crrej_ccd = cosmicray_lacosmic(self.ccddata, sigclip=sigclip,
                                       readnoise=readnoise, gain=gain, niter=8,
                                       psffwhm=psffwhm, psfsize=psffwhm*2.5).multiply(1.0/gain*SacraCCD.UNIT_CFACTOR)
        rejected_pixel = np.count_nonzero(crrej_ccd.mask)
        
        crrej_ccd.mask = None
        newfn = self.get_subext_fn(subext=subext)
        newscrf = SacraFits(newfn, hdul=crrej_ccd.to_hdu())
        newscrf.hdul[0].header = self.ccddata.to_hdu()[0].header
        if os.path.exists(newfn):
            if not self.overwrite:
                sys.stderr.write('File %s exists. Abort.\n' % (newfn))
                sys.exit(1)
            else:
                try:
                    os.remove(newfn)
                except:
                    sys.stderr.write('File %s remove error.\n' % (newfn))
                    sys.exit(1)
                print('File %s removed.' % (newfn))
        
        history_strs = [datetime.utcnow().strftime('# %Y-%m-%d %H:%M:%S UTC'),
                        'sacraccd cosmicray rejection (lacosmic)',
                        '%s: %i pixels rejected.' \
                        % (self.fn, rejected_pixel)]
        for history_str in history_strs:
            if self.verbose:
                print(history_str)
            newscrf.add_history(history_str)
        print('Write file {}'.format(newfn))
        newscrf.writeto()

    def skylevel_correct(self):
        ccddata_sky = ccddata[SKY_X1, SKY_X2: SKY_Y1, SKY_Y2]
        return np.median(ccddata_sky) * (-1.0)

    def get_subext_fn(self, subext='_subext'):
        """
        Return filename with sub-extention.
        """
        return scrm.make_subextfn(self.fn, subext)


"""
Test code for SacraCCD.
"""

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    sccd = SacraCCD(fn=sys.argv[1], overwrite=True)
    sccd.read()
    sccd.crrej_write()
