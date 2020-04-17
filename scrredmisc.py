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

def prepare_file(fn):
    clean_file(fn)
    return(fn)

def clean_file(fn):
    if os.path.isfile(fn):
        os.remove(fn)

def make_subextfn(fn, subext):
    """
    Return filename with a subextention.
    (xxx.ext -> xxx_subext.ext)
    """
    fn_strs= os.path.splitext(fn)
    new_fn = fn_strs[0] + subext + fn_strs[1]
    return new_fn
