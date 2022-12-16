#!/usr/bin/env python3

# Launch the following simple server
# python -m http.server --bind localhost --cgi 8000

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
def fetchMoonPhasesData(theDate, numPhases):

    date = theDate.strftime("%Y-%m-%d")
    tz = isDST(theDate)
    id = "HHYC_WK"

    url = f"https://aa.usno.navy.mil/api/moon/phases/date?id={id}&date={date}&nump={numPhases}"
    logging.debug(f"\turl sent: {url}")

    # store the response of URL
    response = urlopen(url)
    logging.debug(f"\tresponse status: {response.status}")

    # storing the JSON response from url in data
    return json.loads(response.read())

###
# Entrypoint for the call. expected optional parameters for cgi-call are:
# date=mm/dd/yyyy
# nphases=##
###
if __name__ == '__main__':                                                               #01234567890123
    logging.basicConfig(filename='WeatherKiosk.log', format='%(levelname)s:\t%(asctime)s\tmoonFetch     \t%(message)s', level=logging.DEBUG)

    # first fetch the strings passed to us with the fields outlined
    fs = cgi.FieldStorage()  # this is a dictionary of storage objects not strings!
    logging.info(f"\tfield storage: {fs}")

    # default values
    theDate = datetime.now(tz=EST)
    nPhases = 8  # default numbers

    if "date" in fs:
        theDate = datetime.strptime(fs['date'].value, "%m/%d/%Y").replace(tzinfo=EST)
        logging.debug(f"\tdate updated: {theDate}")

    if "nphases" in fs:
        nPhases = fs['nphases'].value
        logging.debug(f"\tnphases updated: {nPhases}")

    result = fetchMoonPhasesData(theDate, nPhases)
    logging.debug(f"\t json: {result}")

    # Return the content.
    print("Content-Type: application/json\n")
    print(json.dumps(result))

    # We're done here.
