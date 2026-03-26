#!/usr/bin/env sh
#
# keep the screen alive at all times
xset -dpms
xset s off
xset s noblank

# start in $HOME
cd /home/pi
# tool to remove idle mouse from screen after a delay
unclutter &

# rotate the log files
# savelog -l -n -c 8 WeatherKiosk/WeatherKiosk.log
# Move old log files to logs directory  (eventually we we will fix the individual log files to do this automatically, but this is a quick fix for now)
# mv WeatherKiosk.log.* resources/logs/
#

# NUCLEAR STARTUP
# Define the profile path (usually ~/.config/chromium/Default)
PROFILE_DIR="$HOME/.config/chromium/Default"

# 1. Clear the persistent cache and GPU shader cache
rm -rf "$PROFILE_DIR/Cache"/*
rm -rf "$PROFILE_DIR/Code Cache"/*
rm -rf "$PROFILE_DIR/GPUCache"/*

# 2. Reset the session state to prevent "Restore Pages" dialogs
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' "$PROFILE_DIR/Preferences"
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' "$PROFILE_DIR/Preferences"

# default directory
cd /home/pi/WeatherKiosk

#
# launch browser in kiosk mode (F12 will NOT bring up developer environment)
chromium-browser \
	http://localhost:8000/WeatherKiosk.html \
	--window-size=1440,900 --window-position=0,0 \
	--start-fullscreen --kiosk \
	--disk-cache-dir=/dev/null \
        --no-first-run --noerrdialogs
	# doesn't seem to be needed. Not clear what it gives me.
	# --no-first-run --noerrdialogs --disable-infobars \
	# This would be cool but it doesn't seem to work (incompatable with kiosk mode?)
	# --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0
