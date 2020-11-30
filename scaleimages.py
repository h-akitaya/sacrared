#!/usr/bin/env python3

import os
import sys
import datetime

import numpy as np
from astropy.table import Table
from astropy.io import fits
from ccdproc.utils.sample_directory import sample_directory_with_files
from ccdproc import ImageFileCollection

import apphot
from apphot import Aperture
from apphot import AperturePhotometry
from astropy.coordinates import SkyCoord

from sacrafits import SacraFits
from sacrafile_woiraf import ImageList, SacraFile, SacraFits
import scrredmisc as scrm
from sacraccd import SacraCCD

SKY_X1 = 501
SKY_X2 = 601
SKY_Y1 = 501
SKY_Y2 = 601

class ScaleImages(object):
    def __init__(self):
        self.phottable = Table(names=('filename', 'count'), dtype=('S', 'f'))
        # Photometry table: filename(str) count(float).

    def get_apphot_table(self, aperture, fnlist):
        """
        Do photometry and make filename-count table.
        @type aperture: Aperture
        """
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
            

    def select_bright_images(self, lsig=2.5):
        """
        Filter bright images (count > median - sigma * lsig),
        and return filtered table (filename, scale).
        @param lsig: Lower limit scale for sigma.
        @return: Filtered file and scale dictionary.
        """
        selected_files = {}  # 'filename': count
        counts = np.array(self.phottable['count'])
        count_median = np.median(counts)
        count_stddev = np.std(counts)
        for line in self.phottable:
            if line['count'] < (count_median - lsig * count_stddev):
                continue
            scale = 1.0 / (line['count'] / count_median)
            print((line['filename'], scale))
            selected_files[line['filename']] = scale
        print('{0:3d} files selected in {1:3d} files.'.format(len(selected_files),
                                                              len(self.phottable)))
        return selected_files

    
    def scale_images(self, selected_files):
        fns = selected_files.keys()
        dir = sample_directory_with_files()
        ic1 = ImageFileCollection(filenames=fns)
        for hdu, fname in ic1.hdus(return_fname=True, save_with_name='_scl'):
            try:
                skylevel_correct = hdu.header['SKYLVCOR']
            except KeyError:
                ccddata_sky = hdu.data[SKY_X1:SKY_X2, SKY_Y1:SKY_Y2]
                skylevel_correct = (-1.0) * np.median(ccddata_sky)
            scale = selected_files[fname]
            hdu.data += skylevel_correct
            hdu.data *= scale
            hdu.header['HISTORY'] = '----'
            hdu.header['HISTORY'] = 'scaleimages.py: {}'.format(datetime.datetime.utcnow().strftime('%c'))
            hdu.header['HISTORY'] = 'Sky correction: {0:.5f}'.format(skylevel_correct)
            hdu.header['HISTORY'] = 'Scaling: {0:.5f}'.format(scale)
        newfns = []
        for fn in selected_files.keys():
            strs = os.path.splitext(fn)
            newfns.append('{}_scl{}'.format(strs[0], strs[1]))
        return newfns

    
    def combine_selected_images(self, lst, fn_out, reject=True, wcs_rp=True):
        ''' Combine selected images.
        '''
        mjd_ave = 0.0
        exptime_total = 0.0
        for fn in lst:
            sf = SacraFits(fn, updatemode=False)
            mjd_ave += sf.get_header_value('MJD-OBS') / len(lst)
            exptime_total += sf.get_header_value('EXPTIME')
            sf.close()
        sf = SacraFile()
        sf.img_combine(lst, fn_out, reject=reject, wcs_rp=wcs_rp,
                    lsigma=2.5, hsigma=2.5, offsets='none', zeroopt='none')
        sf.add_fits_header(fn_out, 'MJD-AVE', mjd_ave, 'MJD Avarage for combining.')
        sf.add_fits_header(fn_out, 'EXPTOTAL', exptime_total, 'Total exposure time for combining.')
        sf.add_fits_header(fn_out, 'N-CMBIMG', len(lst), 'Number of combined images.')
        sf.add_fits_histories(
            fn_out,
            '# Combining: {}\n{}'.format(
                datetime.datetime.utcnow().strftime('%c'),
                ','.join(lst)
            )
        )
        print(mjd_ave, exptime_total, len(lst), fn_out)
        
def scale_images_and_combine(fnpattern, exptime, filtername, fn_out='tmp.fits'):
    loc = '.'
    # fnpattern = '*_wcs_cr.fits'
    # exptime = 30.0
    # filtername = 'z'
    objname = 'NGC2146'

    apsize = 5.0
    r_in = apsize + 3.0
    r_out = r_in + 4.0
    radecstr = '06:17:31.5 +78:25:28.1'
    skycoord = Aperture.get_skycoord_from_radecstr(radecstr)

    ap = Aperture(apsize, r_in, r_out, skycoord)

    imglst = ImageList()
    fnlist = imglst.get_fnlist(loc, fnpattern, objname=objname, exptime=exptime,
    filtername=filtername)
    si = ScaleImages()
    si.get_apphot_table(ap, fnlist)
    selected_table = si.select_bright_images()
    newfns = si.scale_images(selected_table)

    si.phottable.pprint_all()
    # print(si.phottable.columns)
    # print(si.phottable['count'])
    # print(type(si.phottable['count']))
    counts = np.array(si.phottable['count'])
    #print(counts)
    #print(type(counts))
    # print(newfns)

    if len(newfns) == 0:
        print('No files selected.')
        sys.exit(1)

    sf = SacraFile()
    si.combine_selected_images(newfns, fn_out, reject=True, wcs_rp=True)

def test2():
    loc = '.'
    fnpattern = '*_wcs_cr_scl.fits'
    exptime = 30.0
    filtername = 'z'
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
    si = ScaleImages()
    si.get_apphot_table(ap, fnlist)
    print(si.phottable)


if __name__ == '__main__':
    fnpattern = sys.argv[1]
    exptime = float(sys.argv[2])
    filtername = sys.argv[3]
    # objname = sys.argv[4]
    # selected_table = test(fnpattern, exptime, filtername)
    out_fn = '{}_{}.fits'.format(os.path.split(os.path.abspath('.'))[1], filtername)
    selected_table = scale_images_and_combine(fnpattern, exptime, filtername, fn_out=out_fn)
    sf = SacraFits(out_fn)
    objname = sf.get_header_value('OBJNAME')
    object_name = sf.get_header_value('OBJECT')
    object_name_comment = sf.get_header_comment('OBJECT')
    if objname != object_name:
        sf.set_fits_header('OBJECT', objname, object_name_comment)
    
