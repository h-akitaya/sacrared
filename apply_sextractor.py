#!/usr/bin/env python3

import sys
            
from sacrasextractor import SacraSExtractor

if __name__ == '__main__':
    sse = SacraSExtractor()
    fits_fn = sys.argv[1]
    sse.apply_sextractor(fits_fn)
