#!/bin/bash

# produceCofG
# Decide whether to produce Curve of Growth
function produceCofG() {

  if [[ $SWS == *"-c"* ]]
  then
    echo "1"
  else

    echo "0"

  fi
}

export -f produceCofG
