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
# theDay=$(date +"%a")
#if [ $theDay = "Fri" ] || [ $theDay = "Sat" ] || [ $theDay = "Sun" ]
#then
cd /home/pi/WeatherKiosk

chromium-browser \
	http://localhost:8000/WeatherKiosk.html \
	--window-size=1440,900 --window-position=0,0 --start-fullscreen \
	--disk-cache-dir=/dev/null  --start-fullscreen --kiosk
	# --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0
	#        --no-first-run --noerrdialogs \
	#        --disable-infobars
