#!/bin/bash

####################
# Import functions #
####################

source "./shfuncs/prompt.sh"
source "./shfuncs/getOrbits.sh"
source "./shfuncs/getStarname.sh"
source "./shfuncs/produceCofG.sh"
source "./shfuncs/getApertureSize.sh"
source "./shfuncs/ifHelp.sh"

SWS=${*}   # Array of switches

# Check if --help switch has been activated
ifHelp

basedir="./starLists"
filename="OneStar.txt"

CofG="$(produceCofG)"  # Produce Curve of Growth?

infile=${basedir}/${filename}

#############################################
# Prompt user for star name & aperture size #
#############################################

starname="$(getStarname)"
if [[ $starname == "0" ]]
then
  exit
fi

aper="$(getApertureSize)"
if [[ $aper == "0" ]]
then
  exit
fi

#####################################################
# Prompt user for orbits over which to produce TPFs #
#####################################################

ORBS="$(getOrbits)"
if [[ $ORBS == "0" ]]
then
  exit
fi

echo "Orbits selected: ${ORBS}"
echo ' '

if [[ $SWS == *"-s"* ]]
then

  echo "Star: ${starname}"
  if [[ $SWS != *"-c"* ]]
  then
    echo "Aperture: ${aper}"
  fi

  python3 createSAPLC.py $starname $aper $CofG $ORBS

else

  while read -r info; do

    read starname aper <<< "$info"

    echo "Star: ${starname}"
    echo "Aperture: ${aper}"

    python3 createSAPLC.py $starname $aper $CofG $ORBS

  done < "$infile"

fi
