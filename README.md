# TPF2SAPLC
Develop stellar photometric time-series (i.e. 'lightcurves') from previously constructed STEREO HI-1A Target Pixel Images using Simple Aperture Photometry (SAP) methods.

For MAC-OS only.

To execute:
- Open Terminal
- Change directory to the 'base directory' where 'ReadStarFileScript' exists.
- Type "./ReadStarFileScript" 

Sample Target Pixel Files (TPFs), created by createTPFs, are situated in /TPFs
The filename contains the star name without spaces, i.e. 12 Sgr -> 12Sgr

To produce a chosen star's SAP lightcurve from its TPF:
- Access "OneStar.txt" in ./StarLists
- Change the starname (first column) to the one you require (e.g. 12Sgr).
- Leave the aperture pixel size (second column) as-is, i.e. 3.2
- - or you can see the effects of varying the size by changing its value.

I will be adding methods to use dialog boxes to select star and aperture size in the future.


To produce a 'Curve of Growth', to see how total stellar flux varies with aperture size:
- Open "ReadStarFileScript"
- Change CofG value to 1
- Save and execute

Note:
- the total flux increases with aperture size (blue curve).
- the first derivative (green curve) shows:
- - an increase - more and more flux is being collected from the star's profile as the aperture increases in size
- - a decrease - the aperture increases in size, by the star's profile drops off
- - a minumum - the aperture continues to increase and eventually starts collecting flux surrounding the target
