#!/bin/bash
# This should get run once every 10 minutes

# lets make this our home
cd /home/pi/WeatherKiosk/

# fetch unit cycle (1 or 2) This allows us to switch displayed units from m to ft (international audience)
TIDECNT=$(cat resources/env) || 1

#update variable for unit change
export TIDECNT=$(( (TIDECNT+1) % 2 ))

#update the main graph
python bin/tidesGraph.py
#update the graphic
python bin/tidesGraphic.py
#update the table
python bin/tidesTable.py

# save the state
echo "$TIDECNT" > resources/env
