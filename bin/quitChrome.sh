#!/bin/bash
# unclutter needs to be running
pid=0`pidof unclutter`
if [ $pid -ne 0 ]; then
  # unlikely but safe to check
  unclutter &
  sleep 10
fi

# quit gracefully
export DISPLAY=:0
xdotool key Alt+F4
