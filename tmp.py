#!/usr/bin/env python3

from sacrafits import SacraFits

out_fn = '20180306a_i.fits'

if __name__ == '__main__':
    sf = SacraFits(out_fn)
    objname = sf.get_header_value('OBJNAME')
    object_name = sf.get_header_value('OBJECT')
    print(objname, object_name)
    object_name_comment = sf.get_header_comment('OBJECT')
    if objname != object_name:
        sf.set_header_value('OBJECT', objname, object_name_comment)
        sf.update_fits_file()
    sf.close()
