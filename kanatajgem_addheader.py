#!/usr/bin/env python3
#
# Kanata J-GEM Fits Header Modifier
#
#     Ver 1.0  2019/04/13  H. Akitaya
#

import sys
import sacrafits as sfts

# main routine
    
if __name__ == '__main__':
    for fn in sys.argv[1:]:
        try:
            ftsf=sfts.SacraFits(fn)
        except:
            sys.stderr.write('%s open error. Skip.\n' % (fn))
            continue

        try:
            mjd = ftsf.get_header_value("MJD-CEN")
            expt = ftsf.get_header_value("EXP-TOT")
            if ftsf.get_header_value("HN-ARM") == 'ira':
                filt = ftsf.get_header_value("HN-ARM") == 'FILTER12'
            else:
                filt = ftsf.get_header_value("HN-ARM") == 'FILTER02'
                
            ftsf.set_header_value("JGEM-TEL", "Kanata-HONIR", "J-GEM Tel-inst name")
            ftsf.set_header_value("JGEM-FIL", "H", "J-GEM Filter Name")
            ftsf.set_header_value("JGEM-MJD", mjd, "J-GEM MJD")
            ftsf.set_header_value("JGEM-EXP", expt, "J-GEM EXP-T")
            ftsf.set_header_value("JGEM-EXP", 8.16666666e-5, "J-GEM Pixel Scale (deg/pix)")
            ftsf.update_fits_file()
        except:
            sys.stderr.write('%s treatment error. Skip.\n' % (fn))
            continue
        finally:
            ftsf.close()
