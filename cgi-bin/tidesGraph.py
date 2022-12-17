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

pathToResources = "resources/"

###
# import common library
from tidedata import fetchDailyTides

###
# makeTideGraph
# The business end that makes the fancy graphic that includes a moing line that shows out current time
# against a graph of the tide height.
#
def makeTideGraph(detailDF, extremaDF):
    """
    makeTideGraph
    Make tide ala NOAA from two sets of pandas DataFrames:
    detailDF -- Detailed predicted water levels for complete graph
    extremeDF -- The extrema (highs and lows)
    """
    global gTideUnit # unit switch flag

    graphFile = pathToResources + "tmp/"+ "tideGraph.png"

    import matplotlib.transforms
    import matplotlib.dates as mdates

    today = datetime.now(tz=EST).date()

    # Set up the plot and plot the data
    # px = 1/plt.rcParams['figure.dpi']  # pixel in inches (doesn't work if bbox is 'tight')
    fig, ax = plt.subplots(figsize=(2*11.5/3, 4))

    ax.plot(detailDF['DateTime'], detailDF[gTideUnit], color="blue", alpha=0.8)

    # Markers at extrema with square marks
    ax.scatter(extremaDF['DateTime'], extremaDF[gTideUnit], color="blue", marker="s")
    for index, row in extremaDF.iterrows():
        xy = (row['DateTime'], row[gTideUnit])
        u = gTideUnit.split("[")[1].split("]")[0]   # row['Units']
        ax.annotate(f'{xy[1]:5.1f} {u[:2]}', xy=xy, xytext=(8,0), textcoords='offset points', color='blue')

    # Set the axis labels
    # ax.set_xlabel("Date and Time", fontsize=14, fontstyle='italic', color='SlateGray')
    ax.set_ylabel(f"Tide Level [{u}]", fontsize=14, fontstyle='italic', color='SlateGray')
    # ~put an alternate axis in meters~ Alternate between meters and feet in 5min intervals

    # Put a vetical bar that marks right now.
    now = datetime.now(tz=EST)
    (ymin, ymax) = ax.get_ylim()
    ax.annotate(f"Current Time   {now.time().strftime('%I:%M %p')}", xy=(now, (ymin+ymax)/2), xytext=(-15,-60), textcoords='offset points', color='green', rotation=90.0, alpha=0.6 )
    ax.vlines(now, ymin=0.1, ymax=0.9, transform=ax.get_xaxis_transform(), colors="green", linestyles='dashed', linewidth=4, alpha=0.7)

    #Fix the time axis
    ax.xaxis.set_major_locator(mdates.DayLocator(tz=EST))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=4, tz=EST))

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a, %b %d', tz=EST))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M', tz=EST))

    dx = 0.; dy = -10/72.
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, fig.dpi_scale_trans)
    # Create offset transform by 5 points in x direction
    for label in ax.xaxis.get_majorticklabels():
        label.set(horizontalalignment='center', color="darkred", fontweight='bold')
        label.set_transform(label.get_transform() + offset)

    for label in ax.xaxis.get_minorticklabels():
        label.set(horizontalalignment='center', color="darkred", fontsize=6.5)

    ax.grid(True, which='major', linewidth=2, axis='both', alpha=0.7)
    ax.grid(True, which='minor', linestyle="--", axis='both', alpha = 0.5)

    # fig.show()
    fig.savefig(graphFile, bbox_inches='tight', transparent=True)
    plt.close(fig)

# Should run this every 5 minutes to keep the screen up to date.
def refresh():
    # Get the data this method tries to fetch from local store first
    (ryePlayDetailDF, ryePlayExtremDF) = fetchDailyTides(tideStation)

    # make the pseudo NOAA tide graph
    makeTideGraph(ryePlayDetailDF, ryePlayExtremDF)


"""
    Entrypoint for the call. expected optional parameters for cgi-call are:
    units=metric | imperial | 1 | 0
    It is expected that the web page runs this as a cgi request every 15 min or so.
"""
if __name__ == '__main__':                                                               #01234567890123
    logging.basicConfig(filename='WeatherKiosk.log', format='%(levelname)s:\t%(asctime)s\tTideGraph     \t%(message)s', level=logging.INFO)

    #   first fetch the strings passed to us with the fields outlined
    fs = cgi.FieldStorage()  # this is a dictionary of storage objects not strings!
    logging.info(f"\tfield storage: {fs}")
    idx = 0
    if "units" in fs:
        logging.debug(f"\tunits updated: {fs['units'].value}")
        if (fs['units'].value == 'metric') or (fs['units'].value == '1'):
            idx = 1
        elif (fs['units'].value == 'imperial') or (fs['units'].value == '0'):
            idx = 0

    gTideUnit = ('Tide [ft]', 'Tide [m]')[idx]
    logging.info(f"\t...using {gTideUnit}")

    refresh()

    print("Content-Type: text/plain\n")
    print("tidesGraph done.")
