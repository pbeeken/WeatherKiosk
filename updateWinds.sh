#!/bin/bash
# This should get run once every 15 minutes

# lets make this our home
cd /home/pi/TideClock/

#update the winds graph
python ./WindGraph.py

#update the forecast
python ./Forecast.py
