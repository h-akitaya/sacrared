#!/usr/bin/env python3
#
# SaCRA MuSaSHI Fits Header Modifier
#
#     Ver 1.2  2018/05/24  H. Akitaya
#     Ver 1.3  2018/08/01  H. Akitaya
#
#

import sys
import sacrafits as sf

# main routine
    
if __name__ == '__main__':
    for fn in sys.argv[1:]:
        ftsf=sf.SacraFits(fn)
        
        ftsf.setMJDfromOBSTIME()
        ftsf.setOBJECTfromOBJNAME()
        ftsf.setAIRMASSfromZD()
        ftsf.addHistory("Modified by %s" % (sys.argv[0] ))
        ftsf.modifyExptimeToSec()
        ftsf.setDummyHeaderForHonirred()
        
        ftsf.showAllHeaders()
        ftsf.updateFitsFile()
        ftsf.close()