#!/usr/bin/env python3

# Launch the following simple server
# python -m http.server --bind localhost --cgi 8000

import json
import cgi
import ssl
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
        return "true"
    return "false"

###
#  Fetch the data from the data from the USNO server
###
def fetchOneDayData(theDate, latlong="40.93,-73.76", timezone="-5"):
    date = theDate.strftime("%Y-%m-%d")
    dst = isDST(theDate)
    id = "HHYC_WK"

    url = f"https://aa.usno.navy.mil/api/rstt/oneday?id={id}&date={date}&coords={latlong}&tz={timezone}&dst={dst}"
    logging.debug(f"\turl sent: {url}")

    # store the response of URL
    ssl._create_default_https_context = ssl._create_unverified_context  # A logging tool for debugging.
    response = urlopen(url)
    logging.debug(f"\tresponse status: {response.status}")

    # storing the JSON response from url in data
    return json.loads(response.read())

###
# Entrypoint for the call. expected optional parameters for cgi-call are:
# date=mm/dd/yyyy
# coords=-###.###,+###.###
# tz=-5
###
if __name__ == '__main__':
    prog = "usNavObsData "
    logging.basicConfig(filename=f'WeatherKiosk.log', format='%(levelname)s:\t%(asctime)s\t{prog}\t%(message)s', level=logging.DEBUG)

    #   first fetch the strings passed to us with the fields outlined
    fs = cgi.FieldStorage()  # this is a dictionary of storage objects not strings!
    logging.info(f"\tfield storage: {fs}")

    # default values
    theDate = datetime.now(tz=EST)
    coord = "40.93,-73.76"  # default location
    tz = "-5" # default timezone

    if "date" in fs:
        passedDate = fs['date'].value
        theDate = datetime.strptime(passedDate, "%m/%d/%Y").replace(tzinfo=EST)
        logging.debug(f"\tdate updated: {theDate}")

    if "coords" in fs:
        coord = fs['coords'].value
        logging.debug(f"\tcoord updated: {coord}")

    if "tz" in fs:
        tz = fs['tz'].value
        logging.debug(f"\ttz updated: {tz}")

    result = fetchOneDayData(theDate, latlong=coord, timezone=tz)
    logging.debug(f"\t json: {result}")

    # Return the content.
    print("Content-Type: application/json\n")
    print(json.dumps(result))

    # We're done here.
