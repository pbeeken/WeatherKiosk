#!/bin/bash
# This should get run once every 15 minutes

# lets make this our home
cd /home/pi/WeatherKiosk/

#update the winds graph
python bin/WindGraph.py

#update the forecast
python bin/Forecast.py
