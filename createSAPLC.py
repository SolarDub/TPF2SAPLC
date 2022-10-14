import os
import sys

import matplotlib
import matplotlib.pyplot as plt

from funcs.TPF2SAPLC import TPF2SAPLC

def main():

    # Silence number of open plot warnings
    plt.rcParams.update({'figure.max_open_warning': 0})

    # Plot fontsizes 
    axvalsz = 14   # Axis values
    axlabsz = 16   # Axis titles

    # Read in star parameters
    star=str(sys.argv[1])
    apRad=float(str(sys.argv[2]))

    # Research base directory
    readir   = "/Users/pwilliams/Documents/Research/"
    
    resdir   = readir+"stereo/"
    savedir  = resdir+"StellarData/"+star+"/"
    LCdir = savedir+"LC/"
    if os.path.isdir(LCdir) == False:
        os.mkdir(LCdir)

########################################################################
    
    ######################
    # Read in HI-1A data #
    ######################

    orb = 10

    flagthresh = 1.5 # 0.1; 1; 1.5

    print("")
    tx, flux, bkgd, flag, err = TPF2SAPLC(orb,star,apRad,flagthresh)
    print("")

    fig, ax = plt.subplots()
    ax.plot(tx,flux,'.',color="blue")
    ax.plot(tx[flag == 1],flux[flag == 1],'.',color="red")
    
    fig, ax=plt.subplots()
    ax.plot(tx,bkgd,'.',color='blue')

    fig, ax = plt.subplots()
    ax.plot(tx,flag,'.',color="blue")

    fig, ax = plt.subplots()
    ax.plot(flux,bkgd,'.',color="blue")

    plt.show()
    quit()


if __name__ == "__main__":
    main()

