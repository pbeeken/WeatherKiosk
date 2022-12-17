#@title test of gathering wind data.
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from datetime import datetime, date, time, timedelta
from pytz import timezone  # should already be part of pandas but it doesn't hurt to do it again.
import logging

EST = timezone('America/New_York')
UTC = timezone('UTC')

import matplotlib.transforms
import matplotlib.dates as mdates

pathToResources = 'resources/'

# Getting Weather Data from execution rocks (station 44022)  Only needs to run every 15 minutes.

def fetchWindData(source):
  now = datetime.now(tz=EST)

  windDF = pd.read_csv(source, delim_whitespace=True, header=[0,1], na_values='MM', nrows=450 )
  logging.info(f"\t...got {len(windDF)} data values")

  windDF['DateTime'] = windDF[['#YY','MM','DD','hh','mm']].apply(lambda dt: datetime(dt[0], dt[1], dt[2], dt[3], dt[4], tzinfo=UTC).astimezone(EST), axis=1)
  windDF['Time'] = windDF['DateTime'].apply(lambda t: t.time())
  windDF['Date'] = windDF['DateTime'].apply(lambda d: d.date())

  # We need to average the components rather than the angles when resamping.
  windDF['WdirSin'] = np.sin(np.radians(windDF['WDIR']))
  windDF['WdirCos'] = np.cos(np.radians(windDF['WDIR']))

  return windDF #.set_index(windDF['DateTime'] - windDF['DateTime'].min()) # returns a new copy
#  return windDF.set_index('DateTime')

def makeWindGraph(windDF, whereFrom=""):
  if len(windDF) < 16:
    raise BaseException('Not enough points')

  imageRef = pathToResources  + 'tmp/' + 'windGraph.png' # fetch locally (way faster on a pi)
  fig, ax = plt.subplots(figsize=(8, 4))

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
  wspd = np.round(2.23694 * windDF['WSPD'].to_numpy()[-1][0],1)
  mxsp = np.round(2.23694 * windDF['GST'].to_numpy()[-1][0],1)
  if mxsp != mxsp:
    mxsp = '-'
  temp = windDF['ATMP'].to_numpy()[-1][0]
  wdir = windDF['WDIR'].to_numpy()[-1][0]
  old = datetime.now(tz=EST)-tme
  oldmin = np.int32(old.total_seconds()%60)
  oldhrs = np.int32(old.total_seconds()/3600)
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
real_EXR_TimeDataFile = 'https://www.ndbc.noaa.gov/data/realtime2/44022.txt'
# Kings Point
real_KPH_TimeDataFile = 'https://www.ndbc.noaa.gov/data/realtime2/KPTN6.txt'
# Western Long Island Sound
real_WLI_TimeDataFile = 'https://www.ndbc.noaa.gov/data/realtime2/44040.txt'


if __name__ == '__main__':
    prog = 'WindGraph    '
    logging.basicConfig(filename='WeatherKiosk.log', format=f'%(levelname)s:\t%(asctime)s\t{prog}\t%(message)s', level=logging.INFO)
    logging.info('Build wind graph...')

    now = datetime.now().astimezone(EST)
    d = timedelta(days = 2)

    # try to get execution rocks
    try:
      source = 'Execution Rocks'
      # raise NameError('Skip')
      logging.info(f"\t...source: {source}")
      theDF = fetchWindData(real_EXR_TimeDataFile)
      smpl = theDF['DateTime'] > (now - d)
      makeWindGraph( theDF[smpl].resample('1H', on='DateTime').mean(), source )
    except:
      logging.info('\t... failed')
      # if that fails then try western LI buoy
      try:
        source = 'Western LI'
        # raise NameError('Skip')
        logging.info(f"\t...source: {source}")
        theDF = fetchWindData(real_WLI_TimeDataFile)
        smpl = theDF['DateTime'] > (now - d)
        makeWindGraph( theDF[smpl].resample('1H', on='DateTime').mean(), source )
      except:
        logging.info('\t... failed')
        # if that fails then settle on Kings Point (never fails)
        source = 'Kings Point LI'
        logging.info(f"\t...source: {source}")
        theDF = fetchWindData(real_KPH_TimeDataFile)
        smpl = theDF['DateTime'] > (now - d)
        makeWindGraph( theDF[smpl].resample('1H', on='DateTime').mean(), source )

    logging.info('\t...done')

    print('Content-Type: text/plain\n')
    print('windGraph done.')
