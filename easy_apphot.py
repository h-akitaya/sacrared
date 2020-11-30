#!/usr/bin/env python3

import os
import sys

import numpy as np

from sacrasextractor import SacraSExtractor
from sacraccd import SacraCCD
from sacrafits import SacraFits
from astropy.nddata import CCDData

class EasyApphot(object):
    def __init__(self, fn):
        self.fn = fn
        self.scrccd = None
        pass

    def read_ccddata(self):
        self.ccddata = SacraCCD(self.fn)
        self.ccddata.read()

    def get_skylevel(self):
        sf = SacraFits(self.fn, updatemode=False)
        if not sf.has_header('SKYLVCOR'):
            sys.stderr.write('No SKYLVCOR. Abort.\n')
            sys.exit(1)
        skylevel = -1.0 * float(sf.get_header_value('SKYLVCOR'))
        sf.close()
        return skylevel
    
    def add_skylevel(self):
        skylevel = self.get_skylevel()
        scrccd = SacraCCD(self.fn)
        newfn = scrccd.get_subext_fn('_sky')
        scrccd.read()
        hdr = scrccd.ccddata.to_hdu()[0].header
        unit = scrccd.ccddata.unit
        new_ccddata = CCDData(np.nan_to_num(np.asarray(scrccd.ccddata.data)) + skylevel, unit=unit)
        scrccd.ccddata = new_ccddata
        scrccd.ccddata.mask = None
        hdul = scrccd.ccddata.to_hdu(None)
        sf = SacraFits(newfn, hdul=hdul, updatemode=True)
        sf.hdul[0].header = hdr
        print('New file {} (Sky level {} appended.)'.format(newfn, skylevel))
        sf.writeto()
        sf.close()
        return newfn

if __name__ == '__main__':
    cat_fn = 'ngc2146.cat'
    fn = sys.argv[1]
    ea = EasyApphot(fn)
    newfn = ea.add_skylevel()
    
    # SExtractor
    param_fn = sys.argv[2]
    ss = SacraSExtractor()
    ss.apply_sextractor(newfn, param_fn=param_fn)
    fwhm, fwhm_std = ss.calc_fwhm_median_from_img(fn=cat_fn)

    print(fwhm, fwhm_std)
    
