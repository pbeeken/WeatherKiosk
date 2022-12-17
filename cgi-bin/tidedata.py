"""
Essential libraries we need.  This is a library shared between 3 different generators.
"""
import pandas as pd
# This may not be needed as pandas probably brings in everything we need but just in case.
import numpy as np
# matplotlib is the tool that will create the graphs
# import matplotlib.pyplot as plt
import os

###
# Time libraries we are very dependant on 'aware' times. Most bugs have been traced back
# to a misunderstanding of how important that times be 'aware'.
from datetime import tzinfo, timedelta, datetime, date
from pytz import timezone  # should already be part of pandas but it doesn't hurt to do it again.
import logging

# Global constants we use throughout.
EST = timezone('America/New_York')

# # values for REST call
# measureUnits = ("english", "metric")
# stationsNearUs = {  'NewRochelleNY':  "8518490",
#                     'RyePlaylandNY':  "8518091",
#                     'CosCobCT':       "8469549",
#                     'ThrogsNeckBrNY': "8518526",
#                     'KingsPointNY':   "8516945",
#                     'BatteryNY':      "8518750",
#                     'BridgeportCT':   "8467150",
#                     'NewHavenCT':     "8465705",
#                     "NewboldPA":      "8548989",  # Way up the Chesapeake River
#                     'TurkeyPointNY':  "8518962",  # Way up the Hudson River
#                     }

# tideStation = stationsNearUs['RyePlaylandNY']  # Closest one to us with reliable data
# Visual check at [Mamaroneck Web Cam](https://www.weatherbug.com/weather-camera/?cam=MMBPC) for checking the tides?

###
# fetchTideData
# Get raw data from the NOAA tide database/calculator. Tide information is generated based on a harmonic analysis of
# many years of data. The parameters change every 20 years or so so I could just fetch the numbers but NOAA is cagey
# about how to input the time (what epoch constitutes 0 for example) So I pull the data based on our location.  What
# I do to spare the server is to cache the result so I only pull the data once per day.  This way my 'tide' clock can
# update the current pointer once per 5 minutes without hammering on the server.  This is just the inet fetch part.
#
def fetchTideData(station, begDate, endDate, datum="MLLW", interval=15, timezone="LST_LDT", units="english", clock="24hour"):
  """
  fetchTideData
  Fetch tide from NOAA Site using REST -> pandas DataFrame with tide levels
  required arguments:
    station -- StationID
    begDate -- start date (only fetches using day)
    endDate -- end date

    units -- "english" | "metric" # units
    interval -- "hilo" | "h" | 30 | 15 | 6 | 1 # hi and lo, hourly, min intervals
    datum -- "MLLW" | "STND" | "MHHW" | "MHW" | "MTL" | "MLW" | "MLLW" | "NAVD" # height references
    tzone -- "LST_LDT" | "LST" | "GMT" # Local with dst, local or GMT
    clock -- "24hour" | "12hour" # clock style

    This routine checks a local cache cache so that we don't have to fetch that doesn't change
    that much over a 24 hour period.

  """
  noaaSite = [f"https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL",
              f"&begin_date={begDate.strftime('%Y%m%d')}&end_date={endDate.strftime('%Y%m%d')}",
              f"&datum={datum}",
              f"&station={station}",
              f"&time_zone={timezone}&clock={clock}",
              f"&units={units}&interval={interval}&format=csv",
              ]

  # return "".join(noaaSite)
  tideDF = pd.read_csv("".join(noaaSite))

  # First we need to rename some of the columns to take out extraneous spaces
  repl = dict([(s, s.strip()) for s in tideDF.columns])
  tideDF = tideDF.rename(repl, axis='columns')

  # convert string dates to proper date times and other conveniences for future expansion
  #TODO: Consider only fetching GMT but passing tz object as local timezone
  tideDF['DateTime'] = tideDF['Date Time'].apply(lambda x:datetime.strptime(x, "%Y-%m-%d %H:%M").replace(tzinfo=EST))

  # Provide a column with delta hours for calculations (used mostly for debugging)
  minTime = tideDF['DateTime'].min()
  tideDF['Hours'] = tideDF['DateTime'].apply(lambda x:(x-minTime).total_seconds()/3600)

  # Break out the date and time as a strings for comparison tricks
  tideDF['Date'] = tideDF['Date Time'].apply(lambda x: x[:10])
  tideDF['Time'] = tideDF['Date Time'].apply(lambda x: x[11:])

  # Regardless of which units we fetched generate a column of the other so we don't need to duplicate calls.
  #TODO: Consider only getting metric and provide column of imperial as an option.
  if units=='english':
    # add the other units to the list
    tideDF = tideDF.rename({'Prediction': 'Tide [ft]'}, axis='columns')
    tideDF['Tide [m]'] = tideDF['Tide [ft]'] / 3.28084
    tideDF['Units'] = 'ft Feet'
  else:
    tideDF = tideDF.rename({'Prediction': 'Tide [m]'}, axis='columns')
    tideDF['Tide [ft]'] = tideDF['Tide [m]'] * 3.28084
    tideDF['Units'] = 'm  Meters'

  return tideDF

###
# fetchDailyTides
# The entry point for the getting of regular pieces of information about tides.  This routine checks the local
# store and if it is under 24 hours old uses the local cache. Otherwise it refreshes the cache.
#
def fetchDailyTides(fromTideStation):
    """
    fetchDailyTides
    Fetch daily tide predictions to get the tide data for a few days ahead -> (detailDF, extremaDF)
    This method checks for the existance and timelyness of a local store before going to the web.
    before fethcing from the NOAA site.
    fromTideStation -- NOAA tide station code
    """
    # Local store
    detailTidesFile = 'resources/tmp/DetailTides.zip'  # 15 minute intervals (for smooth graph)
    extremTidesFile = 'resources/tmp/ExtremTides.zip'  # Just the hi and low values for extrema

    # Fetch this data once per day.  And run all the subsequent graphics from the local store.
    now       = datetime.now(tz=EST)
    today     = now.date()

    # Proper way to set up timeshifts.
    yesterday = now - timedelta(days=0)
    tomorrow  = now + timedelta(days=2)

    # First look for existing data, if not found: create, if found: load and test for age
    try:
        logging.info("\tLIB:fetchDailyTides...try to read saved data")
        tideDetailDF = pd.read_pickle(detailTidesFile, compression='infer')
        tideExtremDF = pd.read_pickle(extremTidesFile, compression='infer')
    except FileNotFoundError:
        logging.info("\tLIB:fetchDailyTides...file doesn't exist, creating")
        # Get the data
        tideDetailDF = fetchTideData(fromTideStation, yesterday.date(), tomorrow.date())
        tideDetailDF.to_pickle(detailTidesFile, compression='infer')
        tideExtremDF = fetchTideData(fromTideStation, yesterday.date(), tomorrow.date(), interval='hilo')
        tideExtremDF.to_pickle(extremTidesFile, compression='infer')

    # Check to see if the data is stale (older than one day)...
    if tideDetailDF['DateTime'][1].date()!=today:
        tideDetailDF = fetchTideData(fromTideStation, yesterday.date(), tomorrow.date())
        tideDetailDF.to_pickle(detailTidesFile, compression='infer')

    # Check to see if the data is stale (older than one day)...
    if tideExtremDF['DateTime'][1].date()!=today:
        tideExtremDF = fetchTideData(fromTideStation, yesterday.date(), tomorrow.date(), interval='hilo')
        tideExtremDF.to_pickle(extremTidesFile, compression='infer')

    # The REST Call always returns at least 3 days of infomraiont (can't just return the next 24 hours)
    # so we have to truncate the list.
    selDet = tideDetailDF['DateTime']<tomorrow
    selExt = tideExtremDF['DateTime']<tomorrow

    tideDetailDF = tideDetailDF[selDet]
    tideExtremDF = tideExtremDF[selExt]
    logging.info(f"\tLIB:fetchDailyTides...start: {tideDetailDF['DateTime'].iloc[0]} end:{tideDetailDF['DateTime'].iloc[-1]}")

    return (tideDetailDF, tideExtremDF)
