#!/bin/bash
#
# Check in with github to see if there are any updates.
# Save location...
currLoc="`pwd`"
KIOSK="$HOME/WeatherKiosk"

# Move to kiosk folder
cd $KIOSK

# fetch from git any updates
localHash="`git rev-parse HEAD`"
remoteHash="`git rev-parse 'main@{upstream}'`"

# If the hashes don't match
if [ "$localHash" != "$remoteHash" ]; then

    echo "updating..."
    git pull

    echo "copying scripts..."
    # Install scripts, saving old ones.
    cp $HOME/.bashrc $HOME/.bashrc_OLD
    cp $KIOSK/bin/.bashrc $HOME

    cp $HOME/.xinitrc $HOME/.xinitrc_OLD
    cp $KIOSK/bin/.xinitrc $HOME
else

    echo "up to date..."
fi

# ...go back to where we were.
cd $currLoc
