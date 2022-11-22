#!/usr/bin/env sh
#
xset -dpms
xset s off
xset s noblank

# start in $HOME
cd /home/pi
unclutter &

theDay=`date +"%a"`

if [ $theDay = "Fri" ] || [ $theDay = "Sat" ] || [ $theDay = "Sun" ]
then
	# cd /home/pi/WeatherKiosk
	chromium-browser \
		http://localhost:8000/WeatherKiosk.html \
		http://localhost:8000/BoatReservations.html  \
		http://localhost:8000/PorchReservations.html \
		--window-size=1440,900 --window-position=0,0 --start-fullscreen \
		--disk-cache-dir=/dev/null \
	    --kiosk --start-fullscreen \
	#        --no-first-run --noerrdialogs \
	#        --disable-infobars
else
	# cd /home/pi/WeatherKiosk
	chromium-browser \
		http://localhost:8000/WeatherKiosk.html \
		http://localhost:8000/BoatReservations.html  \
		--window-size=1440,900 --window-position=0,0 --start-fullscreen \
		--disk-cache-dir=/dev/null \
	    --kiosk --start-fullscreen \
	#        --no-first-run --noerrdialogs \
	#        --disable-infobars
fi
