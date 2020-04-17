#! /usr/bin/env python
#
#   photometry for point sources with WCS coordinate
#      qlphot2wcsimgs.py
#
#     Ver 1.0 2018/05/07   H. Akitaya
#     Ver 1.1 2018/05/15   H. Akitaya
#

import sys,os,re,tempfile, time, shutil
import astropy.io.fits as fits
import argparse

from pyraf import iraf
from subprocess import Popen, PIPE
from scrredmisc import *
from sacrafits import *
from sacrafile import *

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
    sf = SacraFile(DT_OBJ)
    try:
        objname = str(args.sysargs[0])
        band = str(args.sysargs[1])
        #        xy_init = ImgCoord(float(sys.argv[3]), float(sys.argv[4]))
        #        cbox = float(sys.argv[5])
        fn_coord= str(args.sysargs[2])
        fn_final = str(args.sysargs[3])
        fn_pattern = re.compile(args.sysargs[4])
        #        fn_final = str(sys.argv[6])
        #        fn_pattern = re.compile(sys.argv[7])
    except:
        exit(1)
    ftsinf = FitsInfo(objname=objname, band=band, datatype=DT_OBJ)
    sf.set_fn_pattern(fn_pattern)
    fnlst = sf.get_fn_list(".", ftsinf)
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
            #            xy = sf.get_centroid(fn, xy_init, cbox)
            if fn0 == "":
                fn0 = fn
            fn_out = sf.get_fn_with_sub_extention(fn, SubExt)
            if not args.skip_imshift:
                try:
                    csresult = sf.get_centroid_shift(fn, fn_coord, fn0)
                    dxdy_list = sf.analyse_imcentroid_shift(csresult, 'median')
                except:
                    print('#%s : imcontroid error. Skip.' % fn)
                    continue
                #dxdy = xy.calc_shift(xy_init, signplus=False)
                dxdy = ImgCoord(dxdy_list[0], dxdy_list[1])
                #            dxdy.show()
                if os.path.exists(fn_out):
                    print("File %s exists. Skip." % fn_out)
                else:
                    sf.img_shift(fn, fn_out, dxdy)
            else:
                if not os.path.exists(fn_out):
                    print("File %s not found. Skip." % fn_out)
                    continue
                    
            # SCRFVMRK Header (for rejection) check
            sfts = SacraFits(fn)
            if sfts.has_header('SCRFVMRK'):
                if sfts.get_header_value('SCRFVMRK') == 'true':
                    print("%s marked as SCRFVMRK=false. Skip.", fn)
                    nimg_rej += 1
                    continue
            # read fits header (exptime, mjd)
            exptime = float(sfts.get_header_value("EXPTIME"))/1000.0
            mjd = float(sfts.get_header_value("MJD"))
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
    tl_f = sf.write_lst_to_tmpf(fnlist)
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
        
    sfts = SacraFits(fn_final)
    sfts.set_header_value("MJD_AVE", mjd_ave, "Average MJD for combined images.")
    sfts.set_header_value("EXPTIMET", exptime_total, "Total exposure time (s).")
    sfts.set_header_value("NCOMB", nimg, "Number of combined images.")
    sfts.add_history("Processed by imgshiftcomb.py")
    sfts.close()
    
if __name__ == "__main__":
    iraf.honir()
    #    iraf.lparam("imexam")
    print(sys.argv[1], sys.argv[2])
    iraf.honir.qlphot(sys.argv[1], sys.argv[2], apertures="9.0",
                      cbox=20.0, annulus=10.0, dannulus=3.0, interactive='no')
#    iraf.qphot(sys.argv[1], 20.0, 9.0, 3.0, "8.0", coords=sys.argv[2],
#               interactive="no", zmag=25.0, output="tmp.mag")
