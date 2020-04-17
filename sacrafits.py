#!/usr/bin/env python3
#
# SaCRA MuSaSHI Fits Header Manager
#
#     Ver 1.0  2018/03/03  H. Akitaya
#     Ver 1.1  2018/03/21  H. Akitaya
#     Ver 1.2  2018/05/24  H. Akitaya
#     Ver 1.3  2018/08/01  H. Akitaya
#     Ver 1.4  2018/08/08  H. Akitaya
#     Ver 1.5  2018/09/07  H. Akitaya; updatemode appended
#     Ver 1.6  2018/09/18  H. Akitaya; checksum removed
#     Ver 1.7  2018/11/09  H. Akitaya; declare to use python3
# 

import sys, math, re
from astropy.time import Time
from astropy.io import fits

class SacraFits(object):
    def __init__(self, fn, hdul=None, updatemode=True):
        self.fn = fn
        self.hdul = hdul  # HDUList
        if hdul is None:
            if updatemode==False:
                self.roopen()
            else:
                self.open()
        else:
            self.set_hdr()
        self.overwrite = False  # overwrite mode

    def hdul_check(self):
        if isinstance(self.hdul, astropy.io.fits.hdu.hdulist.HDUList):
            return True
        else:
            sys.stderr.write('Not correct HDUList.\n')
            exit(1)

    def set_filename(self, fn):
        self.fn = fn
        
    def open(self):
        try:
            self.hdul = fits.open(self.fn, mode='update', checksum=False )
        except OSError:
            sys.stderr.write("Not correct fits file.\n")
            exit()
        self.hdr=self.hdul[0].header

    def set_hdr(self):
        """
        Set HDUList from argument.
        """
        try:
            self.hdr = self.hdul[0].header
        except:
            sys.stderr.write('Not correct HDUList.\n')
            exit(1)

    def roopen(self):
#        fits_img_fn = fits.util.get_testdata_filepath(self.fn)
        try:
            self.hdul = fits.open(self.fn, checksum=True)
        except OSError:
            sys.stderr.write("Not correct fits file.\n")
            exit()
        self.hdr=self.hdul[0].header

    def has_history_str(self, hstrystr):
        for hstry_line in self.hdr['history']:
            if hstrystr in hstry_line:
                return True
        return False

    def allow_overwrite(self):
        self.overwrite = True

    def deny_overwrite(self):
        self.overwrite = False
        
    def has_header(self, header):
        try:
            dummy = self.hdr[header]
            return True
        except KeyError:
            return False
        return False

    def writeOK(self, header):
        if self.has_header(header):
            if self.overwrite == False:
                return False
        else:
            return True
    
    def close(self):
        self.hdul.close()
        
    def get_header_value(self, header):
        return self.hdr[header]
    
    def set_header_value(self, header, value, comment):
        self.hdr[header] = (value, comment)
        
    def add_history(self, history_str):
        self.hdr['history'] = history_str
        
    def show_all_headers(self):
        print(repr(self.hdr))
        
    def set_mjd_from_obstime(self):
        if not self.writeOK("MJD"):
            return 1
        time_str = self.get_header_value("DATE-OBS")
        t = Time(time_str, format='isot', scale='utc')
        self.set_header_value("MJD", t.mjd, "MJD of DATE-OBS")
        
    def exptime_to_sec(self):
        if not self.has_header("EXPTMSEC"):
            expt_ms = self.get_header_value("EXPTIME")
            expt_s = float(expt_ms)/1000.0
            self.set_header_value("EXPTMSEC", expt_ms, "Exposure Time [msec]")
            self.set_header_value("EXPTIME", expt_s, "Exposure Time [sec]")
        
    def set_object_from_objname(self):
        if not self.writeOK("OBJECT"):
            return 1
        self.set_header_value("OBJECT", self.get_header_value("OBJNAME"), "Object name (same as OBJNAME)")

    def set_airmass_from_zd(self):
        if not self.has_header("ZD"):
            return 1
        if not self.writeOK("AIRMASS"):
            return 1
        airmass = 1.0/math.cos(math.pi/180.0*float(self.get_header_value("ZD")))
        airmass = round(airmass, 6)
        self.set_header_value("AIRMASS", airmass, "Airmass")
        
    def update_fits_file(self):
        self.hdul.flush()

    def dummy_header_honirred(self):
        self.set_header_value("WH_IRAF2", "NA", "Dummy for honirred" )
        if not self.writeOK("HA"):
            return 1
        self.set_header_value("HA", 0.0, "Dummy for honirred" )
        if not self.writeOK("HA-DEG"):
            return 1
        self.set_header_value("HA-DEG", 0.0, "Dummy for honirred" )


    def chk_modified(self):
        if self.hdr.countget('SCRFTSMD') != 0:
            return True
        else:
            return False

    def add_header_modified_history(self):
        self.set_header_value("SCRFTSMD", "True", "SaCRA FITS Modified History (True=yes")

    def writeto(self, fn):
        self.hdul.writeto(fn)

# main routine
    
if __name__ == '__main__':
    main()
