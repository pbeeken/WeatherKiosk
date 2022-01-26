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
gTideUnit = 'Tide [ft]' # 'Tide [m]'  default replaced in main

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

###
# import common library
from tidedata import fetchDailyTides

#@markdown Make the summary table for the next four tide extrema 
def makeTideTable(extremaDF):
    """
    Make the html table of the next 4 tide extrema
    extremeDF -- The extrema (highs and lows)
    """
    global gTideUnit
    lbl = {'H': 'HIGH', 'L': 'LOW'}

    now = datetime.now(tz=EST)

    tideFile = "tideTable.html"
    templateFile = "_" + tideFile

    # pick the units based on gTideUnit

    sel = extremaDF['DateTime'] > now
    futureTides = extremaDF[sel]

    htmlText = futureTides[:4].to_html( 
                            columns=['Date', 'Time', 'Type', gTideUnit], 
                            index=False, 
                            border=0,
                            formatters={
                                gTideUnit: lambda x:f"{x:6.1f}",
                                'Type': lambda l: lbl[l]
                                },
                            table_id = "tideTable"
                            )

    #open the template file
    with open(templateFile, "r") as templateFile:
        templateHTML = templateFile.readlines()
 #   templateFile.close()

    # copy the html table into the text and write out a new file 
    with open(tideFile, "w") as htmlFile:
        htmlFile.write( ("".join(templateHTML)).replace('<!--Table Place-->', htmlText) )

# Should run this every 5 minutes to keep the screen up to date.
def refresh():
    # Get the data this method tries to fetch from local store first
    (ryePlayDetailDF, ryePlayExtremDF) = fetchDailyTides(tideStation)

    # make the pseudo NOAA tide graph
    makeTideTable(ryePlayExtremDF)


"""
We want to run this command peridoically to update the clock 
If we run it within python we run the risk of memory leaks so
I will run it as a periodic bash shell (we only have to run once every 5min or so)
"""
if __name__ == '__main__':
    import os
    
    print("Building tide table...")

    idx = 0
    try:
        idx = int( os.getenv('TIDECNT') )
    except:
        pass
    
    gTideUnit = ('Tide [ft]', 'Tide [m]')[idx]
    print(f"\t...using {gTideUnit} [{idx}]")
    
    refresh()

    print("\t...I'm outta here!")
