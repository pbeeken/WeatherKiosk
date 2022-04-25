#!/usr/bin/env python3

# Launch the following simple server
# python -m http.server --bind localhost --cgi 8000

import json
import cgi
# A logging tool for debugging.
# import cgitb
# cgitb.enable(display=0, logdir="cgi-bin/status.log")

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


###
#  Fetch the data from the data from the USNO server
###
def fetchMoonPhasesData(theDate, numPhases):

    date = theDate.strftime("$Y-%m-%d")
    id = "HHYCtc"

    url = f"https://aa.usno.navy.mil/api/moon/phases/date?id={id}&date={date}&nump={numPhases}"

    # store the response of URL
    response = urlopen(url)

    # storing the JSON response from url in data
    return json.loads(response.read())


###
# Entrypoint for the call.
###
#if __name__ == '__main__':
def main():
    # first fetch the strings passed to us with the fields outlined
    fs = cgi.FieldStorage()  # this is a dictionary of storage objects not strings!
    # simulated input comment the next 4 lines when running standalone... fix the '.value' entries below.
    # fs = { "date": "2/5/2022", "number": 10, }

    theDate = datetime.now(tz=EST)

    coord = "40.93,-73.76"  # default location
    theDate = datetime.now()

    if "date" in fs:
        passedDate = fs['date'].value
        theDate = datetime.strptime(passedDate, "%m/%d/%Y").replace(tzinfo=EST)
    
    if "number" in fs:
        coord = fs['number'].value

    result = fetchMoonPhasesData(theDate, coord)

    # dmp = json.dumps(result)

    print("Content-Type: application/json\n")
    print(result)
