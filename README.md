:construction_worker: WORK IN PROGRESS :construction_worker:

# TPF2SAPLC #
These application will develop stellar photometric time-series (i.e. 'lightcurves') from previously constructed STEREO HI-1A Target Pixel File (TPF) images using Simple Aperture Photometry (SAP) methods.

## Requirements

Currently, this application has been written only for Mac-OS.

This application will work with Python 3.7 or later.

This application is currently a demonstration version. It is hard-coded to read sample TPFs from a directory located in this current working directory.

## Help scripts

To access the help file, which lists the usable switches, at the terminal prompt, type

    $ ./runCreateSAPLC.sh --help

or simply

    $ ./runCreateSAPLC.sh

----

## Producing SAP Lightcurves

A star's photometric time-series (lightcurves) is produced from images located in its respective TPF, created by the createTPFs application. A list of ready-made TPFs can be found in the TPFs directory:

    $ ls -al TPFs/

The filenames contain the star names without spaces, i.e. 12 Sgr -> 12Sgr.

To produce a selected star's SAP lightcurve from its TPF, one may proceed in one of two ways.

##### Enter the details into prompt boxes

- At the terminal prompt, enter

    $ ./runCreateSAPLC.sh -s

- A prompt box will appear requesting the entry of a single star name. Try 12 Sgr by typing:

    `12Sgr`
    
- The next prompt will appear requesting the entry of the aperture size, in pixels, to be using in the SAP process. Try 3.2 pixels by typing:

    `3.2`
    
- You may wish to see the effects of varying the size by trying a different value (up to 4.5 pixels).

##### Using data within a prepared text file

- Open "OneStar.txt" in ./StarLists
- Change the starname (first column) to the one you require (e.g. 12Sgr).
- Leave the aperture pixel size (second column) as-is, i.e. 3.2
  - or you can see the effects of varying the size by changing its value (up to 4.5).
- Then at the terminal prompt, type:

    $ ./runCreateSAPLC.sh -t

A prompt to enter the orbit number of interest will subsequently appear:
- The only orbit currently available is Orbit 10
- To see the orbit numbers with the corresponding observation time range, enter:
  - "./runCreateSAPLC.sh --ohelp" 

You may quit the program by entering 0 into any of the above prompts.

----

The lightcurve produced is a simple sampling of the target pixel image array, including noise, trends, spikes, etc. The movie shown below illustrates the production line of HI-1A image -> target pixel images -> lightcurve for the Cepheid star 12 Sgr. Note the two downward spikes, one due to the star's image x-position coinciding with that of the bloomed CCD columns of the Earth (near 7522 days), the second due to Mars (near 7562 days). For other examples, the plot scaling may be influenced by these spikes, so one may have to zoom in to observe the lightcurve.

These artifacts are reduced and the lightcurve analysed in both the time- and frequency-domains using subsequent codes. A sample of these codes are archived in the classes directory of this repository.

https://user-images.githubusercontent.com/81772405/196067242-d9a88692-9f2e-430d-a35f-628e80ae2313.mp4

----

To produce a 'Curve of Growth', to see how total stellar flux varies with aperture size, add the switch -c to the executable command, i.e.:
- Type "./runCreateSAPLC.sh -c", or
- Type "./runCreateSAPLC.sh -c -s" if you also wish to enter the name of the star into the prompt 

Note:
- the total flux increases with aperture size (blue curve).
- the first derivative (green curve) shows:
  - an increase - more and more flux is being collected from the star's profile as the aperture increases in size
  - a decrease - the aperture increases in size, by the star's profile drops off
  - a minumum - the aperture continues to increase and eventually starts collecting flux surrounding the target

![12Sgr_CofG](https://user-images.githubusercontent.com/81772405/196067826-26f62e58-0f45-48fa-8a29-0ea6aa188cfb.jpg)

