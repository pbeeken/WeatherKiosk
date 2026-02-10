#!/bin/bash
#
# Full shutdown and restart the machine remotely from ssh login.
# Takes about 2-3 minutes to completely restart with kiosk running
#
# Find the one running instance of x-window
export DISPLAY=:0

# unclutter needs to be running
pid=0`pidof unclutter`
if [ $pid -ne 0 ]; then
  # unlikely but safe to check
  unclutter &
  sleep 2
fi

# Kill the browser
xdotool key Alt+F4

# This delays startup so networking can begin.
read -t 10 -p "Wait 10 seconds so chrome can quit nicely..."

# shutdown with restart
sudo shutdown -r now
