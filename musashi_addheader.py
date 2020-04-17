#!/usr/bin/env python3
#
# SaCRA MuSaSHI Fits Header Modifier
#
#     Ver 1.2  2018/05/24  H. Akitaya
#     Ver 1.3  2018/08/01  H. Akitaya
#     Ver 2.0  2018/08/28  H. Akitaya; change fits files
#     Ver 2.1  2018/08/28  H. Akitaya; error treatment for broken fits file
#     Ver 2.2  2018/11/09  H. AKitaya; declare to use python3
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
            ftsf.set_mjd_from_obstime()
            ftsf.set_object_from_objname()
            ftsf.set_airmass_from_zd()
            ftsf.add_history("Modified by %s" % (sys.argv[0] ))
            ftsf.exptime_to_sec()
            ftsf.dummy_header_honirred()
        
            ftsf.show_all_headers()
            ftsf.update_fits_file()
        except:
            sys.stderr.write('%s treatment error. Skip.\n' % (fn))
            continue
#        finally:
#            ftsf.close()
