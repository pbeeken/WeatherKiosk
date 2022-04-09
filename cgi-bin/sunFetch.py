#!/usr/bin/env python3

# Launch the following simple server
# python -m http.server --bind localhost --cgi 8000

import json
import cgi
# A logging tool for debugging.
# dbgReport = None

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
    date = theDate.strftime("%m/%d/%Y")
    dst = isDST(theDate)
    id = "HHYC_019E3"

    url = f"https://aa.usno.navy.mil/api/rstt/oneday?id={id}&date={date}&coords={latlong}&tz={timezone}&dst={dst}"
    # dbgReport.write(f"--- {url}\r")

    # store the response of URL
    response = urlopen(url)

    # storing the JSON response from url in data
    return json.loads(response.read())

###
# Entrypoint for the call. expected optional parameters for cgi-call are:
# date=mm/dd/yyyy
# coords=-###.###,+###.###
# tz=-5
###
if __name__ == '__main__':
#   first fetch the strings passed to us with the fields outlined
    fs = cgi.FieldStorage()  # this is a dictionary of storage objects not strings!

    # simulated input comment the next 4 lines when running standalone... fix the '.value' entries below.
    # fs = { "date":   "2/5/2022", "coords": "40.93,-73.76", }
    # simulated output
    #    result = { "apiversion": "3.0.0", 
    #           "geometry": {"coordinates": [-73.76, 40.93], "type": "Point"}, 
    #           "properties": {"data": {
    #                                 "closestphase": {"day": 8, "month": 2, "phase": "First Quarter", "time": "08:50", "year": 2022}, 
    #                                 "curphase": "Waxing Crescent", "day": 5, "day_of_week": "Saturday", "fracillum": "23%", "isdst": false, "label": null, "month": 2, 
    #                                 "moondata": [{"phen": "Rise", "time": "09:40"}, 
    #                                              {"phen": "Upper Transit", "time": "15:57"}, 
    #                                              {"phen": "Set", "time": "22:24"}], 
    #                                 "sundata": [{"phen": "Begin Civil Twilight", "time": "06:33"}, 
    #                                             {"phen": "Rise", "time": "07:01"}, 
    #                                             {"phen": "Upper Transit", "time": "12:09"}, 
    #                                             {"phen": "Set", "time": "17:17"}, 
    #                                             {"phen": "End Civil Twilight", "time": "17:46"}], 
    #                                 "tz": -5.0, "year": 2022}}, 
    #                                 "type": "Feature"}
    # dbgReport = open("sunFetch.log", "w+")
    # dbgReport.write("--- START ---\r")


    theDate = datetime.now(tz=EST)

    coord = "40.93,-73.76"  # default location
    tz = "-5" # default timezone

    if "date" in fs:
        passedDate = fs['date'].value
        theDate = datetime.strptime(passedDate, "%m/%d/%Y").replace(tzinfo=EST)
    
    if "coords" in fs:
        coord = fs['coords'].value
    
    if "tz" in fs:
        tz = fs['tz'].value

    # dbgReport.write(f"---{theDate}\r")
    # dbgReport.write(f"---{coord}\r")
    # dbgReport.write(f"---{tz}\r")

    result = fetchOneDayData(theDate, latlong=coord, timezone=tz)

    # dbgReport.write(json.dumps(result))
    # dbgReport.close()

    print("Content-Type: application/json\n")
    print(json.dumps(result))