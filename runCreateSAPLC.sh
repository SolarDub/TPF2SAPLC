#!/bin/bash

####################
# Import functions #
####################

SRCBASHDIR="./src/Bash/"
SRCPYTHDIR="./src/Python/"

source ${SRCBASHDIR}"prompt.sh"
source ${SRCBASHDIR}"getOrbits.sh"
source ${SRCBASHDIR}"getStarname.sh"
source ${SRCBASHDIR}"produceCofG.sh"
source ${SRCBASHDIR}"getApertureSize.sh"
source ${SRCBASHDIR}"ifHelp.sh"

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

  python3 ${SRCPYTHDIR}createSAPLC.py $starname $aper $CofG $ORBS

elif [[ $SWS == *"-t"* ]]
then

  while read -r info; do

    read starname aper <<< "$info"

    echo "Star: ${starname}"
    echo "Aperture: ${aper}"

    python3 ${SRCPYTHDIR}createSAPLC.py $starname $aper $CofG $ORBS

  done < "$infile"

fi
