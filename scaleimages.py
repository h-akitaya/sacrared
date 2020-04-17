#!/usr/bin/env python3

import numpy as np
from astropy.table import Table
from astropy.io import fits
from ccdproc import ImageFileCollection
from ccdproc.utils.sample_directory import sample_directory_with_files

import apphot
from apphot import Aperture
from apphot import AperturePhotometry
from astropy.coordinates import SkyCoord

class ApPhot(object):
    def __init__(self):
        self.phottable = Table(names=('filename', 'count'), dtype=('S', 'f'))
        pass
    
    def get_apphot_table(self, aperture, fnlist):
        for fn in fnlist:
            hdu = fits.open(fn)
            aph = apphot.AperturePhotometry(hdu,
                                           aperture.skycoord,
                                           aperture.apsize,
                                           aperture.r_in,
                                           aperture.r_out)
            count = aph.apphot()
            self.phottable.add_row((fn, count))
            hdu.close()

    def select_brightimages(self):
        
        pass

class ImageList(object):
    def __init__(self):
        self.fnlist = []
        pass

    def get_fnlist(self, loc, fnpattern, objname,
                   exptime, filtername):
        """
        Get FITS file list with objname, exptime, and 
        filtername.
        """
        keys = ['exptime', 'objname', 'filter']
        ic_all = ImageFileCollection(location=loc,
                                     keywords=keys,
                                     glob_include=fnpattern,
                                     glob_exclude=None)
        return ic_all.files_filtered(filter=filtername,
                                       objname=objname,
                                       exptime=exptime)

if __name__ == '__main__':
    loc = '.'
    fnpattern = '*_wcs.fits'
    exptime = 60.0
    filtername = 'r'
    objname = 'NGC2146'
    
    apsize = 5.0
    r_in = apsize + 3.0
    r_out = r_in + 4.0
    radecstr = '06:17:31.5 +78:25:28.1'
    skycoord = Aperture.get_skycoord_from_radecstr(radecstr)
    
    ap = Aperture(apsize, r_in, r_out, skycoord)

    imglst = ImageList()
    fnlist = imglst.get_fnlist(loc, fnpattern, objname, exptime,
                      filtername)
    aph = ApPhot()
    aph.get_apphot_table(ap, fnlist)
    print(aph.phottable)
    print(aph.phottable.columns)
    print(aph.phottable['count'])
    print(type(aph.phottable['count']))
    counts = np.array(aph.phottable['count'])
    print(counts)
    print(type(counts))
