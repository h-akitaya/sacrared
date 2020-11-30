#!/usr/bin/env python3
#
#  2020/07/16 H. Akitaya
#

import os
import sys
import glob

from ccdproc import ImageFileCollection
import numpy as np
from astropy.table import Table, Column
from astropy.io import fits

from sacrafits import SacraFits

DEFAULT_TBL_NAMES = ('objname', 'object', 'exptime', 'filter')
DEFAULT_TBL_DTYPE = ('S', 'S', 'f', 'S')

class ShowFileList(object):
    def __init__(self, fn_pattern,
                 names=DEFAULT_TBL_NAMES,
                 dtype=DEFAULT_TBL_DTYPE):
        self.fnlist = glob.glob(fn_pattern)
        self.nlist = len(self.fnlist)
        self.names = names
        self.tbl = Table(names=names, dtype=dtype)

    def read_items(self):
        for fn in self.fnlist:
            values = []
            sf = SacraFits(fn, updatemode=False)
            for header in self.names:
                if sf.has_header(header):
                    values.append(sf.get_header_value(header))
                else:
                    values.append(None)
            self.tbl.add_row(values)
            sf.close()
        col_fn = Column(name='filename', data=self.fnlist)
        self.tbl.add_column(col_fn, index=0)

    def show_table(self):
        self.tbl.pprint_all()

def usage_exit():
    print('Usage: {} fn_pattern'.format(sys.argv[0]))
    sys.exit(1)
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage_exit()
    fn_pattern = sys.argv[1]
    sfl = ShowFileList(fn_pattern)
    sfl.read_items()
    sfl.show_table()
