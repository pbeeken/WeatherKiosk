#!/bin/bash
#
# This tests if the unclutter daemon is running and launches
# it if it isn't running. rotateTabs needs unclutter to pass
# keystrokes to the foremost application in the xwindow.
# This script will dissapper eventually as we will only have one window
#
pid=0`pidof unclutter`
if [ $pid -gt 0 ]; then
  echo "unclutter operational"
else
  echo "launching unclutter..."
  unclutter &
fi

pid=0$(pidof -x rotateTabs.sh)
if [ $pid -gt 0 ]; then
  echo "rotateTabs operational"
else
  echo "launching rotateTabs..."
  /home/pi/WeatherKiosk/bin/rotateTabs.sh &
fi

echo 0
