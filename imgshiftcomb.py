#! /usr/bin/env python
#
#   image shift and combine for SaCRA images
#      imgshiftcomb.py
#
#     Ver 1.0 2018/05/07   H. Akitaya
#     Ver 1.1 2018/05/15   H. Akitaya
#     Ver 2.0 2018/08/28   H. Akitaya; rename imported packages
#

import sys,os,re,tempfile, time, shutil
import astropy.io.fits as fits
import argparse

from pyraf import iraf
from subprocess import Popen, PIPE
from scrredmisc import *
import sacrafits as sfts
import sacrafile as sf

WorkDir = "."
SubExt = "_sft"

def main():
    parser = argparse.ArgumentParser(description='Image shift and combine for MuSaSHI images.')
    parser.add_argument('--reject-imcomb', help='Imcomb rejection', action='store_true')
    parser.add_argument('--skip-imshift', help='skip imshift', action='store_true')
    parser.add_argument('sysargs', metavar='Sysargs', type=str, nargs='+',\
                    help='usual option')
    args = parser.parse_args()
#    print(args.skip_imshift)
#    exit(1)
    sfobj = sf.SacraFile(DT_OBJ)
    try:
        objname = str(args.sysargs[0])
        band = str(args.sysargs[1])
        #        xy_init = sf.ImgCoord(float(sys.argv[3]), float(sys.argv[4]))
        #        cbox = float(sys.argv[5])
        fn_coord= str(args.sysargs[2])
        fn_final = str(args.sysargs[3])
        fn_pattern = re.compile(args.sysargs[4])
        #        fn_final = str(sys.argv[6])
        #        fn_pattern = re.compile(sys.argv[7])
    except:
        exit(1)
    ftsinf = FitsInfo(objname=objname, band=band, datatype=DT_OBJ)
    sfobj.setFnPattern(fn_pattern)
    fnlst = sfobj.getFnList(".", ftsinf)
    fnlst.sort()
    #    exit(1)
    #    print fnlst
    #    print len(fnlst)

    if args.skip_imshift:
        print("Imshift skipping")

    try:
        nimg = 0
        nimg_rej = 0
        exptime_total = 0.0
        mjd_ave_tmp = 0.0
        
        fnlist=[]
        fn0=""
        for fn in fnlst:
            if not fn_pattern.match(fn):
                continue
            #            xy = sfobj.getCentroid(fn, xy_init, cbox)
            if fn0 == "":
                fn0 = fn
            fn_out = sfobj.getFnWithSubExtention(fn, SubExt)
            if not args.skip_imshift:
                try:
                    csresult = sfobj.getCentroidShift(fn, fn_coord, fn0)
                    dxdy_list = sfobj.analyseImcentroidShift(csresult, 'median')
                except:
                    print('#%s : imcontroid error. Skip.' % fn)
                    continue
                #dxdy = xy.calcShift(xy_init, signplus=False)
                dxdy = sf.ImgCoord(dxdy_list[0], dxdy_list[1])
                #            dxdy.show()
                if os.path.exists(fn_out):
                    print("File %s exists. Skip." % fn_out)
                else:
                    sfobj.imgShift(fn, fn_out, dxdy)
            else:
                if not os.path.exists(fn_out):
                    print("File %s not found. Skip." % fn_out)
                    continue
                    
            # SCRFVMRK Header (for rejection) check
            sfts = sfts.SacraFits(fn)
            if sfts.hasHeader('SCRFVMRK'):
                if sfts.getHeaderValue('SCRFVMRK') == 'true':
                    print("%s marked as SCRFVMRK=false. Skip.", fn)
                    nimg_rej += 1
                    continue
            # read fits header (exptime, mjd)
            exptime = float(sfts.getHeaderValue("EXPTIME"))/1000.0
            mjd = float(sfts.getHeaderValue("MJD"))
            mjd_ave_tmp += (mjd + exptime/24.0/60.0/60.0)
            exptime_total += exptime
            fnlist.append(fn_out)
            sfts.close()
            nimg += 1
            
    except KeyboardInterrupt:
        sys.stderr.write("Break.")
        exit(1)
    mjd_ave = mjd_ave_tmp / nimg
    
    # combine
    tl_f = sf.writeLstToTmpf(fnlist)
#    print fnlst
    try:
        print "Combined file: %s" % fn_final
        print "List file: %s" % tl_f.name
        shutil.copyfile(tl_f.name, "tmppy.lst")
        if args.reject_imcomb:
            iraf.imcombine("@%s" % (tl_f.name), "%s" % (fn_final), \
                           combine="average", reject="avsigclip", \
                           mclip='yes', lsigma=5.0, hsigma=5.0 )
        else:
            iraf.imcombine("@%s" % (tl_f.name), "%s" % (fn_final), \
                           combine="average", reject="none" )
        print("Combined: %d, Rejected: %d" % (nimg, nimg_rej))
                       
    except:
        sys.stderr.write("Imcombine Error(%s).\n" % fn_final)
        exit(1)
    finally:
        tl_f.close()
        
    rslt = sfts.SacraFits(fn_final)
    rslt.setHeaderValue("MJD_AVE", mjd_ave, "Average MJD for combined images.")
    rslt.setHeaderValue("EXPTIMET", exptime_total, "Total exposure time (s).")
    rslt.setHeaderValue("NCOMB", nimg, "Number of combined images.")
    rslt.addHistory("Processed by imgshiftcomb.py")
    rslt.close()
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write('Ctrl+C Interruption')
        exit(1)
