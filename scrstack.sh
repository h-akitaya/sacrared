#!/usr/bin/env bash
#
#   Reduction Pipeline Script (stacking)
#
#      2018/12/10 H. Akitaya
#

bands='r i z'

objlist=`cut -f 3 -d ' ' explog*.log | uniq | xargs`
echo ${objlist}

sacrareddir=/home/akitaya/iraf/sacrared

if [ $# -eq 0 ];then
    exptime=30.0
fi

for obj in ${objlist}; do
    for band in ${bands}; do
	echo ${sacrareddir}/imgstack.py ${obj} ${band} ${exptime}
	${sacrareddir}/imgstack.py ${obj} ${band} ${exptime}
    done
done



	
