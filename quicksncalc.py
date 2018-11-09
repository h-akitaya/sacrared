#!/usr/bin/env python
#
#   MuSaSHI SN ratio calculator
#        Ver 1.0   2018/09/14   H. Akitaya
#
#

import sys, io, math

RONA_MB1 = 19.7
RONA_MB2 = 12.0
RONA_DD1 = 10.6
RONA_DD2 = 11.65

GAIN_MB1 = 0.925
GAIN_MB2 = 1.344
GAIN_DD1 = 1.912
GAIN_DD2 = 1.171

class AstroPrecision(object):
    def __init__(self):
        self.totalsignal = 0.0
        self.signalpersec = 0.0
        self.skyperpix = 0.0
        self.skyperpixsec = 0.0
        self.gain = 1.0
        self.ronoiseadu = 0.0
        self.apfwhm = 0.0
        self.nap = 0.0
        self.apfactor = 0.0

    def usage(self):
        print('Usage: %s (detector) (fwhm) (aperturefactor) (FLUX) (SKY) (exptime)' % (sys.argv[0]))

    def calcSignalPerExpt(self, expt):
        return self.signalpersec * expt * self.gain
        
    def calcNoisePerExpt(self, expt):
        return math.sqrt(self.nap
                               *self.ronoiseadu*self.gain
                               *self.ronoiseadu*self.gain
                               +self.nap
                               *self.gain*self.skyperpixsec*expt)
    def calcSnRatioPerExpt(self, expt):
        snratio = self.calcSignalPerExpt(expt) / self.calcNoisePerExpt(expt)
        return snratio

    def setSignal(self, totalsignal, expt):
        self.totalsignal = totalsignal
        self.signalpersec = totalsignal / expt

    def setSkyPerPix(self, skyperpix, expt):
        self.skyperpix = skyperpix
        self.skyperpixsec = skyperpix / expt

    def setGain(self, gain):
        self.gain = gain
        
    def setRonoiseadu(self, ronoiseadu):
        self.ronoiseadu = ronoiseadu

    def setApfwhm(self, apfwhm):
        self.apfwhm = apfwhm

    def setApfactor(self, apfactor):
        self.apfactor = apfactor

    def calcNap(self):
        self.nap = math.pi * (self.apfactor*self.apfwhm/2.0)**2

    def setGainRoforDetector(self, detname):
        if detname == 'MB1':
            self.setGain(float(GAIN_MB1))
            self.setRonoiseadu(float(RONA_MB1))
        elif detname == 'MB2':
            self.setGain(float(GAIN_MB2))
            self.setRonoiseadu(float(RONA_MB2))
        elif detname == 'DD1':
            self.setGain(float(GAIN_DD1))
            self.setRonoiseadu(float(RONA_DD1))
        elif detname == 'DD2':
            self.setGain(float(GAIN_DD2))
            self.setRonoiseadu(float(RONA_DD2))
        else:
            sys.stderr.write('Cannot identify detector name\n')
            exit(1)

if __name__ == "__main__":

    ap = AstroPrecision()
    if len(sys.argv) < 7:
        ap.usage()
        exit(1)
    
    detname=sys.argv[1]
    ap.setGainRoforDetector(detname)

    try:
        exptime = float(sys.argv[6])
        ap.setApfwhm(float(sys.argv[2]))
        ap.setApfactor(float(sys.argv[3]))
        ap.setSignal(float(sys.argv[4]), exptime)
        ap.setSkyPerPix(float(sys.argv[5]), exptime)
        ap.calcNap()
    except:
        sys.stderr.write('Parameter initialize error\n')
        exit(1)

    for i in range(1,50):
        snr = ap.calcSnRatioPerExpt(exptime*i)
        print("%7.2f %8.2f" % (snr, exptime*i))
