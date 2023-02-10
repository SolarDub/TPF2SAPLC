import os
import sys

import matplotlib
import matplotlib.pyplot as plt

from produceCofG import produceCofG
from TPF2SAPLC import TPF2SAPLC
from TargetPixelFile import analysisPlots

def main():

    # Silence number of open plot warnings
    plt.rcParams.update({'figure.max_open_warning': 0})

    # Plot fontsizes
    axvalsz = 14   # Axis values
    axlabsz = 16   # Axis titles

    # Distribute input arguments
    star=str(sys.argv[1])            # Star name
    apRad=float(str(sys.argv[2]))    # Aperture radius
    CofG = int(str(sys.argv[3]))     # Whether to just produce Curve of Growth
    orb  = int(str(sys.argv[4]))     # List of orbits

########################################################################

    ######################
    # Read in HI-1A data #
    ######################


    flagthresh = 1.5 # 0.1; 1; 1.5

    if (CofG == 1):
        produceCofG(orb,star,flagthresh)

    print("")
    tx, flux, bkgd, flag, err = TPF2SAPLC(orb,star,apRad,flagthresh)
    print("")

#    analysisPlots(tx, flux, bkgd, flag)

    plt.show()
    quit()


if __name__ == "__main__":
    main()
