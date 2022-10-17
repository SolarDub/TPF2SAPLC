#!/bin/bash

# getApertureSize
# Get aperture size from user
function getApertureSize() {

  if [[ $SWS == *"-s"* ]]   && [[ $SWS != *"-c"* ]]   # Execute if user defined a star
  then

    while [[ $apsize == "" ]] || [[ $apsize > "4.5" ]] && [[ $apsize != "0" ]]; do
      PRMPT1="Enter aperture size"  # Create user prompt text
      PRMPT2="(in pixels)"
      PRMPT3="Enter 0 to quit."
      APENT="$(prompt "$PRMPT1\n$PRMPT2\n$PRMPT3")"  # Prompt user to enter value

      apsize="${APENT%" "}"                    # Remove trailing space
    done

    echo $apsize

  else

    echo "-1"

  fi
}

export -f getApertureSize
