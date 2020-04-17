#!/usr/bin/env bash
#
#  SaCRA WCS Resolver using Astrometry.net binaries or self calib.
#
#
#       Ver 1.0  2018/10/12  H. Akitaya
#


bindir_astr=/usr/local/astrometry/bin/
#radius=0.1
radius=0.2
#pixscale=0.74
pixscale=0.3312
#pixscale=1.88777  # prime-focus


cleanfile()
{
    if [ -f $1 ]; then
	rm -f $1
    fi
}

logwrite()
{
    if [ "${FLAG_LOG}" = "true" ]; then
       echo $1 >> ${logfn}
    fi
}

wcsresolve_ref()
{
    fn=$1
    refimg=$2
    fn_wcs=$(get_wcsfn $fn)
    
    if [ ! -f ${refimg} ]; then
	echo "${refimg} not found"
	usage_exit
    fi
    fn_wcs=$(get_wcsfn $fn)
    if [ -f ${fn_wcs} -a "${FLAG_OVERRIDE}" = "false" ]; then
	echo "${fn_wcs} exists. Skip."
	return
    fi
    tmprefcat=$(mktemp)
    tmpimgcat=$(mktemp)
    imstar  ${opt_reflect} -j -p ${pixscale}  $refimg | awk '{print($5, $6, $2, $3)}' > ${tmprefcat}
    imstar  ${opt_reflect} -p ${pixscale}  $fn | awk '{print $5, $6, $4}' > ${tmpimgcat}

    ra=`gethead 'RA' $fn`
    dec=`gethead 'DEC' $fn`

    imwcs ${opt_reflect} \
	-e -p ${pixscale} -o ${fn_wcs} \
	-c ${tmpimgcat} -u ${tmprefcat} \
	-w -v -t 10 -h 15 -q irpts $fn
#	-j $ra $dec \
#    imwcs -n 4 -h 10 \
#	  -p ${pixscale} -o ${fn_wcs} \
#	  -c ${tmpimgcat} -u ${tmprefcat} -w -v -e -t 10 $fn

#    echo ${tmprefcat}
#    echo ${tmpimgcat}
#    echo $ra $dec
    rm -f ${tmprefcat} ${tmpimgcat}
    logwrite "${refimg} ${fn} ${fn_wcs}"
}

get_wcsfn()
{
    fn_base=`echo $1 | sed 's/\.[^\.]*$//'`
    fn_wcs=${fn_base}_wcs.fits
    echo ${fn_wcs}
}

wcsresolve_ast()
{
    fn=$1
    fn_wcs=$(get_wcsfn $fn)
    echo ${fn_wcs}
    if [ -f ${fn_wcs} -a "${FLAG_OVERRIDE}" = "false" ]; then
	echo "${fn_wcs} exists. Skip."
	return
    fi
    ra=`gethead 'RA' $fn`
    dec=`gethead 'DEC' $fn`
#    echo $ra $dec
    ${bindir_astr}solve-field --match none \
		  --corr none \
		  --rdls none \
		  --solved none \
		  --index-xyls none \
		  --wcs none \
		  --no-verify \
		  --overwrite \
		  --use-sextractor \
		  --fits-image \
		  --guess-scale \
		  --ra ${ra} --dec ${dec} --radius ${radius} \
		  --new-fits ${fn_wcs} $fn
    cleanfile ${fn_base}-objs.png
    cleanfile ${fn_base}.axy
}
#		  --depth 50 \
#		  --overwrite \
#		  --sigma 40 \
#		  --tweak-order 2 \
#		  -E 5 \

usage_exit()
{
 echo 'Usage: wcsresolve.sh [-oh] fn1 fn2 ... fnn'
 exit 1
}


FLAG_OVERRIDE=false
FLAG_WCSRESOLVE=ast
FLAG_LOG=false
FLAG_AUTO=false
opt_reflect=''
while getopts aohmr:l: OPT
do
    case $OPT in
	a) FLAG_AUTO=true;;
        o) FLAG_OVERRIDE=true
           ;;
        h) usage_exit
           ;;
	r) FLAG_WCSRESOLVE=ref
	   reffn=$OPTARG
	   ;;
	l) FLAG_LOG=true
	   logfn=$OPTARG
	   ;;
	m) opt_reflect='-l'
	   ;;
        \?) usage_exit
            ;;
    esac
done

shift $((OPTIND - 1))

[ $# -lt 1 ] && usage_exit

# main loop

for fn in $*; do
    if [ "${FLAG_WCSRESOLVE}" = "ast" ]; then
	wcsresolve_ast $fn
    elif [ "${FLAG_WCSRESOLVE}" = "ref" ]; then
	wcsresolve_ref $fn $reffn
    fi
done
