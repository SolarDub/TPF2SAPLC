:construction_worker: WORK IN PROGRESS :construction_worker:

# TPF2SAPLC #
These application will develop stellar photometric time-series (i.e. 'lightcurves') from previously constructed STEREO HI-1A Target Pixel File (TPF) images using Simple Aperture Photometry (SAP) methods.

## Requirements

Currently, this application has been written only for Mac-OS.

This application will work with Python 3.7 or later.

This application is currently a demonstration version. It is hard-coded to read sample TPFs from a directory located in this current working directory.

Codes called in this application can be found their respective src directories:

```
./src/Bash
./src/Python
```

## Help scripts

To access the help file, which lists the usable switches, at the terminal prompt, type:

    $ ./runCreateSAPLC.sh --help

or simply:

    $ ./runCreateSAPLC.sh

----

## Observations

Each star is observed for ~18 days once each orbit of the STEREO spacecraft around the Sun. An orbit starts and end on the center of the HI-1A camera passing the celestial Right Ascension 0 hour meridian. The yearly observations for every star are categorized in orbit numbers, which correspond to the time range within with the star was observed.

To see the orbit numbers to the corresponding observation time range, enter:

    $ ./runCreateSAPLC.sh --ohelp

Note, only TPFs for Orbit 10 are currently available.

For Orbit 10, entering the above command yields:

```
Or Start Date/Time     End Date / Time
...
10 2015 09 27 21 47 25 2016 09 06 09 43 58
...
```

This described Orbit 10 beginning on September 27 2015 at 21:47:25 UTC and ending on September 9 2016 at 09:48:58 UTC, at which point Orbit 11 begins.

So an observation of 12 Sgr from June 5 2016 at 02:09:01 UTC until June 23 2016 at 13:29:01 UTC falls within the bounds of Orbit 10.

----

## Producing SAP Lightcurves

A star's photometric time-series (lightcurves) is produced from images located in its respective TPF, created by the createTPFs application. A list of ready-made TPFs can be found in the TPFs directory:

    $ ls -al TPFs

The filenames contain the star names without spaces, i.e. 12 Sgr -> 12Sgr.

To produce a selected star's SAP lightcurve from its TPF, one may proceed in one of two ways. You may quit the program by entering 0 into any of the following prompts.


#### Enter the details into prompt boxes

- At the terminal prompt, enter

    $ ./runCreateSAPLC.sh -s

- A prompt box will appear requesting the entry of a single star name. Try 12 Sgr by entering:

    `12Sgr`
    
- The next prompt will appear requesting the entry of the aperture size, in pixels, to be using in the SAP process. Try 3.2 pixels by entering:

    `3.2`
    
- You may wish to see the effects of varying the size by trying a different value (up to 4.5 pixels).
- The next prompt will appear requesting the entry of the orbit number of the star's TPF to be used. The only orbit currently available is Orbit 10, so enter:

    `10`


#### Using data within a prepared text file

- Open "OneStar.txt" in ./StarLists
- Change the starname (first column) to the one you require (e.g. 12Sgr).
- Leave the aperture pixel size (second column) as-is, i.e. 3.2
  - or you can see the effects of varying the size by changing its value (up to 4.5).
- At the terminal prompt, type:

    $ ./runCreateSAPLC.sh -t

- A prompt will appear requesting the entry of the orbit number of the star's TPF to be used. The only orbit currently available is Orbit 10, so enter:

    `10`

----

The displayed lightcurve is derived from a simple sampling of the target pixel image array, and may including noise, trends, spikes, etc. The movie shown below illustrates the lightcurve production pipeline of:

    `STEREO HI-1A image -> target pixel images -> lightcurve`

for the Cepheid star 12 Sgr.

Note the two downward spikes, one due to the star's image x-position coinciding with that of the bloomed CCD columns of the Earth (near 7522 days), the second due to Mars (near 7562 days). For other examples, the plot scaling may be influenced by these spikes, so one may have to zoom in to observe the lightcurve.

These artifacts can be reduced and the lightcurve analysed in both the time- and frequency-domains using sample codes that have been included in the 'classes' directory of this repository:

    $ ls -al classes

----

https://user-images.githubusercontent.com/81772405/196067242-d9a88692-9f2e-430d-a35f-628e80ae2313.mp4

----

## Auxillary scripts

A 'Curve of Growth' that illustrates how total stellar flux varies with aperture size can be used to select an aperture size to use with the SAP process.

To produce a such a Curve of Growth, add the switch -c to the executable command.

If using the star list to input the star name, enter:

    $ ./runCreateSAPLC.sh -c

or if entering the star name via the prompt, enter:

    $ ./runCreateSAPLC.sh -c -s

The resulting plot includes:
- the total flux, which increases with aperture size (blue curve).
- the first derivative (green curve) shows:
  - an increase - more and more flux is being collected from the star's profile as the aperture increases in size,
  - a decrease - the aperture increases in size, by the star's profile drops off,
  - a minumum - the aperture continues to increase and eventually starts collecting flux surrounding the target.

![12Sgr_CofG](https://user-images.githubusercontent.com/81772405/196067826-26f62e58-0f45-48fa-8a29-0ea6aa188cfb.jpg)

