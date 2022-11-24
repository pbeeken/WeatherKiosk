#!/bin/bash
# set default address
if [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  addr="$1"
else
  addr="8.8.8.8"
fi
echo "$addr"
# test reachability
status="$(ping $addr -w 1 -c 1 | grep 'packet loss')"
([[ "$status" =~ \ 100\% ]]) && echo "&#11015; DN" || echo "&#11014; UP"
