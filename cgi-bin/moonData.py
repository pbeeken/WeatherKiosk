#!/usr/bin/env python3

# python -m http.server --bind localhost --cgi 8000
# python -mwebbrowser http://localhost:8000/cgi-bin/moonData.py
import json
import cgi
# import cgitb
# cgitb.enable(display=0, logdir="cgi-bin/status.log")

# import urllib library
from urllib.request import urlopen

fo = ""
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

    datestr = theDate.strftime("%m/%d/%Y")
    tz = isDST(theDate)

    url = f"https://aa.usno.navy.mil/api/rstt/oneday?date={datestr}&coords={latlong}&tz={tz}"
    # fo.write(f"--- {url}\r")
    # store the response of URL
    response = urlopen(url)
    
    # storing the JSON response 
    # from url in data
    data_json = json.loads(response.read())

    return data_json

###
# Entrypoint for the call.
###
if __name__ == '__main__':

    fs = cgi.FieldStorage()  # this is a dictionary of storage objects not strings!
    theDate = datetime.now(tz=EST)
#    timeZone = 0 since we know our time zone we will work out EDT/EST from the date
    coord = "0.0,0.0"

    # fo = open("status.log", "w+")
    # fo.write("--- START ---\r")

    # if "tz" in fs:
    #     timeZone = fs['tz'].value

    if "date" in fs:
        theDate = datetime.strptime(fs['date'].value, "%m/%d/%Y").replace(tzinfo=EST)
    
    if "coords" in fs:
        coord = fs['coords'].value

    # fo.write(f"---{timeZone}\r")
    # fo.write(f"---{theDate}\r")
    # fo.write(f"---{coord}\r")
    # for (k,v) in fs.keys():
    #     fo.write(f"---{k}:{v.value}")
    #     if k.lower() == "date":
    #         theDate = datetime.strptime(v.value,"%m/%d/%Y").replace(tzinfo=EST)
    #     if k.lower() == "coords":
    #         coord = v.value
    #     if k.lower() == "tz":
    #         timeZone = v.value

    result = fetchOneDayData(theDate,coord)

    dmp = json.dumps(result)
    # fo.write(f"{dmp}\r")
    # fo.close()

    print("Content-Type: application/json\n")
    print(dmp)