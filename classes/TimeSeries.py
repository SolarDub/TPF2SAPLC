import math as m
import numpy as np

import statistics as stats

import matplotlib
import matplotlib.pyplot as plt

from scipy import signal
from scipy.signal import find_peaks
from scipy import interpolate

from classes.Spectrum import *

#
#   Set up a base class for a general time-series
#
class TimeSeries(object):
    # Set up instance
    def __init__(self, time, data):

        if len(time) == len(data):
            self.time = time
            self.data = data
        else:
            print('Time and data arrays have different lengths.')
            print('Program terminated.')

            quit()

    # Upper and lower bounds using interquartile range
    def iqrBounds(self):
        x=self.data   # data

        # Determine upper and lower bounds of interquartile range
        q1, q3= np.percentile(x,[25,75])    # determine 1st and 3rd quartiles
        iqr = q3 - q1                       # interquartile range
        uif = q3+1.5*iqr                    # upper inner fence
        lif = q1-1.5*iqr                    # lower inner fence
        uof = q3+3*iqr                      # upper outer fence
        lof = q1-3*iqr                      # lower outer fence

        # Indices of residual values to keep
        indkeep = ~((x < lif) | (x > uif))

        return iqr, uif, lif, uof, lof, indkeep

    # Remove large spikes from time-series by removing data outside N-sigma from mean
    def RemoveNsigSpikes(self, N, **kwargs):
        t = self.time   # time
        x = self.data   # data

        # Select interquartile range of time-series
        _,_,_,_,_,sel = TimeSeries(t,x).iqrBounds()
        tIQR = t[sel]
        xIQR = x[sel]

        xmed1 = np.median(xIQR)
        xmed2 = np.median(x)
        xmean = np.mean(xIQR)
        xstd  = np.std(xIQR)
#        print("Time-series Median1: ", xmed1)
#        print("Time-series Median2: ", xmed2)
        print("Time-series Mean: ", xmean)

#        print("Nt-1: ",len(tx))

        # Remove large spikes from time-series by removing data outside N-sigma from mean
        while (len(x[(x-xmean)>(N*xstd)]) > 0):
#            print(len(x[(x-xmean)>(N*xstd)]),x[(x-xmean)>(N*xstd)])
            ttmp  = t[(x-xmean)<(N*xstd)]
            xtmp = x[(x-xmean)<(N*xstd)]
            t = ttmp
            x = xtmp

#        print("Number of x points beyond N-sigma from mean: ", len(x[(x-xmean)>(N*xstd)]))
#        print("Standard deviation of series, sigma: ",xstd)
#        print("5sigma point from mean: ", N*xstd)
#        print(abs(x-xmean)>(N*xstd))

        for kw in kwargs:
            if (kw == 'plot'):
                if (kwargs[kw] == 1):
                    fig, ax = plt.subplots()
                    ax.plot(t,x,'.',color="red")
                    ax.plot(tIQR,xIQR,'.',color="blue")
                    ax.plot(tIQR,xmean + np.zeros(len(xIQR)),'--',color="black")
                    ax.plot(tIQR,xmean+N*xstd + np.zeros(len(xIQR)),':',color="black")
                    ax.plot(tIQR,xmean-N*xstd + np.zeros(len(xIQR)),':',color="black")

        return t, x


    # Smooth time-series using low-pass filter
    def smoothFilter(self, width):
        t = self.time
        x = self.data
        
        fs     = 36/24/3600         # samp frq 36 img per day in Hz
        ny     = fs / 2             # eff Nyquist - half  sampling frq
        cutoff = 1/(width*ny*3600)  # cutoff frq = 24 hours
        print('width= ',1/(cutoff*nyquist*3600),' hours') 

        # Butterworth filter (order 5)
        b, a = signal.butter(5, cutoff, btype='lowpass') #low pass filter

        fluxfilt = signal.filtfilt(b, a, x)
        fluxfilt = np.array(fluxfilt)
        fluxfilt = fluxfilt.transpose()

        return fluxfilt

    # Fit polynomial to time-series
    def polynomialFit(self, order, **kwargs):
        t = self.time   # time
        x = self.data   # data
        
        z = np.polyfit(t - t[0], x, order)
        pf = np.poly1d(z)
        pfit = pf(t - t[0])

        for kw in kwargs:
            if (kw == 'plot'):
                if (kwargs[kw] == 1):
                    fig, ax = plt.subplots()
                    ax.plot(t,x,'.')
                    ax.plot(t,pfit)
                    ax.set_xlabel('Time (BJD-2454833)', fontsize=16)
                    ax.set_ylabel('Fractional Flux Deviation', fontsize=16)

        return pfit

    # Remove function 'pfit' from time-series
    def removeFit(self, pfit, **kwargs):
        t = self.time   # time
        x = self.data   # data

        xrem = np.array(x)/np.array(pfit)

        for kw in kwargs:
            if (kw == 'plot'):
                if (kwargs[kw] == 1):
                    # Plot time-series with polynomial trend
                    fig = plt.figure()
                    ax1 = fig.add_subplot(211)
                    ax1.plot(t,x,'.')
                    ax1.plot(t,pfit)
                    ax1.set_ylabel('Fractional Flux Deviation', fontsize=16)
                    # and time-series with trend removed
                    ax2 = fig.add_subplot(212)
                    ax2.plot(t,xrem,'.')
                    ax2.set_xlabel('Time (BJD-2454833)', fontsize=16)
                    ax2.set_ylabel('Fractional Flux Deviation', fontsize=16)
                    for label in (ax2.get_xticklabels() \
                                + ax2.get_yticklabels()): label.set_fontsize(14)

        return t, xrem


    # Select range start -> end of time-series, while removing any NaN values

    def selectRange(self,start,end, **kwargs):
        t = self.time   # time
        x = self.data   # data

        rnge  = ((t > start) & (t < end) & ~np.isnan(x))
        tsel = t[rnge]
        xsel = x[rnge]

        for kw in kwargs:
            if (kw == 'plot'):
                if (kwargs[kw] == 1):
                    fig, ax = plt.subplots()
                    ax.plot(tsel,xsel,'.')
                    ax.set_xlabel('Time (BJD-2454833)', fontsize=16)
                    ax.set_ylabel('Fractional Flux Deviation', fontsize=16)

        return tsel, xsel


    def rebinSeries(self,bs,cadm, **kwargs):
        t = self.time   # time
        x = self.data   # data

        cadd = cadm/(60*24)  # cadence in days
        tlen = cadd * bs     # Box length in days
        low  = t[0]          # Low limit of first box
        high = low + tlen    # High limit of first box
        tl   = []
        xl   = []
#        dffx = []
        print("HI1A cadence: ",cadd ,"    Box length: ",tlen)
        
        ichk = 0
        while (high < t[len(t)-1]):
            ichk = ichk+1
            vals = x[(t>=low) & (t<high)]
            if (len(vals) == 0):
                xav = 0
            else:
                xav = np.sum(vals)/len(vals)        

            tl.append(low);  xl.append(xav)
            tl.append(high); xl.append(xav)
#            dffx.append(vals.tolist())
            low  = high          # New low limit of next time box
            high = low + tlen    # New high limit of next time box

        high = t[len(t)-1]
        vals = x[(t>=low)]
        xav  = np.sum(vals)/len(vals)        
        tl.append(low);  xl.append(xav)
        tl.append(high); xl.append(xav)

#       dffx.append(vals.tolist())
#       flatdffx = [item for sublist in dffx for item in sublist]
#       print(len(txk2),len(vals),ichk,len(dffx),len(flatdffx),len(txtl))

        for kw in kwargs:
            if (kw == 'plot'):
                if (kwargs[kw] == 1):
                    fig, ax = plt.subplots()
                    ax.plot(t,x,'-',color="red")
                    ax.plot(tl,xl,'-',color="blue")
                    ax.set_xlabel('Time (BJD-2454833)', fontsize=16)
                    ax.set_ylabel('Fractional Flux Deviation', fontsize=16)
                    for label in (ax.get_xticklabels() \
                                + ax.get_yticklabels()): label.set_fontsize(14)

#                    fig, ax = plt.subplots()
#                    ax.plot(txk2,fluxz-np.array(flatdffx),'-',color="red")
        
    # Produce auto-correlation function of time-series
    def ACF(self,span, **kwargs):
        t = self.time   # time
        x = self.data   # data

        # Correlate first 'span' elements with 'span' elements offset by i
        # Select [0,1] element from correlation matrix
        # Perform until last element of offset span is the last element of
        # the input array
        # First element of ACF=1 is time-series auto-correlated with zero offset
        acorr = np.array([1]+[np.corrcoef(x[0:span], x[i:i+span])[0,1]  \
                for i in range(1, len(x)-span)])

        for kw in kwargs:
            if (kw == 'plot'):
                if (kwargs[kw] == 1):
                    fig, ax = plt.subplots()
                    ax.plot(t[0:len(x)-span]-t[0],acorr,'.',color="blue")
                    ax.set_title("Time-series Auto-Correlation Function")
                    ax.set_xlabel('Lag time (Days)', fontsize=16)
                    ax.set_ylabel('Pearson Coefficient', fontsize=16)
                    for label in (ax.get_xticklabels() \
                                + ax.get_yticklabels()): label.set_fontsize(14)



    # Produce Lomb-Scargle Periodogram
    def periodLS(self, name):

        def timeInfo(t):
            
            dt   = min(np.diff(t))  # Minimum (nominal) time spacing
            
            print('')
            print(f'Dataset name: {name}')
            print(f'First time stamp: {t[0]}')
            print(f'Last time stamp: {t[-1]}')
            print(f'Length of time-series: {t[-1] - t[0]}')
            print(f'Time spacing (days): {dt}')
            print(f'Time spacing (mins): {dt*24*60}')
            print(f'Number of time-series data points: {len(t)}')
            print('')

        def defineFreq(t, ovsmp):

            Lt = t[-1] - t[0]
            # Frequency spacing
            df   = 1*(m.pow(10,m.floor(m.log10(1/(ovsmp*Lt)))))
            # Effective Nyquist frequency
            Nyfq = int(m.floor(0.5/min(np.diff(t))))
            # Number of frequencies
            Nmfq = Nyfq/df
            # Frequency array
            f = np.arange(df,Nyfq+df,df)

            print("Frequency spacing (cycles per day): ",df)
            print("Nyquist frequency c/d): ", Nyfq)
            print(f[-1])
            print("Number of frequencies: ", Nmfq)

            return f, df

        def calcFAP(t,x,f):

            # Angular frequency array as input to Lomb-Scargle
            w = 2*m.pi*f

            # Calculate Lomb-Scargle power
            Pxx  = np.array(signal.lombscargle(t-t[0], x, w, normalize=True))

            fig, ax = plt.subplots()
            ax.plot(f,Pxx)
            fig, ax = plt.subplots()
            ax.plot(f,1-Pxx)

            M    = np.floor((t[-1]-t[0])*f[-1]);
            fig, ax = plt.subplots()
            ax.plot(f,np.log10((1-Pxx)**M))


#            FAPs = M*np.exp(-Pxx)
#            FAPs = 1 - (1 - np.exp(-Pxx))**M
            FAPs = 1 - (1 - Pxx)**M
#            inds = (FAPs > 0.00001)
#            FAPs[inds] = 1-(1-np.exp(Pxx[inds]))**M
#            logFAPs = np.log10(FAPs)
#            inds2 = (FAPs < 10**-300)
#            logFAPs = np.round(np.log10(M)-Pxx[inds2]*np.log10(np.exp(1)))

            fig, ax = plt.subplots()
            ax.plot(f,FAPs)
            
            
        t = self.time   # time
        x = self.data   # data

        timeInfo(t)

        ovsmp = 5          # Oversampling factor (normally 5)

        # Define frequency array
        f, df = defineFreq(t, ovsmp)

        # Calculate False-Alarm Probabilities
#        calcFAP(t,x,f)

        # Angular frequency array as input to Lomb-Scargle
        w = 2*m.pi*f

        # Calculate Lomb-Scargle power
        P = signal.lombscargle(t-t[0], x, w)
        # Calculate Lomb-Scargle amplitudes    
        A = Spectrum(f,P).pow2amp()

        # Calulate mean noise level within lower & upper limits
        noise = Spectrum(f,A).noiseLevel(5, 15)
        print(f'Noise level: {noise}')
#        print(f'Noise level (ppt): {noise*1000}')

        fPeak, APeak = Spectrum(f,A).maxPeak()
        print(f'Peak frequency: {fPeak}')
        print(f'Peak period:    {1/fPeak}')
        print(f'Peak amplitude:    {APeak}')

        # Factor by which to interpolate
        fac = 0.1

        fpt, Apt = Spectrum(f,A).specInterp(df, fac)

        fPeak2, APeak2 = Spectrum(fpt,Apt).maxPeak()
        print(f'Peak frequency: {fPeak2}')
        print(f'Peak period:    {1/fPeak2}')
        print(f'Peak amplitude:    {APeak2}')

        fpsrt2, Apsrt2 = Spectrum(fpt,Apt).getPeaks()

        return f, A, noise, fPeak

    def phaseFold(self, P):
        t = self.time   # time
        x = self.data   # data

        axvalsz = 14
        axlabsz = 16

        tz = t - t[0]
        frac  = t/P

        phi = (frac)-np.floor(frac)

        phi2  = np.concatenate((phi, 1+phi.T))
        x2    = np.concatenate((x, x.T))

        return phi2, x2

    # Smooth time-series using low-pass filter
    def produceResiduals(self,width):
        t = self.time   # time
        x = self.data   # data

        res = x-TimeSeries(t,flux).smoothFilter(width)

        stdv = stats.stdev(res)
        meanres = np.mean(res[res < stdv])

        res2 = res-meanres

        return res2

    # Write time-series to two-column (time, data) text file
    def write2text(self,file):
        t = self.time   # time
        x = self.data   # data

        with open(file, "w+") as h:
            for i in range(0, len(t)-1, 1):
                q = ",".join(map(str, [t[i], x[i]]))
                h.write(q +"\n")



    # Plot time-series
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

