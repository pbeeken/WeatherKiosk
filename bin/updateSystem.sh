#!/bin/bash
#
# Check in with github to see if there are any updates.
# Save location...
currLoc="$(pwd)"
KIOSK="$HOME/WeatherKiosk"

# Move to kiosk folder
cd $KIOSK
git fetch -a # update from upstream (nothing is overwritten)

# fetch from git any updates
remoteBranch="`git rev-parse --symbolic-full-name --abbrev-ref @{upstream}`"
localHash="`git rev-parse HEAD`"
remoteHash="`git rev-parse '@{upstream}'`"

# If the hashes don't match
if [ "$localHash" != "$remoteHash" ]; then

    echo "updating..."
    # we don't care about any changes on the pi; we discard them.
    # reset the pointer to ignore any changes (made accidentally?)
    #git reset --hard origin/main
    git pull --force

    echo "copying scripts..."
    # Install scripts, saving old ones.
    cp $HOME/.bashrc $HOME/.bashrc_OLD
    cp $KIOSK/bin/.bashrc $HOME

    cp $HOME/.xinitrc $HOME/.xinitrc_OLD
    cp $KIOSK/bin/.xinitrc $HOME
else

    echo "up to date..."
fi

# Update executable tags on linux
# This is an important step as if the cgi-bin scripts fail,
# the whole kiosk fails. This guarantees that this is never an issue.
echo "updating exec mode on scripts..."
chmod 755 $KIOSK/bin/*.sh
chmod 755 $KIOSK/cgi-bin/*.py

# ...go back to where we were.
cd $currLoc
