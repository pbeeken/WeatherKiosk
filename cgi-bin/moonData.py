#!/usr/bin/env python3

# python -m http.server --bind localhost --cgi 8000
# python -mwebbrowser http://localhost:8000/cgi-bin/moonData.py
import json
import cgi
import logging

# import urllib library
from urllib.request import urlopen

###
# Time libraries we are very dependant on 'aware' times. Most bugs have been traced back
# to a misunderstanding of how important that times be 'aware'.
from datetime import tzinfo, timedelta, datetime, date
from pytz import timezone  # should already be part of pandas but it doesn't hurt to do it again.
from dateutil import parser
import time
EST = timezone('America/New_York')

##
#  Returns the appropriate string value for the REST call
##
def isDST(theDate):
    earlyDate = datetime(theDate.year, 2, 13, 2, tzinfo=EST)
    lateDate  = datetime(theDate.year, 10, 6, 2, tzinfo=EST)

    if theDate > earlyDate and theDate <= lateDate:
        return -4
    return -5


###
#  Fetch the data from the data from the USNO server
###
def fetchOneDayData(theDate,latlong):

    datestr = theDate.strftime('%Y-%m-%d')
    tz = isDST(theDate)
    id = 'HHYC_WK'

    url = f"https://aa.usno.navy.mil/api/rstt/oneday?date={datestr}&coords={latlong}&tz={tz}"
    logging.debug(f"\turl sent: {url}")

    # store the response of URL
    response = urlopen(url)
    logging.debug(f"\tresponse status: {response.status}")

    # storing the JSON response
    # from url in data
    data_json = json.loads(response.read())

    return data_json

###
# Entrypoint for the call. expected optional parameters for cgi-call are:
# date=mm/dd/yyyy
# coords=-###.###,+###.###
###
if __name__ == '__main__':                                                               #01234567890123
    prog = 'moonData        '
    logging.basicConfig(filename='WeatherKiosk.log', format='%(levelname)s:\t%(asctime)s\t{prog}\t%(message)s', level=logging.INFO)

    fs = cgi.FieldStorage()  # this is a dictionary of storage objects not strings!
    logging.info(f"\tfield storage: {fs}")

    # default values
    theDate = datetime.now(tz=EST)
    coord = '0.0,0.0'

    if 'date' in fs:
        theDate = datetime.strptime(fs['date'].value, '%m/%d/%Y').replace(tzinfo=EST)
        logging.debug(f"\tdate updated: {theDate}")

    if 'coords' in fs:
        coord = fs['coords'].value
        logging.debug(f"\tcoord updated: {coord}")

    result = fetchOneDayData(theDate,coord)
    logging.debug(f"\t json: {result}")

    # Return the content.
    print('Content-Type: application/json\n')
    print(json.dumps(result))
