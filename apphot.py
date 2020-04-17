#!/usr/bin/env python3

import sys
import numpy
from astropy.io import fits
from photutils import DAOStarFinder,  CircularAperture
from photutils.aperture import SkyCircularAperture, aperture_photometry, SkyCircularAnnulus
from astropy.stats import mad_std, median_absolute_deviation
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u

class Aperture(object):
    def __init__(self, apsize, r_in, r_out, skycoord):
        self.apsize = apsize * u.arcsec
        self.r_in = r_in * u.arcsec
        self.r_out = r_out * u.arcsec
        self.skycoord = skycoord

    @staticmethod
    def get_skycoord_from_radecstr(radecstr):
        return SkyCoord(radecstr, unit=(u.hourangle, u.deg))

class AperturePhotometry(object):
    def __init__(self, hdu, skycoord, apsize, r_in, r_out):
        """
        Define aperture photometry parameters.
        """
        self.hdu = hdu  # fits hdu
        self.skycoord = skycoord  # SkyCoord of the object
        self.apsize = apsize  # aperture size (arcsec)
        self.r_in = r_in  # inner radius of the sky region
        self.r_out = r_out  # outer radius of the sky region
        self.img = self.hdu[0].data  # image data
        self.wcs = WCS(self.hdu[0].header)  # wcs definition

    def subtract_global_bg(self):
        """
        Subtract median value from the image. 
        Return the median value.
        """
        bg_median = numpy.median(self.img)
        self.img -= bg_median
        return bg_median

    def apphot(self):
        """
        Aperture photometry.
        """
        aperture = SkyCircularAperture(self.skycoord,
                                       r=self.apsize)
        annulus_aperture = SkyCircularAnnulus(self.skycoord,
                                              r_in=self.r_in,
                                              r_out=self.r_out)
        phot_table = aperture_photometry(self.img,
                                         [aperture, annulus_aperture],
                                         wcs=self.wcs)
        bkg_mean = phot_table['aperture_sum_1'] \
            / annulus_aperture.to_pixel(self.wcs).area
        bkg_sum = bkg_mean * aperture.to_pixel(self.wcs).area
        final_sum = phot_table['aperture_sum_0'] - bkg_sum
        phot_table['residual_aperture_sum'] = final_sum
        phot_table['residual_aperture_sum'].info.format = '%.8g'
        count = float(phot_table['residual_aperture_sum'][0])
        return count
        
if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print('%s filename' % (sys.argv[0]))
        exit()

    fn = sys.argv[1]
    hdu = fits.open(fn)

    radec = '06:17:31.5 +78:25:28.1'
    apsize = 2.5 * 2.5 * u.arcsec  # 0.73 arcsec/pix
    r_in = apsize + 2.0 * u.arcsec
    r_out = apsize + 5.0 * u.arcsec

    skycoord = SkyCoord(radec, unit=(u.hourangle, u.deg))

    ap = AperturePhotometry(hdu, skycoord, apsize, r_in, r_out)
    #
    count = ap.apphot()
    hdu.close()
