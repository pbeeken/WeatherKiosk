#!/usr/bin/env sh
#
theDay=`date +"%a" --date='05:00 next Fri'`
echo ">>>$theDay<<<"

if [ $theDay = "Fri" ] || [ $theDay = "Sat" ] || [ $theDay = "Sun" ]
then
  echo "Porch Time"

else
  echo "No Need"

fi
