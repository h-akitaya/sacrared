#!/usr/bin/env python3
#
# image stacking for MuSaSHI preprocessed images
#
#    2018/11/26  Ver 1.0  H. Akitaya

import sys, os, re, time
import argparse
from scrredmisc import *
import sacrafile as sf

DEFAULT_SUBEXT='_wcs'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Options for imgscack.py')
    parser.add_argument('-o', '--override', action='store_true',
                        default=False, help='Override pre-existed output file(s).' )
    parser.add_argument('-e', '--sub-extention', action='store', nargs=None, const=None,
                        default=DEFAULT_SUBEXT, type=str, choices=None, 
                        help='Sub-extention of the image names (e.g.) "_wcs" in ...._wcs.fits; default="%s"' % (DEFAULT_SUBEXT), 
                        metavar=None)
    parser.add_argument('objname', action='store', nargs=None, const=None,
                        default=None, type=str, choices=None, 
                        help='Object name in the fits header', metavar=None)
    parser.add_argument('band', action='store', nargs=None, const=None,
                        default=None, type=str, choices=None, 
                        help='Filter name in the fits header', metavar=None)
    parser.add_argument('exptime', action='store', nargs=None, const=None,
                        default=None, type=float, choices=None, 
                        help='Exposure time in the fits header', metavar=None)
    
    args = parser.parse_args()

    exptime = args.exptime
    objname = args.objname
    band = args.band
    print(objname, band, exptime)

    out_rej_fn = '%s_%s_comb.fits' % (objname, band)
    out_norej_fn = '%s_%s_rejcomb.fits' % (objname, band)

    for fn in [out_rej_fn, out_norej_fn]:
        if os.path.isfile(fn):
            print("File %s exists." % (fn))
            if args.override == True:
                os.remove(fn)
                print("File %s removed." % (fn))
            else:
                print('Skip.')

    fi = sf.FitsInfo(objname=objname, exptime=exptime, band=band, datatype=DT_OBJ)
    sfl = sf.SacraFile()
    print('Construction file list...')
    fnlst = sfl.getFnList('./', fi, subext=args.sub_extention)

    print('Measuring sky level...')
    skyarea = sf.StatArea
    fnlst_tmp = fnlst
    for fn in fnlst_tmp:
        result = sfl.imgAddHeaderSkyLevelEstimate(fn, skyarea)
        if result != 0:
            fnlst.remove(fn) # remove image with sky estimate error
    
    print('Combining...')
    try:
        sfl.imgCombine(fnlst, out_rej_fn, reject=True, lsigma=2.5, hsigma=2.5,
                       offsets='wcs', zeroopt='!SKYLVCOR')
        sfl.imgCombine(fnlst, out_norej_fn, reject=False,
                       offsets='wcs', zeroopt='!SKYLVCOR')
    except:
        sys.stderr.write('Combine error.\n')
        exit(1)
    
    print('Rejection combined image: %s' % (out_rej_fn))
    print('Non-rejection combined image: %s' % (out_norej_fn))
    print('Done.')

    
