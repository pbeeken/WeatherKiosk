#!/bin/bash
# unclutter needs to be running
export DISPLAY=:0
while sleep 30; do
  xdotool key Ctrl+Tab
done
