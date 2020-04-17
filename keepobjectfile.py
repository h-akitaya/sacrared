#!/usr/bin/env python
#
# SaCRA MuSaSHI Keep images with given Object name
#     ( move other images to ./TempDir/)
#
#     Ver 1.0  2018/08/28  H. Akitaya
#
#
import sys, os, glob
import sacrafits as sf

TempDir = "tmpmove"

# main routine

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s Object_Name" % (sys.argv[0]))
        exit(1)

    obj_aim = sys.argv[1]

    if os.path.exists(TempDir):
        if not os.path.isdir(TempDir):
            print("%s is not directory." % TempDir)
            exit(1)
    else:
        os.mkdir(TempDir)

    fitslist = glob.glob('*.fits')
    
    for fn in fitslist:
        if not os.path.isfile(fn):
            next
        try:
            ftsf = sf.SacraFits(fn)
            objname = ftsf.get_header_value('OBJECT')
        except:
            sys.stderr.write('astropy.fits error. Skip.\n')
            next
        if objname != obj_aim:
            os.rename(fn, './%s/%s' % (TempDir, fn) )
            print('%s: mv %s -> ./%s/' % (objname, fn, TempDir ))
