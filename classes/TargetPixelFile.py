import os
import sys

import math as m
import numpy as np

import statistics as stats

import matplotlib
import matplotlib.pyplot as plt

import fitsio
from fitsio import FITS,FITSHDR

# Function to read HI-1A TPF times and stamps
def readSTEREO(basedir, orb,star):

    savedir   = basedir+"stereo/StellarData/"+star+"/"
    multidir  = savedir+"Multi/"

    if os.path.isdir(multidir) == False:
        os.mkdir(multidir)

    pref = "STEREO_HI-1A"
    ext  = "fits"

    filenm    = pref + "_r" + f'{orb:02d}' + "_" + star + "." + ext
    file_name = savedir + 'TPFs/' + filenm

    fits = fitsio.FITS(file_name)

    h0   = fits[0].read_header()
    h1   = fits[1].read_header()

    # HI-1A TPF image dimensions
    img_dim = h1['TDIM2']
    sXdim   = int(img_dim[1:3])
    sYdim   = int(img_dim[4:6])

    # Read HI-1A times into tuple
    t = fits[1].read(columns=['TIME'])

    # unpack tuples into an array object
    tx=np.zeros(len(t))
    for i in range(len(t)):
        tx[i]=float(*t[i])

    # Read in image stamp data
    stamp=fits[1].read(columns=['IMAGE'])

    return sXdim, sYdim, tx, stamp


def subpixelGrid(sXdim, sYdim, stsz):

    gdXsz  = int(sXdim/stsz)   # Grid x-dimension
    gdYsz  = int(sYdim/stsz)   # Grid y-dimension

    x      = np.linspace(-sXdim/2.0,sXdim/2.0-stsz,gdXsz)  
    y      = np.linspace(-sYdim/2.0,sYdim/2.0-stsz,gdYsz)
    xv, yv = np.meshgrid(x, y)

    return xv, yv

def subpixelDataField(stamp, stsz, gdXsz):

    lstarr = []   # Set up blank list array to construct sub-pixel datafield

    # Loop through stamp columns and repeat values
    #  by number of sub-pixels per pixel
    # Append onto current list array
    for ip in range(gdXsz):
        lst = np.repeat(stamp[m.floor(ip*stsz),:],int(1/stsz))
        lstarr.append(lst)
        
    datfld = (np.array(lstarr))

    return datfld

def initialFluxCentroid(sXdim, sYdim, stamp):

    mxp  = 1        # Use pixel square around target image center
    pxhw = 0.5      # Half a pixel width

    datsbvT = stamp[int(sXdim/2-mxp):int(sXdim/2+mxp+1), \
                    int(sYdim/2-mxp):int(sYdim/2+mxp+1)]
    datsbv  = datsbvT

    Dim = np.shape(datsbv)
    xD  = Dim[0]
    yD  = Dim[1]

    xm = np.linspace(-mxp,mxp,xD)
    ym = np.linspace(-mxp,mxp,yD)
    
    xmv, ymv = np.meshgrid(xm, ym)
    
    XCMsub = np.sum(datsbv*xmv)/np.sum(datsbv) 
    YCMsub = np.sum(datsbv*ymv)/np.sum(datsbv)

    return XCMsub, YCMsub

def FluxCentroid(apRadCent, xv, yv, XCMsub, YCMsub, gdXsz,gdYsz, datfld):

    # Initialise percent difference between previous and current flux centroid positions
    XCMdiff = 100
    YCMdiff = 100

    # Repeat estimation of centroid coordinates until both differences
    # between previous and current positions differ by less than 1%
    while(XCMdiff > 1 or YCMdiff > 1):

        # Sub-pixel distance from current centoid position
        Rmat2 = np.sqrt((xv-XCMsub)*(xv-XCMsub) \
                      + (yv-YCMsub)*(yv-YCMsub))

        # Create an aperture mask around the current position
        mask = 1 + np.zeros((gdXsz,gdYsz))
        mask[Rmat2 > apRadCent] = 0

        # Mask over datafield
        mskddat = mask*datfld

        # Use this masked field to define new centroid position
        XCMsub2 = np.sum(mskddat*xv)/np.sum(mskddat)
        YCMsub2 = np.sum(mskddat*yv)/np.sum(mskddat)

        # Compared previous and current positions
        XCMdiff = 100*2*abs((XCMsub-XCMsub2)/(XCMsub+XCMsub2))
        YCMdiff = 100*2*abs((YCMsub-YCMsub2)/(YCMsub+YCMsub2))

        # Replace previous with current
        XCMsub = XCMsub2
        YCMsub = YCMsub2

    return XCMsub, YCMsub

def collectFlux(apRad, Rmat2, gdXsz,gdYsz, datfld, flagthresh):

    # Create an aperture mask around this centroid 
    mask                = 1 + np.zeros((gdXsz,gdYsz))
    mask[Rmat2 > apRad] = 0
    # Calculate number of pixels within aperture
    Nsigp = np.sum(mask)

    mskddat = mask*datfld          # Mask out datafield keeping only values within aperture
    mskddat = mskddat[mskddat > 0] # Ignore any zero values from datafield

    # Sum the values within the aperture
    # This is the signal for this time-stamp
    sig = np.sum(mskddat)

    # Bad pixels are flagged 1e-17.
    # If near the aperture center they will affect the signal,
    # so this signal will be nulled.
    # flagthresh determines how near to aperture center to check for bad pixels
    # The flux for this time-stamp set to zero and eventually voided.

    # Set up mask around centroid, mask out datafield
    # and find unique values within
    nrmask              = 1 + np.zeros((gdXsz,gdYsz))
    nrmask[Rmat2 > flagthresh] = 0    # Seems 1.5 is too harsh for some stars
    nrmaskdat           = nrmask*datfld
    nrmaskdat           = nrmaskdat[nrmaskdat > 0]
    uninrdat            = np.unique(np.array(nrmaskdat))

    # Look for null (=1e-17) values
    flagval = 0
    if(len(uninrdat[uninrdat <= 1E-17]) > 0 ):
        flagval = 1

    return sig, flagval, Nsigp, uninrdat

def sampleBackground(gdXsz,gdYsz,Rmat2,annrad,annwid,datfld):

    # Set up annulus mask
    annmask = 1 + np.zeros((gdXsz,gdYsz))
    annmask[(Rmat2 < annrad) & (Rmat2 > annrad+annwid)] = 0

    # Mask out datafield values outside annulus
    allvals = annmask*datfld

    # Consider unique values inside annulus
    alluniq = np.unique(np.array(allvals[allvals != 0]))

    # Calculate lower and upper quartile points of annulus data
    Q1, Q3 = np.percentile(alluniq,[25,75])

    # Determine interquartile range
    IQR = Q3 - Q1

    # Select values within interquartile range
    selvals = alluniq[~((alluniq < (Q1-1.5*IQR)) | (alluniq > (Q3+1.5*IQR)))]

    # Calculate the mean & variance of these selected values
    bkval = np.mean(selvals)
    bkvar = np.var(selvals)
    bknum = len(selvals.flatten())

    # Calculate sky noise error
    bkerr = np.sqrt(bkvar + bkvar/bknum)

    return bkval, bkerr
        

def plotTPFplusLC(apRad, annrad, annwid, stsz, halfwayterms, tx, flux):

    XCMsub = halfwayterms[0]
    YCMsub = halfwayterms[1]
    datfld = halfwayterms[2]
    uninrdat = halfwayterms[3]

    bpxc = 100           # center coordinate of brightest target pixel

    # Set up aperture and annulus for plotting purposes
    angle    = np.linspace(0,2*np.pi*(199./200.),200)  # 0-2pi anugular space
    xcircAp  = (apRad/stsz) * np.cos(angle)
    ycircAp  = (apRad/stsz) * np.sin(angle)
    xcircAnI = (annrad/stsz) * np.cos(angle)
    ycircAnI = (annrad/stsz) * np.sin(angle)
    xcircAnO = ((annwid+annrad)/stsz) * np.cos(angle)
    ycircAnO = ((annwid+annrad)/stsz) * np.sin(angle)

#    print("Center of flux offset from image center (x,y): ",XCMsub, YCMsub)

    fig, ax = plt.subplots(1,2, gridspec_kw={'width_ratios': [1, 3]},figsize=(12,6))

    # Plot TPF image stamp
    ax[0].imshow(np.flipud(datfld) \
                ,extent=[-10,10,-10,10] \
                ,cmap=plt.get_cmap('pink')\
                ,vmin=min(uninrdat) \
                ,vmax=max(uninrdat))
    plt.gca().invert_yaxis()
    ax[0].plot(bpxc/10+XCMsub-10,bpxc/10+YCMsub-10,'.',color='green')
    ax[0].plot(bpxc/10+XCMsub+xcircAp/10-10,bpxc/10+YCMsub+ycircAp/10-10,'--',color='red')
    ax[0].plot(bpxc/10+XCMsub+xcircAnI/10-10,bpxc/10+YCMsub+ycircAnI/10-10,':',color='orange')
    ax[0].plot(bpxc/10+XCMsub+xcircAnO/10-10,bpxc/10+YCMsub+ycircAnO/10-10,':',color='orange')
    x_label_list = ['-10', '-5', '0', '5', '10']
    ax[0].set_xticks([-10,-5,0,5,10])
    ax[0].set_xticklabels(x_label_list, fontsize=14)
    y_label_list = ['-10', '-5', '0', '5', '10']
    ax[0].set_yticks([-10,-5,0,5,10])
    ax[0].set_yticklabels(y_label_list, fontsize=14)
    ax[0].set_xlabel('X (pixels)', fontsize=16)
    ax[0].set_ylabel('Y (pixels)', fontsize=16)

    meanflux = np.median(flux)

    if (max(flux)-meanflux) < (meanflux-min(flux)):
        ylmu = max(flux)+1
        ylml = 2.2*meanflux-max(flux)-1
    else:
        ylmu = 2.2*meanflux-min(flux)+1
        ylml = min(flux)-1

    # Plot full time-series
    ax[1].plot(tx,flux,'.')
    ax[1].set_xlim(min(tx),max(tx))
    ax[1].set_xlabel('Time (BJD-2450000)')
    ax[1].set_ylim(ylmu,ylml)
    ax[1].set_ylabel('Flux (DN/s/pixel)')
    plt.gca().invert_yaxis()

