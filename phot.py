#!/usr/bin/env python3

import os
import sys
import math
import numpy as np

from astropy.coordinates import SkyCoord
import astropy.units as u
from photutils import SkyCircularAperture, CircularAperture, SkyCircularAnnulus, CircularAnnulus, aperture_photometry
from astropy.io import fits
from astropy.units import Quantity
from astropy.wcs import WCS
from astropy.nddata import CCDData

from sacrafits import SacraFits
from sacraccd import SacraCCD
from sacrasextractor import SacraSExtractor

AP_FACTOR = 2.5
ANN_RIN_DIFF = 2.0
ANN_WIDTH = 2.0
MAG0 = 25.0
CCDGAIN = 1.2

class Apphot(object):
    def __init__(self, fn):
        self.fn = fn
        self.sf = SacraFits(fn, updatemode=True)
        self.fwhm = 0.0

    def close(self):
        self.sf.close()
        
    def photometry(self, position, fwhm, ap_factor=AP_FACTOR, ann_rin_diff=ANN_RIN_DIFF, ann_width=ANN_WIDTH, mag0=MAG0, ccdgain=CCDGAIN):
        """
        Aperture photometry.
        """
        self.fwhm = fwhm
        ap_radius = self.fwhm/2.0 * AP_FACTOR
        ap = SkyCircularAperture(position, r=ap_radius*u.arcsec)
        r_in = ap_radius + ann_rin_diff
        r_out = r_in + ann_width
        ann = SkyCircularAnnulus(position, r_in*u.arcsec, r_out*u.arcsec)

        wcs = WCS(self.sf.hdul[0].header)
        ap_pix = ap.to_pixel(wcs)
        ann_pix = ann.to_pixel(wcs)
        apers = [ap_pix, ann_pix]
        data = u.Quantity(self.sf.hdul[0].data, unit=self.sf.hdul[0].header['BUNIT'])
        # phot_table = aperture_photometry(self.sf.hdul[0], apers)
        phot_table = aperture_photometry(data, apers)

        len_tbl = len(phot_table['aperture_sum_1'])
        ccdgain_q = ccdgain * u.electron/u.adu
        phot_table['residual_aperture_sum'] = [0.0] * len_tbl *u.adu
        phot_table['mag'] = [u.Magnitude(1.0 * u.adu)] * len_tbl
        phot_table['mag_err'] = [0.0] * len_tbl *u.mag
    

        # sys.exit()

        if self.sf.has_header('SKYLVCOR'):
            bkg0 = -1.0 * float(self.sf.get_header_value('SKYLVCOR')) * u.adu
        else:
            bkg0 = 0.0
        bkg0_total = bkg0 * ap_pix.area
        if self.sf.has_header('N-CMBIMG'):
            n_cmbimg = int(self.sf.get_header_value('N-CMBIMG'))
        else:
            n_cmbimg = 1

        phot_table
                
        for i in range(len_tbl):
            bkg_mean = phot_table['aperture_sum_1'][i] / ann_pix.area
            bkg_sum = bkg_mean * ap_pix.area
            final_sum = phot_table['aperture_sum_0'][i] - bkg_sum
            phot_table['residual_aperture_sum'][i] = final_sum
        
            # Error estimation
            total_flux_e = final_sum * n_cmbimg * ccdgain_q
            total_sky_e = (bkg_sum + bkg0_total) * n_cmbimg * ccdgain_q
            total_err = math.sqrt(float(total_flux_e/u.electron) + float(total_sky_e/u.electron)) * u.electron / ccdgain_q
            mag = u.Magnitude(final_sum) + u.Magnitude(mag0)
            mag_err = 1.0857 * total_err / final_sum * u.mag
            phot_table['mag'][i] = mag
            phot_table['mag_err'][i] = mag_err
        return phot_table
    

    def show_table(self, phot_table):
        for col in phot_table.colnames:
            phot_table[col].info.format = '%.10g'
        print(phot_table)

    def calc_diffmag(self, phot_table, magzero=None, verbose=False):
        print(magzero)
        len_tbl = len(phot_table['aperture_sum_1'])
        if len_tbl == 1:
            print("Only one object in the table.")
            sys.exit(1)
        result_phot = []
        for i in range(len_tbl):
            mag = phot_table['mag'][i].value
            mag_err = phot_table['mag_err'][i].value
            result_phot.append([mag, mag_err])
            if verbose:
                print(mag, mag_err)

        result_diff = []
        for i in range(1, len_tbl):
            mag_d, mag_d_err = mag_diff(phot_table['mag'][0].value,
                                        phot_table['mag_err'][0].value,
                                        phot_table['mag'][i].value,
                                        phot_table['mag_err'][i].value)
            if magzero is not None:
                if i < len(magzero)+1:
                    mag_d += magzero[i-1]
            if verbose:
                print('Obj-C{}: {:8.3f} {:8.3f}'.format(i, mag_d, mag_d_err))
            result_diff.append([mag_d, mag_d_err])
        return result_phot, result_diff

    def output_diffmag_result(self, phot_table, magzero=None):
        filtern = str(self.sf.get_header_value('FILTER'))
        mjd_ave = float(self.sf.get_header_value('MJD-AVE'))
        exptotal = float(self.sf.get_header_value('EXPTOTAL'))
        n_cmbimg = int(self.sf.get_header_value('N-CMBIMG'))
        skylevel = (-1.0) * float(self.sf.get_header_value('SKYLVCOR'))
        result_phot, result_diff = self.calc_diffmag(phot_table, magzero)
        resultlines = ''
        resultlines = ''.join([resultlines, '# {: >13s} {: >8s} {: >8s} {: >8s} {: >8s} {: >8s} '.format('MJD-AVE', 'EXPTOTAL', 'N_CMBIMG', 'SKYLEVEL', 'FWHM', 'FILTER')])
        obj_num = len(result_phot)
        diff_num = len(result_diff)
        for i in range(0, obj_num):
            resultlines = ''.join([resultlines, '    mag{} mag_err{} '.format(i, i)])        
        for i in range(1, diff_num+1):
            resultlines = ''.join([resultlines, 'mag(Obj-C{}) mag_err(Obj-C{}) '.format(i+1, i+1)])
        resultlines = ''.join([resultlines, '\n'])
        resultlines = ''.join([resultlines, '  {: >13f} {: >8.2f} {: >8d} {: >8.2f} {: >8.1f} {: >8s} '.format(mjd_ave,exptotal, n_cmbimg, skylevel, self.fwhm, filtern)])
        for mag_magerr in result_phot:
            resultlines = ''.join([resultlines, ('{: >8.4f} {: >8.4f} '.format(mag_magerr[0], mag_magerr[1]))])
        for mag_magerr in result_diff:
            resultlines = ''.join([resultlines, ('{: >11.4f} {: >15.4f} '.format(mag_magerr[0], mag_magerr[1]))])
        resultlines = ''.join([resultlines, '\n'])
        print(resultlines)
        return resultlines
        
def mag_diff(mag_obj, mag_err_obj, mag_ref, mag_err_ref):
    mag_d = mag_obj - mag_ref
    mag_d_err = math.sqrt(mag_err_obj*mag_err_obj + mag_err_ref*mag_err_ref)
    return mag_d, mag_d_err
        

if __name__ == '__main__':
    astmet_param_fn = '/home/works/akitaya/work7/saitama/obs/SN2018zd/stackedimg/ngc2146_astmt.sex'
    catalog_fn = 'ngc2146.cat'
    fn = sys.argv[1]
    out_fn = sys.argv[2]
    ra = list(map(float, sys.argv[3].split()))
    dec = list(map(float, sys.argv[4].split()))
    magzero = list(map(float, sys.argv[5].split()))
    # print(ra, dec)
    position = SkyCoord(ra=ra * u.deg, dec=dec * u.deg)
    
    # Measure fwhm
    print('Measure fwhm')
    sf = SacraFits(fn)
    skylevel = -1.0 * float(sf.get_header_value('SKYLVCOR'))
    print(skylevel)
    sf.close()
    data = SacraCCD(fn)
    data.read()
    header_old = data.ccddata.to_hdu()[0].header
    new = CCDData(np.nan_to_num(np.asarray(data.ccddata.data)) + skylevel, unit='adu')
    data.overwrite = True
    data.ccddata = new
    newfn = data.get_subext_fn('_sky')
    if os.path.isfile(newfn):
        os.remove(newfn)
    data.ccddata.mask = None
    hdul = data.ccddata.to_hdu(None)
    hdul[0].header = header_old
    hdul.writeto(newfn)

    ssext = SacraSExtractor(catalog_fn)
    ssext.apply_sextractor(newfn, param_fn=astmet_param_fn)
    vals = ssext.calc_fwhm_median_from_img()
    fwhm = vals[0]
    
    app = Apphot(fn)
    phot_table = app.photometry(position, fwhm)
    # app.show_table(phot_table)
    # app.calc_diffmag(phot_table)
    resultlines = app.output_diffmag_result(phot_table, magzero=magzero)
    with open(out_fn, 'a') as f:
        f.write(resultlines)
    app.close()
