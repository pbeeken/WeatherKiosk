#!/usr/bin/python3

"""
Docstring for cgi-bin.windGraphOCR
This is intended to be a 'plug replacement' for the existing
wind graph generation code. It will fetch the data from the
buoys, process it, and generate a graph that can be used in the
kiosk display. The graph will show wind speed and direction
over time, with annotations for current conditions and data source.

2/16/26 It WORKS!  Tough to develop on a powerful pc and deploy on a toy.
2/16/26    needs refactoring to clean-up the hacks.
"""

import logging
from datetime import datetime, timedelta
from pytz import timezone  # should already be part of pandas but it doesn't hurt to do it again.

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.transforms
import matplotlib.dates as mdates

EST = timezone('America/New_York')
UTC = timezone('UTC')

# The data is stored locally in a csv file that is updated by a separate process that fetches the data from the buoys.
# This is much faster than fetching the data from the buoys every time we want to generate a graph, especially on a Raspberry Pi.
# On the pi there are two repositories. One contains the feedstock of the visual elements (static images, html, etc) and the other
# is the cache of materials (graphs, images and table) that are refreshed by separate processes.

# The pwd is the webpage
pathToResources = 'resources/'  # where the data cache and the "static" resources are stored.
pathToImages = 'resources/tmp/'  # where the generated graphs and tables are stored. aja "mutable content"

def fetchWindData(source):
    """
    This gathers the accumulated data from an asynchronous populated datastore by
    OCR the screens from floating buoys out on the sound within a few miles of our club.
    The tabulated data was published by the NWS but UCONN redesigned or had built
    new more robust units but lost the personnel to vet the data so the NWS stopped
    hosting the stream.
    :param source: the path to the file that contains the data store.  We ingest it.
    :return pandas dataframe containing the data.
    """

    logging.info(f"\t...getting from {source}")
    # Getting Weather Data from execution rocks (station 44022)  Only needs to run every 15 minutes.
    windDF = pd.read_csv(source, index_col=0, parse_dates=True)
    windDF.dropna(inplace=True)                                     # wind data has glitches
    logging.info(f"\t...got {len(windDF)} data values")

    # We need to average the components rather than the angles when re-sampling.
    windDF['WdirSin'] = np.sin(np.radians(windDF['WindDir [°]']))
    windDF['WdirCos'] = np.cos(np.radians(windDF['WindDir [°]']))

    return windDF

def makeWindGraph(windDF, whereFrom=""):
    """
    makeWindGraph builds the wind graph from the recorded data.

    :param windDF:  pandas DataFrame with wind data.
    :param whereFrom: Description
    """
    if len(windDF) < 16:
      raise BaseException('Not enough points')

    # determine how old the data is...
    last = windDF.index[-1].to_pydatetime()
    now = datetime.now(EST)
    delta = now-last
    # print(f"{last} -> {now}  Data is {delta} old")

    # Work with data from the last 2 days
    cutoff_time = datetime.now(EST) - timedelta(hours=32)
    windDF = windDF[windDF.index >= cutoff_time]

    # Resample to 1 hour intervals, averaging the components
    windDF = windDF.select_dtypes('number').resample('30min').mean()

    logging.debug(windDF.head())
    logging.debug('...')
    logging.debug(windDF.tail())

    imageRef = pathToImages + "windGraph.png" # fetch locally (way faster on a pi)
    fig, ax = plt.subplots(figsize=(8, 4))

    tme = windDF.index
    wspd = windDF['WindSpeedAvg [kts]'] # windDF['WSPD']
    mxsp = windDF['WindSpeedGst [kts]'] # windDF['GST']

    # convert m/s to mph: 0.447, m/s to knot: 0.5144
    ax.plot(tme, wspd, 'bo-', alpha=0.8)
    ax.plot(tme, mxsp, 'ro-', alpha=0.8)

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
    wspd = np.round(windDF['WindSpeedAvg [kts]'].to_numpy()[-1],1)
    mxsp = np.round(windDF['WindSpeedGst [kts]'].to_numpy()[-1],1)
    # wspd = np.round(2.23694 * windDF['WSPD'].to_numpy()[-1][0],1)
    # mxsp = np.round(2.23694 * windDF['GST'].to_numpy()[-1][0],1)
    if mxsp != mxsp:
      mxsp = '-'
    temp = windDF['AirTemp [°F]'].to_numpy()[-1]
    wdir = windDF['WindDir [°]'].to_numpy()[-1]
    # temp = windDF['AirTemp [°F]'].to_numpy()[-1][0]
    # wdir = windDF['WindSpeedAvg [m/s]'].to_numpy()[-1][0]
    oldmin = np.int32(delta.total_seconds()%60)
    oldhrs = np.int32(delta.total_seconds()/3600)
    logging.info(f"{tme}, {oldhrs}:{oldmin} old, {wspd} kts, {mxsp} kts, {wdir:4.0f}°T, {windDirection(wdir)}, {temp}°F")
    # print(f"{tme}, {oldhrs}:{oldmin} old, {wspd} kts, {mxsp} kts, {wdir:4.0f}°T, {windDirection(wdir)}, {temp}°F")

    plt.text(0.99, 0.90, f"Last readings spd:{wspd}, max:{mxsp}, dir:{windDirection(wdir)}",
          horizontalalignment='right', verticalalignment='center',
          transform=ax.transAxes, color='blue', alpha=0.6 )
    if oldhrs > 1 and oldmin > 30:
      plt.text(0.99, 0.84, f"Warning {oldhrs}:{oldmin} old",
            horizontalalignment='right', verticalalignment='center',
            transform=ax.transAxes, color='darkred', alpha=0.6 )

    #   fig.show()
    fig.savefig(imageRef, bbox_inches='tight', transparent=True)
    plt.close(fig)

def windDirection(ang):
    # direction indexer
    labels = {
      'N': (348.75, 11.25), 'NNE': (11.25, 33.75),   'NE': (33.75, 56.25),   'ENE': (56.25, 78.75),
      'E': (78.75, 101.25), 'ESE': (101.25, 123.75), 'SE': (123.75, 146.25), 'SSE': (146.25, 168.75),
      'S': (168.75, 191.25),'SSW': (191.25, 213.75), 'SW': (213.75, 236.25), 'WSW': (236.25, 258.75),
      'W': (258.75, 281.25),'WNW': (281.25, 303.75), 'NW': (303.75, 326.25), 'NNW': (326.25, 348.75),
    }
    for tag, (min_ang, max_ang) in labels.items():
        if tag == 'N':  # Special case for North, which wraps around
            if ang > min_ang or ang <= max_ang:
                return tag
        else:
            if min_ang < ang <= max_ang:
                return tag
    return '-?-'

def main():
    # Retrieve the OCR data for execution rocks.
    source = pathToResources + "wind_data.csv"
    dest   = pathToImages + "windGraph.png" # desitnation for the graph, but also the source of the data (since it's generated locally from the csv)

    logging.info(f"\t...source: {source}")

    windDF = fetchWindData(source)

    logging.debug(windDF.head())
    logging.debug('...')
    logging.debug(windDF.tail())

    logging.info(f"\t...destination: {dest}")
    makeWindGraph(windDF, "Execution Rocks" )

    logging.info('\t...done')

    # This is a CGI script, so we need to print the content type header and a blank line before the output.
    print('Content-Type: text/plain\n')
    print('windGraph done.')

if __name__ == '__main__':
    prog = 'WindGraph    '
    logging.basicConfig(filename='WeatherKiosk.log', format=f'%(levelname)s:\t%(asctime)s\t{prog}\t%(message)s', level=logging.INFO)
    logging.info('Build wind graph...')
    main()
