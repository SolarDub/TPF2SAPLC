##################################################################
# Reads in a HI-1A Target Pixel File for a given star during a   #
# given orbit. Performs Simple Aperture Photometry on the star   #
# for one image over a range of apertures, producing a graphical #
# Curve of Growth, and its derivative.                           #
##################################################################


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

from TargetPixelFile import *

def plotCofG(halfwayterms, flux):

    ############
    # Plot CoG #
    ############

    XCMsub = halfwayterms[0]
    YCMsub = halfwayterms[1]
    datfld = halfwayterms[2]
    uninrdat = halfwayterms[3]

    unimax              = max(uninrdat)
    unimin              = min(uninrdat)

    bpxc = 100           # center coordinate of brightest target pixel

    flux  = np.array(flux)
    ap    = np.linspace(0,5,51)
    dap   = 0.1
    dflx  = np.concatenate((([0]), np.diff(flux)/dap))

    fig, ax = plt.subplots(1,2, gridspec_kw={'width_ratios': [1, 3]},figsize=(12,6))
    ax[0].imshow(np.flipud(datfld),extent=[-10,10,-10,10],cmap=plt.get_cmap('pink')\
                ,vmin=unimin,vmax=unimax)
    plt.gca().invert_yaxis()
    ax[0].plot(bpxc/10+XCMsub-10,bpxc/10+YCMsub-10,'.',color='green')
    x_label_list = ['-10', '-5', '0', '5', '10']
    ax[0].set_xticks([-10,-5,0,5,10])
    ax[0].set_xticklabels(x_label_list, fontsize=14)
    y_label_list = ['-10', '-5', '0', '5', '10']
    ax[0].set_yticks([-10,-5,0,5,10])
    ax[0].set_yticklabels(y_label_list, fontsize=14)
    ax[0].set_xlabel('X (pixels)', fontsize=16)
    ax[0].set_ylabel('Y (pixels)', fontsize=16)

    ax[1].plot(ap,flux)
    plt.gca().invert_yaxis()
    ax[1].set_xlabel('Aperture Size, R$_{ap}$ (pix)', fontsize=16)
    ax[1].set_ylabel('Total Flux (DN/s/pix)', fontsize=16)
    # twin object for two different y-axis on the sample plot
    ax2=ax[1].twinx()
    # make a plot with different y-axis using second axis object
    ax2.plot(ap, dflx,color="green")
    ax2.set_ylabel('dFlux/dR$_{ap}$ (DN/s/pix/pix)', fontsize=16)

#    fig.savefig(savedir+star+"_CofG2.pdf", bbox_inches='tight')

    plot2ndDeriv(ap, dflx, dap)

def plot2ndDeriv(ap, dflx, dap):

    ddflx = np.concatenate((([0]), np.diff(dflx)/dap))

    fig, axi = plt.subplots()
    axi.plot(ap,dflx,color="green")
    axi.set_xlabel('Aperture Size, R$_{ap}$ (pix)', fontsize=16)
    axi.set_ylabel('dFlux/dR$_{ap}$ (DN/s/pix/pix)', fontsize=16)
    axi2=axi.twinx()
    axi2.plot(ap,ddflx,color="red")
    axi2.set_ylabel('d$^2$Flux/dR$_{ap}^2$ (DN/s/pix/pix$^2$)', fontsize=16)



def produceCofG(orb,star,flagthresh):

    ######################
    # Read in HI-1A data #
    ######################

#    basedir   = "/Users/pwilliams/Documents/Research/"
    basedir = os.getcwd()

    # Stamp dimensions, timestamp, input pixel stamp
    sXdim, sYdim, tx, stampin = readSTEREO(basedir, orb, star)

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

    minRad = 0
    maxRad = 5.0

    # Select image data at point halfway along lightcurve
    # (ie, star near center of HI-1A image)
    i = round(len(tx)/2)

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


    # Set up blank HI-1A flux and background flux arrays
    flux = []

    for iRad in range(int(minRad*10),int(maxRad*10)+1,1):
#    for iRad in range(int(apRad*10),int(apRad*10)+1,1):


        apRad = iRad/10  # Current aperture radius

        #############################################
        # Collect the flux from within the aperture #
        #############################################

        sig, _, _, uninrdat = collectFlux(apRad, Rmat2, gdXsz, gdYsz, datfld, flagthresh)

        # Divide by number of sub-pixels per pixel
        sig = sig*stsz*stsz

        flux.append(sig)      # Append flux data array

    # Save aperture image data at point halfway along lightcurve
    halfwayterms = [XCMsub, YCMsub, datfld, uninrdat]

   # Plot aperture image + lightcurve #
    plotCofG(halfwayterms, flux)

    plt.show()
    quit()
