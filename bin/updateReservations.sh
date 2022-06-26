#!/bin/bash
# This should get run once every 5 minutes.
# An interesting idea. Download the published html which seems to get more up to date content. BUT the file isn't formatted quite the same way.

# lets make this our home
# cd /home/pi/WeatherKiosk/reservations

# fetch unit cycle (1 or 2) This allows us to switch displayed units from m to ft (international audience)
#curl "https://docs.google.com/spreadsheets/d/e/2PACX-1vQfkbGPQgtOsolvk6_VMVDx77C31iISIxv74YjIMiCUbOXJa2gbTu1WHXd4B2p2XnrDVZ5VTD1zC9uq/pub?gid=696214441&single=true&output=html" >tmp.html
curl "https://docs.google.com/spreadsheets/d/e/2PACX-1vQfkbGPQgtOsolvk6_VMVDx77C31iISIxv74YjIMiCUbOXJa2gbTu1WHXd4B2p2XnrDVZ5VTD1zC9uq/pub?gid=696214441&single=true&output=html" >tmp.html
sed 's/<head>/<head><meta http-equiv="refresh" content="120"><meta http-Equiv="Cache-Control" Content="no-cache">/' tmp.html >dayboat.html

#curl "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdr-1WqdwRBrSuXwyaLDJg8hURpnU9WDQSA1JWgk-vnsKexrb0INK6dZyl1ToHvQFMwZdxsTvnX8HS/pub?gid=696214441&single=true&output=html" >tmp.html
curl "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdr-1WqdwRBrSuXwyaLDJg8hURpnU9WDQSA1JWgk-vnsKexrb0INK6dZyl1ToHvQFMwZdxsTvnX8HS/pub?gid=696214441&single=true&output=html" >tmp.html
sed 's/<head>/<head><meta http-equiv="refresh" content="120"><meta http-Equiv="Cache-Control" Content="no-cache">/' tmp.html >i18boat.html

rm tmp.html
