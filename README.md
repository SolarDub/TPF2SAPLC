# TPF2SAPLC
Develop stellar photometric time-series (i.e. 'lightcurves') from previously constructed STEREO HI-1A Target Pixel Images using Simple Aperture Photometry (SAP) methods.

For Mac-OS only.

To execute:
- Open Terminal.
- Change directory to the 'base directory' where 'ReadStarFileScript' resides.
- Type "./ReadStarFileScript", with optional switches
  - These options may be reviewed by entering "./ReadStarFileScript --help".

----

Sample Target Pixel Files (TPFs), created by the createTPFs program, are situated in "TPFs" directory. The filename contains the star name without spaces, i.e. 12 Sgr -> 12Sgr.

To produce a chosen star's SAP lightcurve from its TPF, either:
- To enter the name of the star into the prompt, type:
  - "./ReadStarFileScript -s"
- A prompt will follow requesting the aperture size in pixel
  - 3.2 is recommended or you can see the effects of varying the size by selecting a different value (up to 4.5).

or

- Access "OneStar.txt" in ./StarLists
- Change the starname (first column) to the one you require (e.g. 12Sgr).
- Leave the aperture pixel size (second column) as-is, i.e. 3.2
  - or you can see the effects of varying the size by changing its value (up to 4.5).
- Then type:
  - "./ReadStarFileScript" 

A prompt to enter the orbit number of interest will subsequently appear:
- The only orbit currently available is Orbit 10
- To see the orbit numbers with the corresponding observation time range, enter:
  - "./ReadStarFileScript --ohelp" 

You may quit the program by entering 0 into any of the above prompts.

----

The lightcurve produced is a simple sampling of the target pixel image array, including noise, trends, spikes, etc. The movie shown below illustrates the production line of HI-1A image -> target pixel images -> lightcurve for the Cepheid star 12 Sgr. Not the two downward spikes, one due to the star's image x-position coinciding with that of the bloomed CCD columns of the Earth (near 7522 days), the second due to Mars (near 7562 days). For other examples, the plot scaling may be influenced by these spikes, so one may have to zoom in to observe the lightcurve.

These artifacts are reduced and the lightcurve analysed in both the time- and frequency-domains using subsequent codes. A sample of these codes are archived in the classes directory of this repository.

https://user-images.githubusercontent.com/81772405/196067242-d9a88692-9f2e-430d-a35f-628e80ae2313.mp4

----

To produce a 'Curve of Growth', to see how total stellar flux varies with aperture size, add the switch -c to the executable command, i.e.:
- Type "./ReadStarFileScript -c", or
- Type "./ReadStarFileScript -c -s" if you also wish to enter the name of the star into the prompt 

Note:
- the total flux increases with aperture size (blue curve).
- the first derivative (green curve) shows:
  - an increase - more and more flux is being collected from the star's profile as the aperture increases in size
  - a decrease - the aperture increases in size, by the star's profile drops off
  - a minumum - the aperture continues to increase and eventually starts collecting flux surrounding the target

![12Sgr_CofG](https://user-images.githubusercontent.com/81772405/196067826-26f62e58-0f45-48fa-8a29-0ea6aa188cfb.jpg)

