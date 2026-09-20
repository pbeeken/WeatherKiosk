#!/usr/bin/python3

import pandas as pd
import numpy as np

from datetime import datetime, timedelta
import time
import requests
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

# Credentials for Grafana Cloud Loki
import Credentials as cdbs


# Unlike previous implementations we are converting not fetching data.
# def fetchWindData(sourceDF: pd.DataFrame) -> pd.DataFrame:
#     """
#     The dataframe is already fetched from Grafana Cloud Loki.  We just need to massage it into a form that we can graph.
#     """
#     now = datetime.now(tz=EST)
#     logging.info(f"\t...got {len(sourceDF)} data values from {sourceDF.iloc[0]['location']}...")
#     #Remove unneded header and rename columns for clarity
#     #YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE
#     #yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   hPa  degC  degC  degC  nmi  hPa    ft
#     trans = {
#       'timestamp': 'DateTime_UTC',
#       'AirTemp_degC': 'ATMP',
#       # 'AirTemp_degF',
#       'BaromPres_mB': 'PRES',
#       # 'BaromPres_mmHg',
#       'DewPoint_degC': 'DEWP',
#       # 'DewPoint_degF',
#       # 'RelHum_perc',
#       # 'Source',
#       # 'WindDirM24_deg',
#       'WindDir_deg': 'WDIR',
#       # 'WindSpeedAvg_kts',
#       # 'WindSpeedAvg_mph',
#       'WindSpeedAvg_mps': 'WSPD',
#       # 'WindSpeedGst_kts',
#       # 'WindSpeedGst_mph',
#       # 'WindSpeedGst_mps',
#       # 'WindSpeedM24_kts',
#       # 'WindTimeM24',
#       # 'detected_level',
#       # 'device',
#       # 'location',
#       # 'service_name'
#       }
#     sourceDF.rename(columns=trans, inplace=True)

#     # Build DateTime Index column and generate directional components for averaging
#     windDF['DateTime'] = windDF['DateTime_UTC'].dt.tz_convert(EST)
#     windDF = windDF.set_index('DateTime')

#     # Keep only the desired columns
#     windDF = windDF[['WDIR', 'WSPD', 'GST', 'PRES', 'ATMP']]

#     # We need to average the components rather than the angles when resamping.
#     windDF['WdirSin'] = np.sin(np.radians(windDF['WDIR']))
#     windDF['WdirCos'] = np.cos(np.radians(windDF['WDIR']))

#     return windDF

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
    wspd = windDF['WindSpeedAvg_mps'] # windDF['WSPD']
    mxsp = windDF['WindSpeedGst_mps'] # windDF['GST']

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

    ax.grid(True, which='major', linewidth=2,    axis='both', alpha = 0.7)
    ax.grid(True, which='minor', linestyle='--', axis='both', alpha = 0.5)
    ax.set_ylim(bottom=0.0)

    # where did this come from?
    plt.text(0.99, 0.96, f"{whereFrom}",
         horizontalalignment='right', verticalalignment='center',
          transform=ax.transAxes, color='gray', alpha=0.6 )

    ##
    # Put a current conditions slug at the top
    tme = windDF.index[-1]
    wspd = np.round(2.23694 * windDF.iloc[-1]['WindSpeedAvg_mps'],1)
    mxsp = np.round(2.23694 * windDF.iloc[-1]['WindSpeedGst_mps'],1)
    if mxsp != mxsp:
      mxsp = '-'
    temp = windDF.iloc[-1]['AirTemp_degC']
    wdir = np.degrees(
      np.arctan2(windDF.iloc[-1]['WdirCos'],windDF.iloc[-1]['WdirSin']))
      #windDF.iloc[-1]['WDIR']

    old = datetime.now(tz=EST)-tme
    oldmin = np.int32(old.total_seconds()%60)
    oldhrs = np.int32(old.total_seconds()/3600)
    global DATA_AGE_HOURS
    DATA_AGE_HOURS = oldhrs + oldmin/60.0
    logging.debug(f"{tme}, {oldhrs}:{oldmin} old, {wspd} mph, {mxsp} mph, {wdir:4.0f}°T, {temp}°C")

    plt.text(0.99, 0.90, f"Last readings spd:{wspd}, max:{mxsp}, dir:{windDirection(wdir)}",
            horizontalalignment='right', verticalalignment='center',
            transform=ax.transAxes, color='blue', alpha=0.6 )

    if DATA_AGE_HOURS > 0.7: # hours
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

weatherSources = {
  'exrx': 'Execution Rocks',  # Almost due south of HHYC ~1nm.
  'wlis': 'Western LI Sound', # South of Greenwich CT.
  'clis': 'Central LI Sound', # South of Guilford, CT.
  'Kings Point LI': 'https://www.ndbc.noaa.gov/data/realtime2/KPTN6.txt',  # Originally we led with EXR but it's been dead for a while and KPTN6 is the only game in town.
}

def testConnection():
  print("CloudSecrets module imported successfully.")
  print(f"LOKI_URL:        {cdbs.CLD.LOKI_URL}")
  print(f"LOKI_USER:       {cdbs.CLD.LOKI_USER}")
  print(f"LOKI_TOKEN_WRTE: {cdbs.CLD.LOKI_WRTE}")
  print(f"LOKI_TOKEN_READ: {cdbs.CLD.LOKI_READ}")

def fetchData(location="all"):
  LOGQL_QUERY = '{service_name="unknown_service"} | json | logfmt | drop __error__, __error_details__'

  # --- Time range: last 48 hours ---
  end_ns = int(time.time_ns()  + int(20 * 60 * 1e9))  # put the end point 20 min in the future to account for clock skew
  start_ns = end_ns - int(48 * 60 * 60 * 1e9)  # back up 48 hours

  # --- Query Loki directly ---
  url = f"{cdbs.CLD.LOKI_URL}/loki/api/v1/query_range"
  params = {
      "query": LOGQL_QUERY,
      "start": start_ns,
      "end": end_ns,
      "limit": 5000,       # Loki caps results per request; paginate below if you hit this
      "direction": "forward",
  }

  resp = requests.get(url, params=params, auth=(cdbs.CLD.LOKI_USER, cdbs.CLD.LOKI_READ), timeout=30)
  resp.raise_for_status()
  data = resp.json()

  # --- Flatten Loki streams into rows ---
  rows = []
  for stream in data.get("data", {}).get("result", []):
      labels = stream.get("stream", {})
      for ts_ns, line in stream.get("values", []):
          rows.append({
              "timestamp": pd.to_datetime(int(ts_ns), unit="ns", utc=True),
              "line": line,
              **labels,
          })

  # Create the dataframe and sort by timestamp
  df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
  df.set_index("timestamp", inplace=True)

  # 1. Use the following schema to convert columns to appropriate types
  #     any columns commented out or not here will be dropped from the dataframe.
  column_schema = {
    # 'line': "object",
    'AirTemp_degC': "float64",
    'AirTemp_degF': "float64",
    'BaromPres_mB': "float64",
    'BaromPres_mmHg': "float64",
    'DewPoint_degC': "float64",
    'DewPoint_degF': "float64",
    'RelHum_perc': "float64",
    # 'Source': "object",
    'WindDirM24_deg': "float64",
    'WindDir_deg': "float64",
    'WindSpeedAvg_kts': "float64",
    'WindSpeedAvg_mph': "float64",
    'WindSpeedAvg_mps': "float64",
    'WindSpeedGst_kts': "float64",
    'WindSpeedGst_mph': "float64",
    'WindSpeedGst_mps': "float64",
    'WindSpeedM24_kts': "float64",
    'WindTimeM24': "object",
    # 'detected_level': "int64",
    # 'device': "object",
    'location': "object",
    # 'service_name': "object"
    }

  # 3. Filter the dataframe to keep only the columns defined in the schema, plus the timestamp
  # 'timestamp' is always kept as it is the index of the dataframe
  always_keep = []
  columns_to_keep = always_keep + [col for col in column_schema if col in df.columns]

  df = df[columns_to_keep]

  # 4. Safely apply your data types across the entire column at once
  for col, dtype in column_schema.items():
      if col in df.columns:
          if "datetime" in str(dtype):
              df[col] = pd.to_datetime(df[col], utc=True, errors='coerce')
          elif "int" in str(dtype) or "float" in str(dtype):
              # pd.to_numeric supports errors='coerce' to safely turn strings into numbers/NaN
              df[col] = pd.to_numeric(df[col], errors='coerce')

              # Optional: If you explicitly need it as an integer,
              # use 'Int64' (capital I) because standard 'int64' cannot hold NaN values
              if "int" in str(dtype):
                  df[col] = df[col].astype("Int64")
          else:
              df[col] = df[col].astype(dtype, errors='ignore')

  # 5. Ensure the index is in datetime format with UTC timezone
  df.index = pd.to_datetime(df.index, utc=True)  # Make sure the index is in datetime format with UTC timezone

  if location != "all":
      return df[df['location'] == location]

  # return the whole thing if no location filter is applied
  return df

def main():
    now = datetime.now().astimezone(TZ_NY)
    d = timedelta(days = 2)

    # Go through a chain of nearby buoys until we get a good one.
    # I don't want to fail just because one buoy is down.
    # Grafana Cloud Loki has all three buoys in the same log stream so we can just filter by location.
    weatherDF = fetchData()

    # sources = ['exrx', 'wlis', 'clis']
    source = 'exrx'  # For now, just use the Execution Rocks data.  It is our closest source.
    logging.info('\t...source: %s', source)
    weatherDF = weatherDF[weatherDF['location'] == source]

    print(f"Fetched {len(weatherDF)} rows of data for location '{source}'. {weatherDF.index.min()}-{weatherDF.index.max()}")
    lastCaptureDateTime = weatherDF.index.max()
    logging.info(f"\t...last capture {lastCaptureDateTime}")

    graphicalDF = weatherDF[['WindSpeedAvg_mps', 'WindDir_deg', 'AirTemp_degC', 'WindSpeedGst_mps']]
    # # We need to average the components rather than the angles when resamping.
    graphicalDF['WdirSin'] = np.sin(np.radians(graphicalDF['WindDir_deg']))
    graphicalDF['WdirCos'] = np.cos(np.radians(graphicalDF['WindDir_deg']))

    makeWindGraph( graphicalDF.resample('1h').mean(), whereFrom=weatherSources[source] )

    logging.info('\t...done')

    # This is a CGI script, so we need to print the content type header and a blank line before the output.
    print('Content-Type: text/plain\n')
    print(f"SUCCESS: Wind graph generated from data captured '{DATA_AGE_HOURS:0.1f}' hours ago.\n")
    print('windGraphGRF done.')

if __name__ == '__main__':
    prog = 'WindGraphGRF '
    logging.basicConfig(filename= pathToLogs / 'WeatherKiosk.log', format=f'%(levelname)s:\t%(asctime)s\t{prog}\t%(message)s', level=logging.INFO)
    logging.info('Build wind graph...')
    main()
