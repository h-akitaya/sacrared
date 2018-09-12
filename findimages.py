#!/usr/bin/env python

import os, sys
import sacrafits as sfts

def showimgfn(dir, objname):
    fnlist=[]
    fns = os.listdir(dir)
    fns.sort()
    for fn in fns:
        fn_path=os.path.abspath('./%s/%s' % (dir, fn))
        if not os.path.isfile(fn_path):
            sys.stderr.write('%s not file Error\n' % fn_path)
            continue
#        print(fn_path)
        try:
            ftsimg = sfts.SacraFits(fn_path, updatemode=False)
        except:
#            sys.stderr.write('Error2\n')
            continue
        try:
            objname_header = ftsimg.getHeaderValue('OBJNAME')
        except:
#            sys.stderr.write('Error\n')
            continue
#        print(objname_header)
        if objname_header == objname:
            fnlist.append(fn_path)
        ftsimg.close()
    printfnlist(fnlist)


def printfnlist(fnlist):
    fnlist.sort()
    for fn in fnlist:
        print(fn)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit(1)

    objname = sys.argv[1]
    dirs = sys.argv[2:]
    dirs.sort()

    for dir in dirs:
        if not os.path.isdir(dir):
            continue
        showimgfn(dir, objname)
        
