#!/usr/bin/env python3
#
#  Correct OBJECT header to be consistent with OBJNAME
#
#    2020/07/16  H. Akitaya
#

import os
import sys
import glob

from sacrafits import SacraFits


class CorrectObjectHeader(object):
    def __init__(self, fn_pattern):
        self.fnlist = glob.glob(fn_pattern)

    def correct_header(self):
        for fn in self.fnlist:
            try:
                sf = SacraFits(fn)
            except:
                sys.stderr.write('File {} open error.\n'.format(fn))
                continue
            if sf.has_header('objname'):
                objname = sf.get_header_value('objname')
                if sf.has_header('object'):
                    objname_old = sf.get_header_value('object')
                    comment = sf.get_header_comment('object')
                    sf.set_header_value('object', objname, comment)
                    sf.add_history('Header OBJECT corrected: {}->{}'.format(objname_old, objname))
                    print(fn, objname_old, objname)
                else:
                    comment = 'Name of the object observed'
                    sf.set_header_value('object', objname, comment)
                    sf.add_history('Header OBJECT appended')
                    print(fn, "--", objname)
            sf.flush()
            sf.close()

            
if __name__ == '__main__':
    if len(sys.argv) == 0:
        sys.exit(1)
    fn_pattern = sys.argv[1]
    coh = CorrectObjectHeader(fn_pattern)
    coh.correct_header()
