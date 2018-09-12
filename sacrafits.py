#!/usr/bin/env python
#
# SaCRA MuSaSHI Fits Header Manager
#
#     Ver 1.0  2018/03/03  H. Akitaya
#     Ver 1.1  2018/03/21  H. Akitaya
#     Ver 1.2  2018/05/24  H. Akitaya
#     Ver 1.3  2018/08/01  H. Akitaya
#     Ver 1.4  2018/08/08  H. Akitaya
#     Ver 1.5  2018/09/07  H. Akitaya; updatemode appended

import sys, math
from astropy.time import Time
from astropy.io import fits

class SacraFits( object ):
    def __init__( self, fn, updatemode=True ):
        self.setFilename( fn )
        if updatemode==False:
            self.roopen()
        else:
            self.open()
        
        self.overwrite = False


    def setFilename( self, fn ):
        self.fn = fn
        
    def open( self ):
#        fits_img_fn = fits.util.get_testdata_filepath(self.fn)
        try:
            self.hdul = fits.open( self.fn, mode='update', checksum=True )
        except OSError:
            sys.stderr.write("Not correct fits file.\n")
            exit()
        self.hdr=self.hdul[0].header

    def roopen( self ):
#        fits_img_fn = fits.util.get_testdata_filepath(self.fn)
        try:
            self.hdul = fits.open( self.fn, checksum=True )
        except OSError:
            sys.stderr.write("Not correct fits file.\n")
            exit()
        self.hdr=self.hdul[0].header


    def allowOverwrite(self):
        self.overwrite = True

    def denyOverwrite(self):
        self.overwrite = False
        
    def hasHeader(self, header):
        try:
            dummy = self.hdr[header]
            return True
        except KeyError:
            return False
        return False

    def writeOK(self, header):
        if self.hasHeader(header):
            if self.overwrite == False:
                return False
        else:
            return True
    
    def close(self):
        self.hdul.close()
    def getHeaderValue(self, header):
        return self.hdr[header]
    def setHeaderValue(self, header, value, comment):
        self.hdr[header] = (value, comment)
    def addHistory(self, history_str):
        self.hdr['history'] = history_str
    def showAllHeaders(self):
        print(repr(self.hdr))
        
    def setMJDfromOBSTIME(self):
        if not self.writeOK("MJD"):
            return 1
        time_str = self.getHeaderValue("DATE-OBS")
        t = Time(time_str, format='isot', scale='utc')
        self.setHeaderValue("MJD", t.mjd, "MJD of DATE-OBS")
        
    def modifyExptimeToSec(self):
        if not self.hasHeader("EXPTMSEC"):
            expt_ms = self.getHeaderValue("EXPTIME")
            expt_s = float(expt_ms)/1000.0
            self.setHeaderValue("EXPTMSEC", expt_ms, "Exposure Time [msec]")
            self.setHeaderValue("EXPTIME", expt_s, "Exposure Time [sec]")
        
    def setOBJECTfromOBJNAME(self):
        if not self.writeOK("OBJECT"):
            return 1
        self.setHeaderValue("OBJECT", self.getHeaderValue("OBJNAME"), "Object name (same as OBJNAME)")

    def setAIRMASSfromZD(self):
        if not self.hasHeader("ZD"):
            return 1
        if not self.writeOK("AIRMASS"):
            return 1
        airmass = 1.0/math.cos(math.pi/180.0*float(self.getHeaderValue("ZD")))
        airmass = round(airmass, 6)
        self.setHeaderValue("AIRMASS", airmass, "Airmass")
        
    def updateFitsFile(self):
        self.hdul.flush()

    def setDummyHeaderForHonirred(self):
        self.setHeaderValue("WH_IRAF2", "NA", "Dummy for honirred" )
        if not self.writeOK("HA"):
            return 1
        self.setHeaderValue("HA", 0.0, "Dummy for honirred" )
        if not self.writeOK("HA-DEG"):
            return 1
        self.setHeaderValue("HA-DEG", 0.0, "Dummy for honirred" )


    def chkModified(self):
        if self.hdr.countget('SCRFTSMD') != 0:
            return True
        else:
            return False

    def addHeaderModifiedHistory(self):
        self.setHeaderValue("SCRFTSMD", "True", "SaCRA FITS Modified History (True=yes")

# main routine
    
if __name__ == '__main__':
    main()
