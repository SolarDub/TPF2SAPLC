import matplotlib
import matplotlib.pyplot as plt
from scipy import signal
import math as m
import numpy as np
import statistics as stats


#
#   Set up a base class for a lightcurve
#
class LightCurve(object):
    # Set up instance
    def __init__(self, time, data):

        if len(time) == len(data):
            self.time = time
            self.data = data
        else:
            print('Time and data arrays have different lengths.')
            print('Program terminated.')

    # Smooth light curve using low-pass filter
    def smoothFilter(self, width):
        time = self.time
        flux = self.data
        fs=36/24/3600 # sampl frq 36 img per day in Hz
        nyquist = fs / 2 # half the sampling frequency (18 c/d)
        cutoff = 1/(width*nyquist*3600)
        print('width= ',1/(cutoff*nyquist*3600),' hours') #cutoff = 24 hours

        # Butterworth filter (order 5)
        b, a = signal.butter(5, cutoff, btype='lowpass') #low pass filter

        fluxfilt = signal.filtfilt(b, a, flux)
        fluxfilt = np.array(fluxfilt)
        fluxfilt = fluxfilt.transpose()

        return fluxfilt

    # Smooth light curve using low-pass filter
    def produceResiduals(self,width):
        time = self.time
        flux = self.data

        flx = LightCurve(time,flux)

        res = flux-flx.smoothFilter(width)

        stdv = stats.stdev(res)
        meanres = np.mean(res[res < stdv])

        res2 = res-meanres

        return res2

    # Upper and lower bounds using interquartile range
    def iqrBounds(self):
        data=self.data
        q1, q3= np.percentile(data,[25,75])
        iqr = q3 - q1
        upper = q3+1.5*iqr
        lower = q1-1.5*iqr

        # Indices of residual values to keep
        indkeep = ~((data < lower) | (data > upper))

        return upper, lower, indkeep


    # Plot LightCurve
    def plotLightCurve(self,mkln='' \
                           ,xlm=[],xtks=[],xlbl='' \
                           ,ylm=[],ytks=[],ylbl='' \
                           ,file="" \
                           ):

        time = self.time
        data = self.data
        fig, ax = plt.subplots()
        ax.plot(time,data,mkln)
        
        if len(xlm) == 2:
            ax.set_xlim(xlm)
        if len(xtks) > 0:
            xtckstr=list(map(str,xtks))
            ax.set_xticks(xtks)
            ax.set_xticklabels(xtckstr)
            ax.set_xticklabels(xtckstr, fontsize=14)
        if xlbl != '':
            ax.set_xlabel(xlbl, fontsize=16)

        if len(ylm) == 2:
            ax.set_ylim(ylm)
        if len(ytks) > 0:
            ytckstr=list(map(str,ytks))
            ax.set_yticks(ytks)
            ax.set_yticklabels(ytckstr)
            ax.set_yticklabels(ytckstr, fontsize=14)
        if ylbl != '':
            ax.set_ylabel(ylbl, fontsize=16)

        if file != "":
            fig.savefig(file, bbox_inches='tight')

        return ax


    def polFit(self,order):

        time = self.time
        data = self.data

        z = np.polyfit(time - time[0], data, order)
        pf = np.poly1d(z)
        pfit = pf(time - time[0])

        return pf, pfit

    def subFit(self,pf):

        time = self.time
        data = self.data

        pfit = pf(time - time[0])

        subdat = data - pfit

        return subdat

    # Remove polynomial trend
#    def removeTrend(self, order):
#        tme = self.time
#        d = self.data
#        t = tme - tme[0]
#        z = np.polyfit(t, d, order)
#        pf = np.poly1d(z)
#        pfit = pf(t)
#        f_cl_rt = f_cl - pfit
#        pfitr = pf(t)
        
#        r_cl_rt = r_cl - pfitr      # Removed data points

        


