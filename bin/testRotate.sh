#!/bin/bash
pid=0`pidof unclutter`
if [ $pid -gt 0 ]; then
  echo "unclutter operational"
else
  echo "launching unclutter..."
  unclutter &
fi

pid=0`pidof -x rotateTabs.sh`
if [ $pid -gt 0 ]; then
  echo "rotateTabs operational"
else
  echo "launching rotateTabs..."
  /home/pi/WeatherKiosk/bin/rotateTabs.sh &
fi

echo 0
