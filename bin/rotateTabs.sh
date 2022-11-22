#!/bin/bash
# unclutter needs to be running for this script to pass a
# 'next tab' key command to the currently open browser.
# This somewhat inelegant solution does a pretty good job of
# cycling through the open tabs in the browser.
export DISPLAY=:0
while sleep 20; do # every 20 seconds, change. (Based on airport kiosk timing)
  xdotool key Ctrl+Tab
done
