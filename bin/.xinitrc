#!/usr/bin/env sh
#
xset -dpms
xset s off
xset s noblank

# sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' ~/.config/chromium/Default/Preferences
# sed -i 's/"exit_type":"Crashed"/"exit_type": "Normal"/' ~/.config/chromium/Default/Preferences

cd /home/pi
unclutter &
testRotate

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
