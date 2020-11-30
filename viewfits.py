#!/usr/bin/env python
#
#   view images at ds9
#      viewfits.py
#
#     Ver 1.0 2018/05/08   H. Akitaya
#     Ver 1.1 2018/05/14   H. Akitaya; Automode
#     Ver 2.0 2018/08/28   H. Akitaya; rename preproc -> sacrafile
#

import sys
import os
import re
import tempfile
import time
import shutil
from optparse import OptionParser

import astropy.io.fits as fits
import pyds9
from subprocess import Popen, PIPE
from scrredmisc import *
from sacrafits import *
import sacrafile_woiraf as sf
IntPattern = re.compile('\d+')
WaitTime = 0.5
automode = False
Ds9FitsView = 'ds9fitsview'

def get_regfile(fn):
    fns = os.path.splitext(fn)
    fn_reg = fns[0] + '.reg'
    if not os.path.isfile(fn_reg):
        return None
    return fn_reg

def showFitsImage(fn, d):
    d.set('file %s' % (fn))
    if (options.xcenter is not None ) and (options.ycenter is not None):
        d.set('crop {} {} {} {}'.format(options.xcenter, options.ycenter,
                                        options.crop, options.crop))
    d.set('zoom to fit')
    #    d.set('zoom to 1/2')
    fn_reg = get_regfile(fn)
    if fn_reg != None:
        show_regions(fn_reg, d)
 
def show_regions(fn_reg, d):
    with open(fn_reg, 'r') as f:
        for line in f.readlines():
            reg_command = line.strip()
            if reg_command.startswith('#'):
                continue
            if reg_command.startswith('global'):
                continue
            if reg_command.startswith('circle'):
                d.set('regions',  'image; {}'.format(reg_command))

def waitKeyInput():
    try:
        print('Enter to next frame / b + Enter to back')
        com = input(' >> ').strip()
        if IntPattern.search(com):
            return 'goto %s' % com
        elif com == 'c':
            return 'click'
        elif com == 'x':
            return 'reject'
        elif com == 'b':
            return 'back'
        elif com == 'q':
            return 'quit'
        elif com == 'n':
            return 'next'
        elif com == 'm':
            return 'mark'
        elif com == 'u':
            return 'unmark'
        elif com == 'a':
            return 'auto'
        else:
            return 'next'
    except KeyboardInterrupt:
        print('Use "quit" to finish the task')
        return ''

def showImages(files, d, automode):
    n = 0
    n_max = len(files)

    while (n < n_max):
        try:
            if not os.path.isfile(files[n]):
                print(('File %s does not exists. Skip.' % (files[n]) ))
            else:
                print(('Show %s on ds9 (%s/%s).' % (files[n], n+1, n_max) ))
                showFitsImage(os.path.abspath(files[n]), d)
            if automode:
                comarray[0] = 'next'
            else:
                com = waitKeyInput()
                comarray = com.split()
            if comarray[0] == 'click':
                a = d.get('imexam coordinate image')
                print(a)
                #d.get('imexam \{Click at $x,$y\}')
                
            if comarray[0] == 'goto':
                naim = int(comarray[1])
                if naim > n_max+1:
                    print("Number Error.")
                    n += 1
                else:
                    n = naim - 1
            elif comarray[0] == 'quit':
                print('Quit')
                exit(0)
            elif comarray[0] == 'mark':
                try:
                    print('Mark fitsheader SCRVFMRK=true')
                    sfimg = sf.SacraFits(files[n])
                    sfimg.set_header_value('SCRVFMRK', 'ture', 'Marked by viewfits.py')
                    sfimg.close()
                except:
                    printf("Fits file open error. Skip.")
            elif comarray[0] == 'unmark':
                try:
                    print('Unmark fitsheader SCRVFMRK=false')
                    sfimg = sf.SacraFits(files[n])
                    sfimg.set_header_value('SCRVFMRK', 'false', 'Marked by viewfits.py')
                    sfimg.close()
                except:
                    printf("Fits file open error. Skip.")
            elif comarray[0] == 'intr':
                print('Interractive Mode')
                automode = False
            elif comarray[0] == 'auto':
                print('Auto Mode')
                automode = True
                n += 1
            elif comarray[0] == 'back':
                if n != 0:
                    n -= 1
                else:
                    print('First frame')
            else: # comarray[0] == 'next':
                n += 1
        except KeyboardInterrupt:
            print('Ctrl+C Interrupted.')
            print('Cease automode')
            automode = False
            time.sleep(WaitTime)
            n += 1
            continue
            
    print('Finished.')
    exit(0)
#    d.close()

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-x", "--xcenter", dest="xcenter", type="float",
                      help="x_center coordinate")
    parser.add_option("-y", "--ycenter", dest="ycenter", type="float",
                      help="y_center coordinate")
    parser.add_option("-c", "--crop", dest="crop", type="float",
                      help="crop", default=200)
    (options, args) = parser.parse_args()
    print(options.xcenter, options.ycenter, options.crop)
    
    automode = False
    lstfn = args[0]
    try:
        fn = open(lstfn, 'r')
    except:
        sys.stderr.write('File open error. Abort.')

    files = []
    for line in fn.readlines():
        files.append(line.strip())
    fn.close()

    ds9list = pyds9.ds9_targets()
    if ds9list == None:
        print("active ds9 not found. Abort.")
        exit(1)
    print("%d ds9 windows found." % (len(ds9list)))
    print("use %s" % ds9list[0])
    d = pyds9.DS9(target=ds9list[0])
    if (options.xcenter is not None ) and (options.ycenter is not None):
        d.set('crop {} {} {} {}'.format(options.xcenter, options.ycenter,
                                        options.crop, options.crop))
    else:
        d.set('zoom to fit')
    d.set('scale zscale')
    showImages(files, d, automode)
