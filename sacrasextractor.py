#!/usr/bin/env python3
#
#   SExtractor for SaCRA image
#
#     2020/07/20  Ver. 1.0.0   H. Akitaya
#

__version__ = '1.0.0'
__author__ = 'Akitaya, H'

import os
import sys
import subprocess

from astropy.io import ascii
from astropy.table import Table, SortedArray
import numpy as np

SEXTRACTOR_BINDIR='/usr/local/bin'

SX_DEFAULT_CONF='astmt.sex'

MAG_BRIGHTER_LIM = 0.2
MAG_FAINTER_LIM = 0.4

class SacraSExtractor(object):
    def __init__(self, fn=None, verbose=False):
        self.fn = fn
        self.verbose = verbose
        self.data = None
        self.index_array = []

    def read_extracted_table(self):
        try:
            self.data = ascii.read(self.fn, format='sextractor')
            # print(type(self.data))
        except ascii.core.InconsistentTableError:
            sys.stderr.write('Exception: Table is not SExtractor format.\n')
            sys.exit(1)
        except OSError:
            sys.stderr.write('Exception: File read error.\n')
            sys.exit(1)

    def apply_sextractor(self, fits_fn, param_fn=SX_DEFAULT_CONF):
        command = '{}/sex {} -c {}'.format(SEXTRACTOR_BINDIR, fits_fn, param_fn)
        print(command)
        try:
            subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as instance:
            print('Exception occured.')
            print(instance)
            sys.exit(1)

    def add_indexes(self):
        self.data.add_index(['MAG_AUTO', 'FWHM_IMAGE'])

    def show_table_all(self):
        self.data.pprint_all()

    def return_min_and_max_indexes(self, index_array):
        index_min = int(len(index_array)*MAG_BRIGHTER_LIM)
        index_max = int(len(index_array)*MAG_FAINTER_LIM)
        print('# min:{}, max:{}, total:{}'.format(index_min, index_max, len(index_array)))
        return index_array[index_min:index_max]

    
    def calc_fwhm_median(self):
        sorted_array = self.data.argsort('MAG_AUTO')
        sorted_array_med = self.return_min_and_max_indexes(sorted_array)
        try:
            fwhms = np.array([self.data['FWHM_IMAGE'][i] for i in sorted_array_med])
        except:
            print('Error!')
        fwhms_std = np.std(fwhms)
        fwhms_median = np.median(fwhms)
        if self.verbose:
            print(fwhms)
            print('# FWHM: {0:.2f} +/- {1:.2f}'.format(fwhms_median, fwhms_std))
        return fwhms_median, fwhms_std

    def calc_fwhm_median_from_img(self, fn=None):
        if fn is not None:
            self.fn = fn
        self.read_extracted_table()
        self.add_indexes()
        fwhms_median, fwhms_std = self.calc_fwhm_median()
        return fwhms_median, fwhms_std
