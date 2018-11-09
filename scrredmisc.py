#!/usr/bin/env python3
import os
import numpy as np

DT_OBJ=0
DT_BIAS=1
DT_FLAT=2
DT_DARK=3

MOD_MIMG=0 # MuSaSHI Imaging Mode
MOD_SIMG=1 # Single CCD Imaging Mode
MOD_IMPOL=2 # MuSaSHI Imaging Polarimetry Mode

MODESTR=['mimg', 'simg', 'impol']

def prepareFile(fn):
    cleanFile(fn)
    return(fn)

def cleanFile(fn):
    if os.path.isfile(fn):
        os.remove(fn)

       
        
