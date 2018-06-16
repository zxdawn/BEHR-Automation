#!/bin/bash
#
# This function will contact the MODIS LAADS Web server at https://ladsweb.modaps.eosdis.nasa.gov and
# identify MYD06 and MCD43D* files from specific months and retrieve them, putting them in the proper directory.
#
# The MODIS root directory on the file server should be defined in the env. variable MODDIR. (This
# directory should contain subfolders for the various MODIS products.)
#
# Xin Zhang <xinzhang1215@gmail.com> 13 Jun 2018
# The automodis.py script must be there as well for this to work

DEBUG=1

fsource=${BASH_SOURCE[0]}
thisfile=$(readlink -f $fsource)
scriptdir=$(dirname $thisfile)

# Define root MODIS directory on the file server from the env. var MODDIR.
# if empty, error.
if [[ $MODDIR == '' ]]
then
    echo "ERROR - GET_ALL.SH: Env. variable MODDIR undefined"
    exit 1
fi

# Remote directories have the pattern https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/
# <collection>/<product>/<year>/<day-of-year>/<data-files>. This is the root
# remote dir
REMOTEDIR="https://ladsweb.modaps.eosdis.nasa.gov/archive/allData"

## ====================================== ##
## MCD43D07, MCD43D08, MCD43D09, MCD43D31 ##
## ====================================== ##

function usage {
  echo "Usage:"
  echo "  $0 [options]"
  echo ""
  echo "Description:"
  echo "  This script will recursively download all files if they don't exist"
  echo "  from a LAADS URL and stores them to the specified path"
  echo ""
  echo "Options:"
  echo "    -s|--startdate [date]         Recursively download files at [date]"
  echo "    -e|--enddate [date]         Recursively download files at [date]"
  echo "    -t|--token [token]        Use app token [token] to authenticate"
  echo ""
  echo "Dependencies:"
  echo "  Requires 'jq' which is available as a standalone executable from"
  echo "  https://stedolan.github.io/jq/download/"
}

function recurse {
  local startdate=$1
  local enddate=$2
  local token=$3
  
  syear=`date -d ${startdate} +%Y`
  eyear=`date -d ${enddate} +%Y`
  sday=`date -d ${startdate} +%j`
  eday=`date -d ${enddate} +%j`
  for y in `seq ${syear} 1 ${eyear}`
  do
    dest="${MODDIR}/MCD43D/${y}/"
    if [[ ! -d $dest ]]
    then
        echo "Creating $dest"
        mkdir -p $dest
    fi

    for doy in `seq ${sday} 1 ${eday}`
    do
      srcs=(
        "${REMOTEDIR}/6/MCD43D07/${y}/${doy}/"
        "${REMOTEDIR}/6/MCD43D08/${y}/${doy}/"
        "${REMOTEDIR}/6/MCD43D09/${y}/${doy}/"
        "${REMOTEDIR}/6/MCD43D31/${y}/${doy}/"
        )
      for src in "${srcs[@]}"
      do
        echo "Querying ${src}.json"

        for file in $(curl -s -H "Authorization: Bearer ${token}" ${src}.json | jq '.[] | select(.size!=0) | .name' | tr -d '"')
        do
          if [ ! -f ${dest}/${file} ] 
          then
            echo "Downloading $file to ${dest}"
            # replace '-#' with '-s' below for without download progress bars
            curl -# -H "Authorization: Bearer ${token}" ${src}/${file} -o ${dest}/${file}
          else
            echo "Skipping $file ..."
          fi
        done
      done
    done
  done
}

POSITIONAL=()
while [[ $# -gt 0 ]]
do
  key="$1"

  case $key in
    -s|--startdate)
    startdate="$2"
    shift
    shift
    ;;
    -e|--enddate)
    enddate="$2"
    shift
    shift
    ;;
    -t|--token)
    token="$2"
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
  esac
done

if [ -z ${startdate+x} ]
then 
  echo "startdate is not specified"
  usage
  exit 1
fi

if [ -z ${enddate+x} ]
then 
  echo "enddate is not specified"
  usage
  exit 1
fi

if [ -z ${token+x} ]
then 
  echo "Token is not specified"
  usage
  exit 1
fi

recurse "$startdate" "$enddate" "$token"

## =============== ##
##      MYD06      ##
## =============== ##

# Cloud data requires a little more work. There are almost 300 granules per day;
# obviously we don't want to download all of them if we don't need them (and we
# don't). It's much more convinient to select which ones based on their lat/lon
# coordinates, so we will interface with the MODIS web services using SOAPpy.
# This will call the automodis.py Python script which will do this (the
# automodis.py script must be in the same folder as this one to work properly).
# This python script will return a list of URLs that fit the specified lon/lat
# criteria; this will then check if those files have already been downloaded and
# if not will call wget to retrieve the file in the proper folder.
#
# Josh Laughner <joshlaugh5@gmail.com> 7 Aug 2015

startdate=$(date -d $startdate +'%Y-%m-%d 00:00:00')
enddate=$(date -d $enddate +'%Y-%m-%d 23:59:59')

# lon/lat bounds are specified as default values in the Python script
# only retrieve granules with daytime information

echo "Getting MYD06 file list..."
#filelist=$(python ${scriptdir}/automodis.py --products MYD06_L2 --startTime "$startdate" --endTime "$enddate" --dayNightBoth 'DB')
python ${scriptdir}/MODIS_SOAP/automodis.py --product "MYD06_L2" --collection "61" --startTime "${startdate}" --endTime "${enddate}" --output-file "${MODDIR}/MYD06_L2/modis_urls.txt"
echo "Done."
filelist=$(cat ${MODDIR}/MYD06_L2/modis_urls.txt)
for f in $filelist
do
    fname=$(basename $f)
    y=${fname:10:4}
    doy=${fname:14:3}

    fullLocalDir="${MODDIR}/MYD06_L2/${y}"

    if [[ ! -d $fullLocalDir ]]
    then
        mkdir -p $fullLocalDir
    fi

    cd $fullLocalDir

    if [[ ! -f $fname ]]
    then
        echo "Retrieving $fname"
        wget -q -nH -nd $f
    fi
done

exit 0
