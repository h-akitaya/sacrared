#!/usr/local/bin/bash
#
#    preprocessing MuSaSHI observed data
#
#      Ver 1.0  2018/12/24   H. Akitaya
#

datadir='/rawdata/obs'
workdir='/workarea/Student13/preproc'
sacrareddir='/home/akitaya/iraf/sacrared'
datestr=`date -u +'%Y%m%d'`

#preproc_flag_fn='do_preproc'

chk_preproc_flag()
{
    if [ -f "${datadir}/${datestr}/${preproc_flag_fn}" ]; then
	return 0
    else
	return 1
    fi
}
usage()
{
    echo "$0 [-d (datestr; dafault=today_in_UT))]"
    echo "  (e.g.) preproc_musasho.sh -d 20181223"
}

while getopts "d:h" OPT; do
   case $OPT in
	\?) OPT_ERROR=1; break;;
	d) datestr=$OPTARG;;
	h) usage; exit;;
    esac
done
shift $((OPTIND - 1))

#! (chk_preproc_flag) && exit 1

# main process

#rsync -rav ${datadir}/${datestr} ${workdir}

#cd ${workdir}/${datestr}


${sacrareddir}/musashi_addheader.py
${sacrareddir}/preproc.py

bands='r i z'

objlist=`cut -f 3 -d ' ' explog*.log | uniq | xargs`
exptlist=`cut -f 5 -d ' ' explog*.log | uniq | xargs`

${sacrareddir}/musashi_addheader.py *.fits

for obj in ${objlist}; do
    for exptime in ${exptlist}; do
	for band in ${bands}; do
	    echo ${reducbin} ${obj} ${band} ${exptime}
	    ${sacrareddir}/preproc.py ${obj} ${band} ${exptime}
	done
    done
done

${sacrareddir}/wcsresolve.sh *_fl.fits

