#!/usr/bin/python

"""
Tide Graph
This is a python controller for the tide component of the Weahter Kiosk that will run on
a Raspberry Pi driving an old discarded 4:5 monitor that will display current and near term
weather info on the wall outside the Harbor Master's Office.  It will draw upon the latest
NOAA data rather than run a naive delayed clock.

MOD: After a fair amount of experimentation I have decided to call this routine using a crontab.
The reason for this has to do with some interesting long term limitations with the RaspPi model
I am using which seems to corrupt its memory if I leave this program running. (Memory Leak?)
The solution for this given my degree of interest is to simply shut down the program and restart.
This has some consequences: Loading the libraries (pandas and matplotlib in particular) costs.
Before the program can even run the startup can take some time. Fortunately the most frequent
operation we need to perform is once evey 5 minutes so we can live with this.

The toughest part of this has been the alternating between metric and imperial units every other
time.  This is accomplished using an variable stored in a local file .env.  I tried to develop a
persistance method using environment files but just couldn't make it stick.  If I were ambitious I
would implement a profile tool to set many of the specific parameters in there rather than set them
willy nilly throughout this code.

Much of this code is top-down developed on the fly with the help of a jupyter notebook.  It would
probably break if the sources changed a lot.  I'll take my chances.

"""

"""
Essential libraries we need.
"""
import pandas as pd
# This may not be needed as pandas probably brings in everything we need but just in case.
import numpy as np
# matplotlib is the tool that will create the graphs
import matplotlib.pyplot as plt

###
# Time libraries we are very dependant on 'aware' times. Most bugs have been traced back
# to a misunderstanding of how important that times be 'aware'.
from datetime import tzinfo, timedelta, datetime, date
from pytz import timezone  # should already be part of pandas but it doesn't hurt to do it again.
import logging
import cgi
import os

###
# cgi call from browser chooses units

# Global constants we use throughout.
EST = timezone('America/New_York')

# values for REST call
measureUnits = ('english', 'metric')
stationsNearUs = {  'NewRochelleNY':  '8518490',
                    'RyePlaylandNY':  '8518091',
                    'CosCobCT':       '8469549',
                    'ThrogsNeckBrNY': '8518526',
                    'KingsPointNY':   '8516945',
                    'BatteryNY':      '8518750',
                    'BridgeportCT':   '8467150',
                    'NewHavenCT':     '8465705',
                    'NewboldPA':      '8548989',  # Way up the Chesapeake River
                    'TurkeyPointNY':  '8518962',  # Way up the Hudson River
                    }

tideStation = stationsNearUs['RyePlaylandNY']  # Closest one to us with reliable data

pathToResources = 'resources/'

###
# import common library
from tidedata import fetchDailyTides

#@markdown Make the fancy image with next tide
def makeTideGraphic(extremaDF, detailDF=None):
    # make up for image import deprecation
    # import PIL
    # import urllib.request
    """
    Make tide ala NOAA from two sets of pandas DataFrames:
    detailDF -- Detailed predicted water levels for complete graph
    extremeDF -- The extrema (highs and lows)
    """
    global gTime

    lbl = {'H': 'HIGH', 'L': 'LOW'}

    # imageURL = 'https://docs.google.com/drawings/d/e/2PACX-1vRPpyCKk834LQUUwoEWDiopLKIcRscn3AoUPynXzNe6jPRLXWt9TBS90Wwm_MjxVoqezD09hbx_0Sw8/pub?w=225&h=159'
    # imageRef = PIL.Image.open(urllib.request.urlopen(imageURL))
    imageRef = pathToResources + 'TideBackground.png' # fetch locally (way faster on a pi)
    imageOverlay = plt.imread(imageRef)
    (hgt,wdt,cols) = imageOverlay.shape

    plt.figure(figsize=(3, 3))

    implot = plt.imshow(imageOverlay)
    implot.axes.get_xaxis().set_visible(False)
    implot.axes.get_yaxis().set_visible(False)

    oceanFloor = 120  # ocean floor in pixel coordinates

    upcoming = extremaDF[extremaDF['DateTime']>datetime.now(tz=EST)]
    nxtTide = upcoming.iloc[0]

    logging.debug(f"next Tide: '{nxtTide['DateTime'].strftime('%H:%M')}' '{nxtTide['DateTime'].strftime('%I:%M %p')}'")

    if gTime == '24':
        plt.text(wdt/2, 40, nxtTide['DateTime'].strftime('%H:%M'), fontsize=26.0, ha='center' )
    else:
        plt.text(wdt/2, 40, nxtTide['DateTime'].strftime('%I:%M %p'), fontsize=26.0, ha='center' )
    plt.text(wdt/2, 80, lbl[nxtTide['Type']], fontweight='heavy', color='blue', fontsize=20.0, ha='center')

    if nxtTide['Type'] == 'H':
        len = -50
    else:
        len = 50
    plt.arrow(wdt/6, 65-len/4, 0, len, width=6., color='cyan',
                length_includes_head=True, alpha=0.6, fill=False, linewidth=2.0)

    logging.debug(f"next Tide: '{nxtTide['Type']}' len: '{len}'")

    # Somehwat kludgy since we know the range is between -1 and 10ft
    try:
        current = detailDF[detailDF['DateTime']>datetime.now(tz=EST)]
        nxtTide = current.iloc[0]
    finally:
        level = nxtTide['Tide [ft]']

    # arbitrary scaling so we fit tides in our area range from -1ft to +10ft
    sclDepth = (level + 1.5) / 12.0
    scaledTideHeight = int(hgt*sclDepth)

    logging.debug(f"time: {current.iloc[0]['DateTime'].strftime('%I:%M %p')}, hgt: {hgt}, level: {level:6.2f}, scaleDepth: {sclDepth:6.3f}, scaledHeight: {scaledTideHeight:6d}")

    scaledTideHeight = hgt - oceanFloor*(level + 2)/10.

    plt.title('Next Tide At...')
    plt.axis('off')
    oceanFloor = 20  # bottom in pixel coordinates
    t = np.linspace(0, wdt-2, 50)
    y = (hgt-oceanFloor) - (scaledTideHeight + 2 * np.cos(t/4)**2)
    plt.fill_between(t, hgt-oceanFloor, y, color='SkyBlue', alpha=0.50)

    #plt.show()
    plt.savefig(pathToResources  + 'tmp/' + 'tideCartoon.png', bbox_inches='tight', transparent=True)
    plt.close()

# Should run this every 5 minutes to keep the screen up to date.
def refresh(time):
    global gTime
    gTime = time

    # Get the data this method tries to fetch from local store first
    (ryePlayDetailDF, ryePlayExtremDF) = fetchDailyTides(tideStation)

    # make the pseudo 'next tide' graphic
    makeTideGraphic(ryePlayExtremDF, ryePlayDetailDF)

"""
    Entrypoint for the call. The expected optional parameters for cgi-call:
    {'24hour' | '12hour'} which delinate 24 hour or 12 (am/pm) for the time
    It is expected that the web page runs this as a cgi request periodically.
"""
if __name__ == '__main__':                                                               #01234567890123
    prog = 'TideGraphic  '
    logging.basicConfig(filename='WeatherKiosk.log', format=f"%(levelname)s:\t%(asctime)s\t{prog}\t%(message)s", level=logging.INFO)

    #   first fetch the strings passed to us with the fields outlined
    fs = cgi.FieldStorage()  # this is a dictionary of storage objects not strings!
    logging.info(f"\tfield storage: {fs}")
    time = '12hour'
    if 'clock' in fs:
        time = fs['clock']

    logging.info(f"\t...clock format {time}")

    refresh(time)

    logging.info('\t...done')

    print('Content-Type: text/plain\n')
    print('tidesGraphic done.')
