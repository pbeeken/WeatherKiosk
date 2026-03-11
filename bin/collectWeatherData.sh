#!/bin/bash
# NOTE THAT THIS CANNOT RUN ON DEVELOPER ENVIRONMENT. ONLY ON THE RASBERRY PI.
# Get wind or wave data based on the command line switch
# Define the valid options (e.g., 'a' and 'b')
# The leading colon ':' enables silent error reporting
cd /home/pi/WeatherKiosk/bin

SOURCE="exrx"
WAVE_ENABLED=false
WIND_ENABLED=false

# Loop through all arguments provided to the script
while [[ "$#" -gt 0 ]]; do
    case $1 in
        # gather wind data
        -z|--wind)
            echo "Getting wind data from ${@: -1} via OCR"
            WIND_ENABLED=true
            shift # Move to the next argument
            ;;
        -w|--wave)
            echo "Getting wave data from ${@: -1} via OCR"
            WAVE_ENABLED=true
            shift # Move to the next argument
            ;;
	exrx|wlis|clis|all)
            SOURCE=$1
            shift # Move to the next argument
            ;;
        *)
            # Handle unknown options or stop parsing
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -n "$1" ]; then
    SOURCE="$1"
fi

if [ $WAVE_ENABLED = true ]; then
     /bin/python3 captureBuoyData.py -w -s $SOURCE
fi

if [ $WIND_ENABLED = true ]; then
     /bin/python3 captureBuoyData.py -z -s $SOURCE
fi
