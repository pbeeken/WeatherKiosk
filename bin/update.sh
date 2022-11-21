#!/bin/bash
# Save location...
set currLoc="`pwd`"

# Move to kiosk folder
cd /home/pi/WeatherKiosk
# fetch from git any updates
git fetch

# copy relevant files from source to operation locations


# ...go back to where we were.
cd $currLoc
