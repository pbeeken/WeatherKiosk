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
	chromium-browser http://localhost:8000/WeatherKiosk.html https://radar.weather.gov/?settings=v1_eyJhZ2VuZGEiOnsiaWQiOiJsb2NhbCIsImNlbnRlciI6Wy03My41NTMsNDAuODYyXSwibG9jYXRpb24iOm51bGwsInpvb20iOjEwLCJmaWx0ZXIiOiJXU1ItODhEIiwibGF5ZXIiOiJicmVmX3JhdyIsInN0YXRpb24iOiJLRU5YIn0sImFuaW1hdGluZyI6ZmFsc2UsImJhc2UiOiJzdGFuZGFyZCIsImFydGNjIjpmYWxzZSwiY291bnR5IjpmYWxzZSwiY3dhIjpmYWxzZSwicmZjIjpmYWxzZSwic3RhdGUiOmZhbHNlLCJtZW51Ijp0cnVlLCJzaG9ydEZ1c2VkT25seSI6dHJ1ZSwib3BhY2l0eSI6eyJhbGVydHMiOjAuOCwibG9jYWwiOjAuNiwibG9jYWxTdGF0aW9ucyI6MC44LCJuYXRpb25hbCI6MC42fX0%3D#/ http://localhost:8000/BoatReservations.html  http://localhost:8000/PorchReservations.html\
		--window-size=1440,900 --window-position=0,0 --start-fullscreen \
		--disk-cache-dir=/dev/null \
	    --kiosk --start-fullscreen \
	#        --no-first-run --noerrdialogs \
	#        --disable-infobars
else
	# cd /home/pi/WeatherKiosk
	chromium-browser http://localhost:8000/WeatherKiosk.html https://radar.weather.gov/?settings=v1_eyJhZ2VuZGEiOnsiaWQiOiJsb2NhbCIsImNlbnRlciI6Wy03My41NTMsNDAuODYyXSwibG9jYXRpb24iOm51bGwsInpvb20iOjEwLCJmaWx0ZXIiOiJXU1ItODhEIiwibGF5ZXIiOiJicmVmX3JhdyIsInN0YXRpb24iOiJLRU5YIn0sImFuaW1hdGluZyI6ZmFsc2UsImJhc2UiOiJzdGFuZGFyZCIsImFydGNjIjpmYWxzZSwiY291bnR5IjpmYWxzZSwiY3dhIjpmYWxzZSwicmZjIjpmYWxzZSwic3RhdGUiOmZhbHNlLCJtZW51Ijp0cnVlLCJzaG9ydEZ1c2VkT25seSI6dHJ1ZSwib3BhY2l0eSI6eyJhbGVydHMiOjAuOCwibG9jYWwiOjAuNiwibG9jYWxTdGF0aW9ucyI6MC44LCJuYXRpb25hbCI6MC42fX0%3D#/\
		--window-size=1440,900 --window-position=0,0 --start-fullscreen \
		--disk-cache-dir=/dev/null \
	    --kiosk --start-fullscreen \
	#        --no-first-run --noerrdialogs \
	#        --disable-infobars
fi
