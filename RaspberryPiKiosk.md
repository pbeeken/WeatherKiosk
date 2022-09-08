# Notes on Raspberry Pi kiosk
The concrete mission for me was to build a kiosk weather and tide reporting system for a
small boat club that combined data from various sources (most notably NOAA and NWS) for easy
interpretation for skippers and owners heading out to their craft.

I started by building the system from a full Raspbian OS install and started stripping out
unnecessary apps when I realized what I should have done was build it up from a minimal
insatllation of [Raspbian Lite](https://www.raspberrypi.org/downloads/raspbian/).

I found a number of references on the interweb but the two I found most helpful were
  - [A minimal kiosk mode for a Raspberry Pi](https://blog.r0b.io/post/minimal-rpi-kiosk/) a step by step
  - [Minimal Kiosk OS](https://github.com/TheLastProject/minimalKioskOS) a slimmed down version prebuilt with a lot of security

My setup doesn't have an easy profile and the resources for the display are generated on the fly using periodic
python programs (could have been any language this was just easiest for what I wanted to do.)  Thus the actual connectionion
is through the periodic daemons and not the browser which is just used as a configurable display environment.

## Begin the process
Load a copy of the Rasbian Lite using the installer app on an sd card.
This is a very minimal install so you need to add a windowing system compatible with chromium-browser (X11).

```
sudo raspi-config
```
First run the configuration utility to set the conditions where we are using the kiosk:
  1. System Options       Configure system settings
    - WIFi options (note this doesn't recognize a USB dongle, yet)
  2. Display Options      Configure display settings
    - no need to change anything
  3. Interface Options    Configure connections to peripherals
    - SSH turn on
  4. Performance Options  Configure performance settings
    - no need to change anything
  5. Localisation Options Configure language and regional settings
    - Locale, Timezone, Keyboard, WLAN country
  6. Advanced Options     Configure advanced settings
    - no need to change anything
  8. Update               Update this tool to the latest version
    - update this tool (maybe start here)
  9. About raspi-config   Information about this configuration tool

## Setup the [wifi dongle](https://www.lifewire.com/usb-wifi-adapter-raspberry-pi-4058093#toc-edit-the-network-interfaces-file) (if necessary)
Be sure the ssid matches **exactly**! (*This had me going for a while*)  Consider giving kiosk a fixed IP with a strong pw so you can make mods in the field.

## Install needed components
We need to install a windowing system, chromium browser and some additional tools
```
sudo apt-get install dnsmasq
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install --no-install-recommends xserver-xorg-video-all xserver-xorg-input-all xserver-xorg-core xinit x11-xserver-utils
sudo apt-get install --no-install-recommends chromium-browser unclutter
sudo apt-get install --no-install-recommends xdotool
sudo apt-get install git
```

I also installed the [gh tool](https://github.com/cli/cli/blob/trunk/docs/install_linux.md) to make connection to repositories easy.  We can set up a temporary key to allow downloading of the resources. Be sure to enable the user:read context


```
sudo apt install python3-pandas
# sudo apt install python3-numpy      # installed with above
# sudo apt install python3-matplotlib # installed with above
sudo apt-get install libopenjp2-7
```

## Configure Files

**.bashrc**  at the end of the file...
```bash
PATH=/home/pi/.local/bin:$PATH

if [ -z $DISPLAY ] && [ $(tty) = /dev/tty1 ]
then
   # This prevents the 'crash report' in case there was a power outage.
   sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/pi/.config/chromium/Default/Preferences
   sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/pi/.config/chromium/Default/Preferences
   ./rotatetabs.sh & # doesn't seem to work but is also maintained by crontab
   cd WeatherKiosk/
   # update tables and graphs
   /bin/bash /home/pi/WeatherKiosk/updateTides.sh
   /bin/bash /home/pi/WeatherKiosk/updateWinds.sh
   #launch the server
   python -m http.server --cgi -d WeatherKiosk/ &
   # launch xstart
   startx
fi
```

**.xinitrc**
```bash
#!/usr/bin/env sh
#
xset -dpms
xset s off
xset s noblank

# sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' ~/.config/chromium/Default/Preferences
# sed -i 's/"exit_type":"Crashed"/"exit_type": "Normal"/' ~/.config/chromium/Default/Preferences

cd /home/pi
unclutter &
WeatherKiosk/bin/testRotate.sh

# cd /home/pi/WeatherKiosk
chromium-browser http://localhost:8000/WeatherKiosk.html http://localhost:8000/BoatReservations.html\
        --window-size=1440,900 --window-position=0,0 --start-fullscreen \
        --disk-cache-dir=/dev/null \
        --disable-infobars
#        --kiosk --start-fullscreen \
#        --no-first-run --noerrdialogs \
#        --disable-infobars
```

**.gitconfig**
```
# This is Git's per-user configuration file.
[user]
# Please adapt and uncomment the following lines:
	name = nyname
	email = myemail
[credential "https://github.com"]
	helper =
	helper = !/usr/bin/gh auth git-credential
```

**/etc/wpa_suplicant/wpa_supplicant.conf**  -- sets up the wifi settings
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_conf=1
country=US

network={
	ssid="ssid"
	psk="password"
	key_mgmt=WPA-PSK
}
```

personal cron tab. use `cron -e` from the command line to edit
```
# m h  dom mon dow command
*/5  * * * *          /bin/bash /home/pi/WeatherKiosk/bin/updateTides.sh
2,12,27,32,47 * * * * /bin/bash /home/pi/WeatherKiosk/bin/updateWinds.sh
*/14 * * * *          /bin/bash /home/pi/WeatherKiosk/bin/RotateTabs.sh
45 21 * * *           /bin/bash /home/pi/WeatherKiosk/bin/shutDown.sh
# update ssl libraries  This turned out to be a problem with one info site so we do thie regularly
* * 5,10,15,20,25 * * /usr/lib/python3/dist-packages/pip install certifi --upgrade # update ssl libraries
```

Turn on cron logging `sudo nano /etc/rsyslog.conf` and uncommenting the generation of the log file (really useful for debugging)
