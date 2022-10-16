import os
import sys

import math as m
import numpy as np

import statistics as stats

import fitsio
from fitsio import FITS,FITSHDR

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from scipy import signal

from funcs.TargetPixelFile import *

##################################################################
# Reads in a HI-1A Target Pixel File for a given star during a   #
# given orbit. Performs Simple Aperture Photometry on the star   #
# and produces a photometric light-curve with flux values over a #
# range of timestamps.                                           #
##################################################################


def TPF2SAPLC(orb,star,apRad, flagthresh):

    ######################
    # Read in HI-1A data #
    ######################

#    basedir   = "/Users/pwilliams/Documents/Research/"
    basedir = os.getcwd()

    # Stamp dimensions, timestamp, input pixel stamp
    sXdim, sYdim, tx, stampin = readSTEREO(basedir, orb,star)

##################################################################
# Perform Simple Aperture Photometry of HI-1A target pixel images #
##################################################################

    # Set-up

    apRadCent = 1.5     # Aperture radius for finding flux centroid position

    annrad = 4.7        # Inner radius of annulus
    annwid = 3.2        # Width of annulus
                        # Outer radius of annulus = inner radius + width

    stsz   = 0.1               # Sub-pixel step-size
    gdXsz  = int(sXdim/stsz)   # Grid x-dimension
    gdYsz  = int(sYdim/stsz)   # Grid y-dimension

    # Produce TPF subpixel grid
    xv,yv = subpixelGrid(sXdim, sYdim, stsz)

    # Loop through multiple aperture radii
    # iRad is an integer radius index = 10 * aperture_radius
    for iRad in range(int(apRad*10),int(apRad*10)+1,1):

        # Set up blank HI-1A flux and background flux arrays
        flux = []
        bkgd = []
        flag = []
        err  = []

        apRad = iRad/10  # Current aperture radius
        print("Aperture around "+star+": ",apRad)

        # Loop over each time stamp
        for i in range(len(tx)):

            # Initialize datapoint flag to zero
            flagval = 0

            datfld = [] # Set up blank sub-pixel datafield

            # Stamp array for time-step
            stamp = stampin[i][0]

            #######################################################
            # Produce sub-pixel datafield from target image stamp #
            #######################################################

            datfld = subpixelDataField(stamp, stsz, gdXsz)

            ###########################################
            # Determine star's flux centroid position #
            ###########################################

            # Make initial estimation using pixel around image stamp center
            XCMsub, YCMsub = initialFluxCentroid(sXdim, sYdim, stamp)

            # Find centroid position
            XCMsub, YCMsub = FluxCentroid(apRadCent, xv, yv
                                         , XCMsub, YCMsub
                                         , gdXsz, gdYsz, datfld)


            # Use these centroid coordinates to build new distance-from-centroid array
            Rmat2 = np.sqrt((xv-(XCMsub-0.5))*(xv-(XCMsub-0.5)) \
                          + (yv-(YCMsub-0.5))*(yv-(YCMsub-0.5)))

            #############################################
            # Collect the flux from within the aperture #
            #############################################

            sig, flagval, Nsigp, uninrdat = collectFlux(apRad, Rmat2, gdXsz, gdYsz, datfld, flagthresh)

            ########################################
            # Sample background within the annulus #
            ########################################

            bkval, bkerr = sampleBackground(gdXsz,gdYsz,Rmat2,annrad,annwid,datfld)

            # Remove background from signal
            sig = (sig-Nsigp*bkval)*stsz*stsz

            ######################
            # Append data arrays #
            ######################

            flux.append(sig)      # flux
            bkgd.append(bkval)    # background
            flag.append(flagval)  # data flag
            err.append(bkerr)     # background error

            # Save aperture image data at point halfway along lightcurve
            if(i == round(len(tx)/2)):
                halfwayterms = [XCMsub, YCMsub, datfld, uninrdat]


       # Plot aperture image + lightcurve #
        plotTPFplusLC(apRad, annrad, annwid, stsz, halfwayterms, tx, flux)

#########################
# Lightcurve Processing #
#########################

        print("Data points read: ",len(tx))

        tx   = np.array(tx)
        flux = np.array(flux)
        bkgd = np.array(bkgd)
        flag = np.array(flag)
        err  = np.array(err)

    return tx, flux, bkgd, flag, err
