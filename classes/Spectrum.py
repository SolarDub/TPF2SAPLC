import math as m
import numpy as np

import statistics as stats

import matplotlib
import matplotlib.pyplot as plt

from scipy import signal
from scipy.signal import find_peaks
from scipy import interpolate

#
#   Set up a base class for a time-series
#
class Spectrum(object):
    
    # Set up instance
    def __init__(self, freq, spec):

        if len(freq) == len(spec):
            self.freq = freq
            self.spec = spec
        else:
            print('Frequency and spectrum arrays have different lengths.')
            print('Program terminated.')

            quit()

    def pow2amp(self):

        P = self.spec
        
        return np.sqrt(4*P/len(P))

    def noiseLevel(self, fl, fh):

        f = self.freq
        s = self.spec
        
        return np.mean(s[(f > fl) & (f < fh)])

    def maxPeak(self):

        f = self.freq
        s = self.spec

        smax = max(s)

        return f[s == smax], smax

    def getPeaks(self):

        f = self.freq
        s = self.spec

        peaks, _ = find_peaks(s, height=0.00001)

        sp = s[peaks].tolist()
        fp = f[peaks].tolist()

        # Sort spectral peaks highest to lowest
        spsrt = list(reversed(sorted(sp)))

        # Corresponding frequencies
        fpsrt = [i for (j,i) in reversed(sorted(zip(sp,fp)))]

        return fpsrt, spsrt

    def specInterp(self, df, fac):

        f = self.freq
        s = self.spec

        df2 = df*fac
        fpt = np.arange(df2, f[-1]+df2 ,df2)
        q   = interpolate.InterpolatedUnivariateSpline(f, s)
        spt = q(fpt)

        return fpt, spt

    # Write spectrum to two-column (freq, spec) text file
    def write2text(self,file):
        f = self.freq   # frequency
        s = self.spec   # spectrum

        with open(file, "w+") as h:
            for i in range(0, len(f)-1, 1):
                q = ",".join(map(str, [f[i], s[i]]))
                h.write(q +"\n")

