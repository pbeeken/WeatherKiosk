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
import time

###
# With each call we flip the units so we toggle back and 
# general unit choice
#   alternate calls switch back and forth between metric and imperial (we have an international audience)
gTideUnit = 'Tide [ft]' # 'Tide [m]'

# Global constants we use throughout.
EST = timezone('America/New_York')

# values for REST call
measureUnits = ("english", "metric")
stationsNearUs = {  'NewRochelleNY':  "8518490",
                    'RyePlaylandNY':  "8518091",
                    'CosCobCT':       "8469549",
                    'ThrogsNeckBrNY': "8518526",
                    'KingsPointNY':   "8516945",
                    'BatteryNY':      "8518750",
                    'BridgeportCT':   "8467150",
                    'NewHavenCT':     "8465705",
                    "NewboldPA":      "8548989",  # Way up the Chesapeake River
                    'TurkeyPointNY':  "8518962",  # Way up the Hudson River
                    }

tideStation = stationsNearUs['RyePlaylandNY']  # Closest one to us with reliable data
pathToResources = "/home/pi/WeatherKiosk/resources/"

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
    global gTideUnit
    lbl = {'H': 'HIGH', 'L': 'LOW'}

    now = datetime.now(tz=EST)

    # imageURL = "https://docs.google.com/drawings/d/e/2PACX-1vRPpyCKk834LQUUwoEWDiopLKIcRscn3AoUPynXzNe6jPRLXWt9TBS90Wwm_MjxVoqezD09hbx_0Sw8/pub?w=225&h=159"
    # imageRef = PIL.Image.open(urllib.request.urlopen(imageURL))
    imageRef = pathToResources + "TideBackground.png" # fetch locally (way faster on a pi)
    imageOverLay = plt.imread(imageRef)
    # px = 1/plt.rcParams['figure.dpi']  # pixel in inches doesn't quite work when bbox='tight'
    plt.figure(figsize=(3, 3))

    implot = plt.imshow(imageOverLay)
    implot.axes.get_xaxis().set_visible(False)
    implot.axes.get_yaxis().set_visible(False)

    hgt = 125 #158
    wdt = 222 #225
    lvl = 110

    upcoming = extremaDF[extremaDF['DateTime']>datetime.now(tz=EST)]
    nxtTide = upcoming.iloc[0]
    plt.text(wdt/2, 50, nxtTide['DateTime'].strftime("%I:%M %p"), fontsize=30.0, ha='center' )
    plt.text(wdt/2, 90, lbl[nxtTide['Type']], fontweight='heavy', color='blue', fontsize=24.0, ha='center')

    
    if nxtTide['Type'] == 'H':
        len = -50
    else:
        len = 50
    plt.arrow(wdt/6, 90-len/2, 0, len, width=6., color="cyan", 
                length_includes_head=True, alpha=0.6, fill=False, linewidth=2.0)

    # Somehwat kludgy since we know the range is between -1 and 10ft
    try:
        current = detailDF[detailDF['DateTime']>datetime.now(tz=EST)]
        nxtTide = current.iloc[0]
        level = nxtTide[gTideUnit]
    except:
        level = nxtTide[gTideUnit]

    if gTideUnit == 'Tide [ft]':
        scaledTideHeight = hgt - lvl*(level + 2)/10.
    else:
        scaledTideHeight = hgt - lvl*(level + 0.5)/3.0

    plt.title("Next Tide At...")
    plt.axis('off')
    t=np.linspace(0,wdt,50)
    y=scaledTideHeight + np.cos(t/5) * 3
    plt.fill_between(t,y, color="SkyBlue", alpha=0.50)

    #plt.show()
    plt.savefig(pathToResources + "tideGraphic.png", bbox_inches='tight', transparent=True)
    plt.close()

# Should run this every 5 minutes to keep the screen up to date.
def refresh():
    # Get the data this method tries to fetch from local store first
    (ryePlayDetailDF, ryePlayExtremDF) = fetchDailyTides(tideStation)

    # make the pseudo 'next tide' graphic
    makeTideGraphic(ryePlayExtremDF, ryePlayDetailDF)

"""
We want to run this command peridoically to update the clock 
If we run it within python we run the risk of memory leaks so
I will run it as a periodic bash shell (we only have to run once every 5min or so)
"""
if __name__ == '__main__':
    import os
    
    print("Building tide graphic...")

    idx = 0
    try:
        idx = int( os.getenv('TIDECNT') )
    except:
        pass
    
    gTideUnit = ('Tide [ft]', 'Tide [m]')[idx]
    print(f"\t...using {gTideUnit}")
    
    refresh()

    print("\t...I'm outta here!")
