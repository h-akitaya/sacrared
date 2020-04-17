#!/usr/bin/env python3
#
# SaCRA file treatment
#
#    2017/xx/xx  Ver 1.0  H. Akitaya
#    2018/08/21  Ver 1.1  H. Akitaya
#    2018/08/28  Ver 2.0  H. Akitaya separated from preproc.py
#    2018/08/28  Ver 2.0  H. Akitaya : add statistics history on dark/flat
#    2018/09/18  Ver 2.1  H. Akitaya : bug fix for statistics output, etc.
#     Ver 2.2  2018/11/09  H. AKitaya; declare to use python3
#
import sys
import os
import re
import tempfile
import time
from subprocess import Popen, PIPE

import numpy
import astropy.io.fits as fits
#from pyraf import iraf

from scrredmisc import *
from sacrafits import SacraFits

FlatFnPattern = re.compile('.*\d\d\d\d\d\d_.\d+\.fits')
DarkFnPattern = re.compile('.*\d\d\d\d\d\d_.\d+\.fits')
#ImgFnPattern = re.compile('.*\d\d\d\d\d\d_.\d+\.fits')
ImgFnPattern = re.compile('.*\d\d\d\d\d\d_.*.fits')
ImcntrOutputPattern = re.compile('(.*x:)(.*)(y:)(.*)')

DarkFnTemplate = "dark_%s_%04i.fits"
FlatFnTemplate = "flat_%s_%s.fits"
DarkDir="dark/"
FlatDir="flat/"

FL_SUBEXT="_fl"

#ImcntrBxs=91
#ImcntrBbxs=151
#ImcntrMsft=300
ImcntrBxs=51
ImcntrBbxs=101
ImcntrMsft=100
Bgfctr=0.8

StatArea='[501:600,501:600]'

class ImgCoord(object):
    def __init__(self, x=0.0, y=0.0):
        self.x=x
        self.y=y
        
    def calc_shift(self, coord, signplus=True):
        if signplus:
            factor = 1.0
        else:
            factor = -1.0
        dx = factor * (self.x - coord.x)
        dy = factor * (self.y - coord.y)
        dxdy = ImgCoord(dx, dy)
        return dxdy

    def show(self):
        print(self.x, self.y)

class ImcentroidError(Exception):
    pass
class ImcentrError(Exception):
    pass

class FitsInfo(object):
    def __init__(self, objname=None, exptime=None, band=None, datatype=None ):
        self.objname=objname
        self.exptime=exptime
        self.band=band
        self.datatype=datatype

    def match_data_params(self, ftsinf):
        result=False
        if ftsinf.datatype == DT_DARK:
            if self.exptime == ftsinf.exptime and \
               self.band == ftsinf.band:
                result=True
        elif ftsinf.datatype == DT_FLAT:
            if self.band == ftsinf.band:
                result=True
        elif ftsinf.datatype == DT_OBJ:
            if (self.band == ftsinf.band and \
                self.objname == ftsinf.objname):
                result=True
        return(result)
        
class SacraFile(object):
    def __init__(self, datatype=None):
        self.datatype=datatype
        self.fn_pattern=re.compile(".*")
        # iraf.images()
        # iraf.proto()
        self.statarea=StatArea
        return

    def set_fn_pattern(self, regrep_pattern):
        self.fn_pattern = regrep_pattern

    def get_median(self, fn):
        try:
            rslt = iraf.imutil.imstatistics(fn, format="no", field="midpt", Stdout=1)
            midpt = SacraFile.str2float_iraf(rslt[0])
            #            if not type(midpt) == float:
            #                raise ValueError('iraf mstatiscics error')
            return midpt
        except:
            return 0.0

    def analyse_imcentroid_shift(self, lines, calcmode='mean'):
#        print lines
        if len(lines) < 2:
            raise ImcentroidError

        cols = lines[1].replace('(', '').replace(')', '').split()
        try:
            dx=float(cols[1])  # delta x
            dy=float(cols[3])  # delta x
            nobj=int(cols[5])  # nobj
        except:
            raise ImcentroidError
        print('Imcentroid_shift(x, y) = (%f, %f) by %i objects' % (dx, dy, nobj))
        dxdy = []
        dxdy.append(dx)
        dxdy.append(dy)
        return dxdy
        
    def get_centroid_shift(self, fn, coord_fn, ref_fn=""):
        try:
            bg = self.get_median(fn) # bg estimate from median
            print("background: %f\nfn: %s\nref: %s" % (bg, fn, ref_fn))
#            imcnt_rslt = iraf.images.immatch.imcentroid(fn, "", coord_fn, negative=no, boxsize=Imcntr_Bs, bigboxsize=Imcntr_BBs, background=bg, lower=bg, nitertate=3, verbose=no)
            result = iraf.imcentroid(fn, ref_fn, coord_fn, \
                                     negative = "no", \
                                     lower = bg * Bgfctr, niterate = 7, \
                                     verbose="no", boxsize = ImcntrBxs, \
                                     bigbox = ImcntrBbxs, \
                                     maxshift = ImcntrMsft, \
                                     Stdout=1)
        except:
            raise ImcentroidError
#        print(result)
        return result

    def get_centroid(self, fn, xy, cbox):
        try:
            result = iraf.proto.imcntr(fn, xy.x, xy.y, cbox=cbox, Stdout=1)
            result_div = ImcntrOutputPattern.findall(result[0])[0]
            if len(result_div) != 4:
                raise imcntrError(result)
            result = ImgCoord(float(result_div[1]), float(result_div[3]))
        except:
            result = ImgCoord(None, None)
        return result

    def add_fits_header(self, fn, header, value, comment):
        sfts = SacraFits(fn)
        sfts.set_header_value(header, value, comment)
        sfts.update_fits_file()
        sfts.close()

    def add_fits_history(self, fn, history_str):
        sfts = SacraFits(fn)
        sfts.add_history(history_str)
        sfts.update_fits_file()
        sfts.close()

    def dark_comb(self, fn_list ):
        return

    def get_dark_list(self, exp_t):
        dk_list=[]
        return

    def write_lst_to_tmpf(self, fn_list):
        tl_f = tempfile.NamedTemporaryFile(mode='w+t')
#        tl_f.writelines(fn_list)
        for fn in fn_list:
#            print(fn)
#            fnpath = os.path.split(fn)
            tl_f.write( "%s\n" % fn)
        tl_f.flush()
        tl_f.seek(0)
        tl_f.flush()
        return(tl_f)
        
    def get_fn_list(self, workdir, ftsinf_in, subext=""):
        # subext is, for example, '_wcs' in 'yyyymmdd_wcs.fits'
        fn_list=[]
        if subext != "":
            pattern_subext = re.compile('.*%s.fits' % (subext))

        if not os.path.isdir(workdir):
            print("Directory not exists.")
            return(fn_list)

        for fn in os.listdir(workdir):
            #File Name Matching
            if not ImgFnPattern.search(fn):
                continue
            if subext != "":
                if not pattern_subext.search(fn):
                    continue

            match_flag = False
            fn_relpath = os.path.join(workdir, fn)

            if not self.fn_pattern.match(fn_relpath):
                continue
            try:
                hdul = fits.open(fn_relpath)
                ftsinf = FitsInfo()
                ftsinf.exptime = float(hdul[0].header['EXPTIME'])
                ftsinf.band = hdul[0].header['FILTER']
                ftsinf.objname = hdul[0].header['OBJNAME']
            except IOError:
                print('Error 1\n')
                continue
            except:
                print('Error 2\n')
                continue
            
            # Check for every data type
            if not ftsinf.match_data_params(ftsinf_in):
#                print('not required file type\n')
                continue
#            print('%s\n' % fn)
            fn_list.append(os.path.abspath(fn_relpath))
#            fn_list.append("%s/%s" % (workdir, fn))
            
            hdul.close()
        return(fn_list)

    def statisticsAmongImages(self, fn_list):
        vals=[]
        for fn in fn_list:
            print('%s%s' % (fn, self.statarea))
            result = iraf.imstatistics('%s%s' % (fn, self.statarea), format="no", field="midpt", Stdout=1)
            print(SacraFile.str2float_iraf(result[0]))
            vals.append(SacraFile.str2float_iraf(result[0]))
        c_max = numpy.amax(vals)
        c_min = numpy.amin(vals)
        c_ave = numpy.average(vals)
        c_std = numpy.std(vals)
        print("debug:", c_max, c_min, c_ave, c_std)
        return(c_max, c_min, c_ave, c_std)

    def writeHistoryOfStatisticsAmongImages(self, fn, c_max, c_min, c_ave, c_std):
        try:
            ftsf = SacraFits(fn)
        except:
            sys.stderr.write('Statistics write error.\n')
        ftsf.add_history('Average: %f' % c_ave)
        ftsf.add_history('Std. Dev.: %f' % c_std)
        ftsf.add_history('Ratio.(%%): %f' % (c_std/c_ave*100.0))
        ftsf.add_history('Max: %f' % c_max)
        ftsf.add_history('Min: %f' % c_min)
        ftsf.close()
        
    def flatCombine(self, band, fn_list, out_fn):
        iraf.imcombine( self.get_fns_str(fn_list), out_fn )
        
    def img_combine(self, lst, out_fn, reject=False, 
                   lsigma=2.5, hsigma=2.5, offsets='none', zeroopt='none'):
        if len(lst)==0:
            sys.stderr.write("(img_combine) Error: no files in the list\n")
            return(1)
        tl_f = self.write_lst_to_tmpf(lst)
        print(tl_f.name)
        if(os.path.isfile(out_fn)):
            print('File %s exists. Abort.' % (out_fn))
            exit(1)
        try:
            if(reject==True):
                iraf.imcombine( "@%s" % tl_f.name, out_fn, lsigma=lsigma,
                                hsigma=hsigma, reject="sigclip", 
                                combine="average", offsets=offsets, 
                                zero=zeroopt)
            else:
                #iraf.imcombine( "@%s" % tl_f.name, out_fn, offsets=offsets, 
                #               zero=zero)
                iraf.imcombine( "@%s" % tl_f.name, out_fn, offsets=offsets,
                                zero=zeroopt)

        except:
            sys.stderr.write("Imcombine Error (%s).\n" % out_fn)
            return(1)
        finally:
            tl_f.close()

    def get_dark_fn(self, band, exp_t, fullpath=False):
#        dark_fn = DarkFnTemplate % (band, int(exp_t/100.0))
        dark_fn = DarkFnTemplate % (band, int(exp_t*10))
        if fullpath:
            dark_fn = os.path.abspath(os.path.join(DarkDir, dark_fn))
        return(dark_fn)

    def get_flat_fn(self, band, mode, fullpath=False):
        flat_fn = FlatFnTemplate % (band, mode)
        if fullpath:
            flat_fn = os.path.abspath(os.path.join(FlatDir, flat_fn))
        return(flat_fn)
    
    def get_fns_str( self, fn_list ):
        flg_first = True
        liststr=""
        for name in fn_list:
            if (not flg_first):
                liststr += (',%s' % name)
            else:
                liststr += name
                flg_first = False
#        print(liststr)
        return(liststr)

    def make_dark(self, band, exptime, overwrite=False):
        fi = FitsInfo(exptime=exptime, band=band, datatype=DT_DARK)
        lst = self.get_fn_list(DarkDir, fi)
        out_fn = self.get_dark_fn(band, exptime, fullpath=True)
        if os.path.isfile(out_fn):
            print('Dark file still exists.')
            if overwrite==False:
                print('Skip.')
                return(True)
        try:
            self.img_combine(lst, out_fn)
        except:
            return(False)
        c_max, c_min, c_ave, c_std = self.statisticsAmongImages(lst)
        self.writeHistoryOfStatisticsAmongImages(out_fn, c_max, c_min, c_ave, c_std)

        return(True)
            
    def pickup_dark_fn(self, band, exptime):
        darkfn = os.path.join(DarkDir, self.get_dark_fn(band, exptime))
        if not os.path.isfile(darkfn):
            darkfn=None
        return(darkfn)

    def pickup_FlatFn(self, band, mode):
        flatfn = os.path.join(FlatDir, self.get_flat_fn(band, MODESTR[mode]))
#        print flatfn
        if not os.path.isfile(flatfn):
            flatfn=None
        return(flatfn)

    def make_flat(self, band, exptime, mode, overwrite=False):
        dark_fn = self.pickup_dark_fn(band, exptime)
#        iraf.clobber="no"
        if dark_fn == None:
#            print("Dark image for %.1f sec not found\n" % (exptime/1000.0))
            print("Dark image for %.1f sec not found\n" % (exptime))
            return(1)
        fi = FitsInfo(exptime=exptime, band=band, datatype=DT_FLAT)
        lst = self.get_fn_list(FlatDir, fi)
        tmp_fn1 = prepare_file(os.path.join(FlatDir, \
                                              self.get_flat_fn(band, "tmp1")))
        tmp_fn2 = prepare_file(os.path.join(FlatDir, \
                                              self.get_flat_fn(band, "tmp2")))
        out_fn = prepare_file(os.path.join(FlatDir, self.get_flat_fn(band, MODESTR[mode])))
        if os.path.isfile(out_fn):
            print('Dark file still exists.')
            if overwrite==False:
                print('Skip.')
                return(True)
            
        
        print("  %s " % out_fn)
        # Dark Subtraction
        self.img_combine(lst, tmp_fn1)
        c_max, c_min, c_ave, c_std = self.statisticsAmongImages(lst)

        self.img_sub(tmp_fn1, dark_fn, tmp_fn2)
        maxval = self.get_max_value(tmp_fn2)
#        print maxval
        self.img_normalize(tmp_fn2, out_fn, maxval)
        self.writeHistoryOfStatisticsAmongImages(out_fn, c_max, c_min, c_ave, c_std)

    def darksub_flatten(self, objname, band, mode, flip=False, override=True):
        fi = FitsInfo(objname=objname, band=band, datatype=DT_OBJ)
        lst = self.get_fn_list("./", fi)
#        print(lst)  #Debug
        for fn in lst:
            ftsf = SacraFits(fn)
            try:
                exptime = float(ftsf.get_header_value('EXPTIME'))
            except:
                ftsf.close()
                continue
            darkfn=self.pickup_dark_fn(band, exptime)
            if (darkfn == None):
#                print("(darksub_flatten) Dark image for %s, %7.2s not found. Skip.\n" % (band, exptime/1000.0))
                print("(darksub_flatten) Dark image for %s, %7.2s sec not found. Skip.\n" % (band, exptime))
                continue
            
            flatfn=self.pickup_FlatFn(band, mode)
            if (flatfn == None):
                print("(darksub_flatten) Flat image for %s, %s not found. Skip.\n" % (band, mode))
                continue
            tmp_fn1 = prepare_file("tmp1.fits")
            tmp_fn2 = prepare_file("tmp2.fits")
            tmp_fn3 = prepare_file("tmp3.fits")
            out_fn = prepare_file( self.get_fn_with_sub_extention(fn, FL_SUBEXT))
            print(self.check_history_sccred_code(fn, "#SCRRED_DSUB"))
            try:
                if not self.check_history_sccred_code(fn, "#SCRRED_DSUB"):
                    self.img_sub(fn, darkfn, tmp_fn1)
                    self.add_fits_history(tmp_fn1, "SACRARED: Dark Subtracted: %s" % darkfn)
                    self.add_fits_history(tmp_fn1, "SACRARED: #SCRRED_DSUB")
                if not self.check_history_sccred_code(tmp_fn1, "#SCRRED_FLTND"):
                    if(flip == False):
                        self.img_div(tmp_fn1, flatfn, out_fn)
                    else:
                        self.img_div(tmp_fn1, flatfn, tmp_fn3)
                        self.img_flip(tmp_fn3, out_fn)
                    self.add_fits_history(out_fn, "SACRARED: Flattened: %s" % flatfn)
                    if flip == True:
                        self.add_fits_history(out_fn, "SACRARED: Fliped for x-direction")
                    self.add_fits_history(out_fn, "SACRARED: #SCRRED_FLTND")
                print(out_fn)
            except:
                sys.stderr.write('Fits file %s had been processed. Ignored.\n' % fn )
            finally:
                clean_file(tmp_fn1)
                clean_file(tmp_fn2)
                clean_file(tmp_fn3)

    def check_history_sccred_code(self, fn, codestr):
        sfts = SacraFits(fn)
        result = sfts.has_history_str(codestr)
        sfts.close()
        return(result)
        
    def get_fn_with_sub_extention(self, fn, subext):
        name, ext = os.path.splitext(fn)
        return("%s%s%s" % (name, subext, ext) ) #  xxxxxx.ext -> xxxxxxx_yy.ext
            
    def get_max_value(self, fn):
        result = iraf.imstatistics(fn, usigma=2.5, lsigma=2.5, nclip=3, \
                                   format="no", field="max", Stdout=1)
        try:
            maxval=float(result[0])
        except:
            maxval=None
        return(maxval)

    def img_sub(self, fn_in1, fn_in2, fn_out):
        iraf.imarith(fn_in1, "-", fn_in2, fn_out)

    def img_div(self, fn_in1, fn_in2, fn_out):
        iraf.imarith(fn_in1, "/", fn_in2, fn_out)

    def img_flip(self, fn_in1, fn_out):
        iraf.imcopy('%s[-*,*]' % (fn_in1), fn_out)

    def img_addheader_skylevel(self, fn_in, skyarea):
        """
        Add sky level count into fits header.
        skyarea = '[x1:x1, y1:y2]'  # iraf region format
        """
        try:
            skylevel = iraf.imstatistics('%s%s' % (fn_in, skyarea),
                                         format='no', field='midpt',
                                         Stdout=1)
            skycor = (-1.0) * float(skylevel[0])
            self.add_fits_header(fn_in, 'SKYLVCOR', skycor, 
                               'Sky correction estimation in %s' % (skyarea))
            print('%s: SKYLVCOR, %f' % (fn_in, skycor))
        except:
            sys.stderr.write('(SKYLVCOR measureing error in %s' % (fn_in))
            return False
        return True

    def img_shift(self, fn_in, fn_out, dxdy):
        try:
            print("imshift %s %s\n" % (fn_in, fn_out))
            iraf.imshift(fn_in, fn_out, dxdy.x, dxdy.y, shifts_file="", \
                         interp_type="linear", boundary_typ="nearest")
            history_str = "Imshifted (%f, %f)" % (dxdy.x, dxdy.y)
            self.add_fits_history(fn_out, history_str)
        except:
            sys.stderr.write("Error in imshift: %s\n" % (fn_in))

    def img_normalize(self, fn_in, fn_out, nrm_factor):
        iraf.imarith(fn_in, "/", nrm_factor, fn_out)
        self.add_fits_history(fn_out, "Nomalization facor: %9.4f" % nrm_factor)

    @staticmethod
    def str2float_iraf(valstr):
        if(valstr) == 'INDEF':
            return float('nan')
        else:
            return float(valstr)
