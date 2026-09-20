#!/usr/bin/python3

import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import matplotlib.transforms
import matplotlib.dates as mdates

### Global Structures and Configurations
# 03/04/26 now supports ZoneInfo so we can remove the pytz dependency.
TZ_NY = ZoneInfo('America/New_York')
UTC = ZoneInfo('UTC')
EST = TZ_NY
DATA_AGE_HOURS = 99.9  # Optimism, the data should be no more than 1 hour old. We will warn if it's older than that.

# The pwd is the webpage
import logging
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
pathToResources = BASE_DIR.parent / 'resources'       # where the data cache and the "static" resources are stored.
pathToImages = BASE_DIR.parent / 'resources' / 'tmp'  # where the generated graphs and tables are stored. aka "mutable content"
pathToLogs = BASE_DIR.parent / 'resources' / 'logs'   # where the logs are stored.

# Getting Weather Data from execution rocks (station 44022)  Only needs to run every 15 minutes.
def fetchWindData(source):
    now = datetime.now(tz=EST)

    windDF = pd.read_csv(source, sep="\\s+", header=[0,1], na_values='MM', nrows=450 ) # Deprecated: , delim_whitespace=True
    logging.info(f"\t...got {len(windDF)} data values")

    #Remove unneded header and rename columns for clarity
    windDF.columns = windDF.columns.get_level_values(0)
    windDF = windDF.rename(columns={'#YY': 'YY'})

    # Build DateTime Index column and generate directional components for averaging
    windDF['DateTime_UTC'] = pd.to_datetime(windDF[['YY', 'MM', 'DD', 'hh', 'mm']].astype(str).agg('-'.join, axis=1), format='%Y-%m-%d-%H-%M')
    windDF['DateTime_UTC'] = windDF['DateTime_UTC'].dt.tz_localize('UTC')
    windDF['DateTime'] = windDF['DateTime_UTC'].dt.tz_convert(EST)
    windDF = windDF.set_index('DateTime')
    windDF = windDF.drop(columns=['YY', 'MM', 'DD', 'hh', 'mm'])

    # Keep only the desired columns
    windDF = windDF[['WDIR', 'WSPD', 'GST', 'PRES', 'ATMP']]

    # We need to average the components rather than the angles when resamping.
    windDF['WdirSin'] = np.sin(np.radians(windDF['WDIR']))
    windDF['WdirCos'] = np.cos(np.radians(windDF['WDIR']))

    return windDF

def makeWindGraph(windDF, whereFrom=""):
    if len(windDF) < 16:
      raise BaseException('Not enough points')

    imageRef = pathToImages / 'windGraph.png' # fetch locally (way faster on a pi)
    fig, ax = plt.subplots(figsize=(8, 4))

    # determine how old the data is...
    last = windDF.index[-1].to_pydatetime()
    now = datetime.now(TZ_NY)
    delta = now-last

    tme = windDF.index
    wspd = windDF['WSPD'] # windDF['WSPD']
    mxsp = windDF['GST'] # windDF['GST']

    # convert m/s to mph: 0.447, m/s to knot: 0.5144
    ax.plot(tme, wspd/0.5144, 'bo-', alpha=0.8)
    ax.plot(tme, mxsp/0.5144, 'ro-', alpha=0.8)


    # Plot direction arrows
    yloc = 3.0 * np.ones(windDF.shape[0])
    # we stored the direction components so the averages would be modulo 360 (or 2pi)
    #    The average between 10 and 350 should be 0 (or 360) NOT 180.
    # An arrow every other step
    (cosines, sines) = (windDF['WdirCos'], windDF['WdirSin'])
    ax.quiver(tme[::2], yloc[::2], sines[::2], cosines[::2],
              angles='uv', color='DodgerBlue', alpha=0.6, pivot='middle')
    # Set the axis labels
    # ax.set_xlabel('Date and Time', fontsize=10, fontstyle='italic', color='SlateGray')  #obvious don't need it.
    ax.set_ylabel('Wind Speed [knots]', fontsize=12, fontstyle='italic', color='SlateGray')

    #Fix the time axis
    ax.xaxis.set_major_locator(mdates.DayLocator(tz=EST))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=4, tz=EST))

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a, %b %d', tz=EST))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M', tz=EST))

    dx = 0.; dy = -10/72.
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, fig.dpi_scale_trans)
    # Create offset transform by 5 points in x direction
    for label in ax.xaxis.get_majorticklabels():
        label.set(horizontalalignment='center', color='darkred', fontweight='bold')
        label.set_transform(label.get_transform() + offset)

    for label in ax.xaxis.get_minorticklabels():
        label.set(horizontalalignment='center', color='darkred')

    ax.grid(True, which='major', linewidth=2, axis='both', alpha=0.7)
    ax.grid(True, which='minor', linestyle='--', axis='both', alpha = 0.5)
    ax.set_ylim(bottom=0.0)

    # where did this come from?
    plt.text(0.99, 0.96, f"{whereFrom}",
         horizontalalignment='right', verticalalignment='center',
          transform=ax.transAxes, color='gray', alpha=0.6 )

    ##
    # Put a current conditions slug at the top
    tme = windDF.index[-1]
    wspd = np.round(2.23694 * windDF.iloc[-1]['WSPD'],1)
    mxsp = np.round(2.23694 * windDF.iloc[-1]['GST'],1)
    if mxsp != mxsp:
      mxsp = '-'
    temp = windDF.iloc[-1]['ATMP']
    wdir = windDF.iloc[-1]['WDIR']

    old = datetime.now(tz=EST)-tme
    oldmin = np.int32(old.total_seconds()%60)
    oldhrs = np.int32(old.total_seconds()/3600)
    global DATA_AGE_HOURS
    DATA_AGE_HOURS = oldhrs + oldmin/60.0
    logging.debug(f"{tme}, {oldhrs}:{oldmin} old, {wspd} mph, {mxsp} mph, {wdir:4.0f}°T, {temp}°C")

    plt.text(0.99, 0.90, f"Last readings spd:{wspd}, max:{mxsp}, dir:{windDirection(wdir)}",
            horizontalalignment='right', verticalalignment='center',
            transform=ax.transAxes, color='blue', alpha=0.6 )
    if oldhrs > 1 or oldmin > 40:
        plt.text(0.99, 0.84, f"Warning {oldhrs}:{oldmin} old",
                horizontalalignment='right', verticalalignment='center',
                transform=ax.transAxes, color='darkred', alpha=0.6 )

    #   fig.show()
    fig.savefig(imageRef, bbox_inches='tight', transparent=True)
    plt.close(fig)

# direction indexer
def windDirection(ang):
  labels = {
    'N': (-11.25, 11.25), 'NNE': (11.25, 33.75),   'NE': (33.75, 56.25),   'ENE': (56.25, 78.75),
    'E': (78.75, 101.25), 'ESE': (101.25, 123.75), 'SE': (123.75, 146.25), 'SSE': (146.25, 168.75),
    'S': (168.75, 191.25),'SSW': (191.25, 213.75), 'SW': (213.75, 236.25), 'WSW': (236.25, 258.75),
    'W': (258.75, 281.25),'WNW': (281.25, 303.75), 'NW': (303.75, 326.25), 'NNW': (326.25, 348.75),
    }
  for tag in labels.keys():
    if ang > labels[tag][0] and ang <= labels[tag][1]:
      return tag

# Exscution Rocks weather buoy
real_EXR_TimeDataFile = 'https://www.ndbc.noaa.gov/data/realtime2/44022.txt'  # Dead to me
# Kings Point
real_KPH_TimeDataFile = 'https://www.ndbc.noaa.gov/data/realtime2/KPTN6.txt'  # Only game in town right now.
# Western Long Island Sound
real_WLI_TimeDataFile = 'https://www.ndbc.noaa.gov/data/realtime2/44040.txt'  # Dead to me

weatherBuoys = {
  'Kings Point LI': 'https://www.ndbc.noaa.gov/data/realtime2/KPTN6.txt',  # Originally we led with EXR but it's been dead for a while and KPTN6 is the only game in town.
  # 'Execution Rocks': 'https://www.ndbc.noaa.gov/data/realtime2/44022.txt', # LIRACOOS buoy 44022 is at Execution Rocks, the western end of Long Island Sound.  It's the closest to us and was the most reliable. Offline to NWS
  # 'Western LI': 'https://www.ndbc.noaa.gov/data/realtime2/44040.txt',      # LIRACOOS buoy 44040 is at the western end of Long Island Sound.  It's the second closest to us and was the second most reliable. Offline to NWS
}


def main():
    now = datetime.now().astimezone(TZ_NY)
    d = timedelta(days = 2)

    # Go through a chain of nearby buoys until we get a good one.
    # I don't want to fail just because one buoy is down.
    # I want to make sure it works before I try EXR again.
    # As of June 2024 both EXR and WLI are dead to me.
    for (source, url) in weatherBuoys.items():
        try:
            logging.info('\t...source: %s', source)
            theDF = fetchWindData(url)
            # theDF.dropna(inplace=True) # every record has missing data columns but the're not important for the graph.  We just need the date and the wind speed and direction.
            smpl = theDF.index > (now - d)
            lastCaptureDateTime = theDF[smpl].index.max()
            logging.info(f"\t...last capture {DATA_AGE_HOURS:0.1f} hours ago")
            makeWindGraph( theDF[smpl].reset_index().resample('1h', on='DateTime').mean(), whereFrom=source )
            break
        except Exception:
            logging.info('\t... failed.')

    logging.info('\t...done')

    # This is a CGI script, so we need to print the content type header and a blank line before the output.
    print('Content-Type: text/plain\n')
    print(f"SUCCESS: Wind graph generated from data captured '{DATA_AGE_HOURS:0.1f}' hours ago.\n")
    print('windGraphNWS done.')

if __name__ == '__main__':
    prog = 'WindGraphNWS '
    logging.basicConfig(filename=pathToLogs /'WeatherKiosk.log', format=f'%(levelname)s:\t%(asctime)s\t{prog}\t%(message)s', level=logging.INFO)
    logging.info('Build wind graph...')
    main()
