#!/bin/bash
#
#   Reduction Pipeline Script

bands='r i z'

objlist=`cut -f 3 -d ' ' explog*.log | uniq | xargs`
echo ${objlist}
sacrareddir=/home/Student13/sacra_tools/sacrared

if [ $# -eq 0 ];then
    exptime=30.0
fi

${sacrareddir}/musashi_addheader.py *.fits

for obj in ${objlist}; do
    for band in ${bands}; do
	echo ${reducbin} ${obj} ${band} ${exptime}
	${sacrareddir}/preproc.py ${obj} ${band} ${exptime}
    done
done



	