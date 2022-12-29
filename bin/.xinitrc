#!/usr/bin/env sh
#
xset -dpms
xset s off
xset s noblank

# start in $HOME
cd /home/pi
# tool to remove idle mouse from screen after a delay
unclutter &

# rotate the log files
savelog -l -n -c 8 WeatherKiosk/WeatherKiosk.log

#
# default directory
cd /home/pi/WeatherKiosk

#
# launch browser in kiosk mode (F12 will NOT bring up developer environment)
chromium-browser \
	http://localhost:8000/WeatherKiosk.html \
	--window-size=1440,900 --window-position=0,0 \
	--disk-cache-dir=/dev/null  --start-fullscreen --kiosk
	# doesn't seem to be needed. Not clear what it gives me.
	# --no-first-run --noerrdialogs --disable-infobars \
	# This would be cool but it doesn't seem to work (incompatable with kiosk mode?)
	# --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0
