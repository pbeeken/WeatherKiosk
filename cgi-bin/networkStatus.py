#!/bin/python
"""
  Former bash shell, python is more cross platform
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
"""
from urllib.request import urlopen
from urllib.error import URLError
import logging

def isUp(url=None):
  if url is None:
    url = 'https://8.8.8.8'
  try:
    urlopen(url, timeout=1)
    return True
  except URLError as err:
    return False

import socket

def isUpAlt(host="8.8.8.8", port=53, timeout=2):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        return False

if __name__ == '__main__':
    	prog = "networkStatus   "
	logging.basicConfig(filename='WeatherKiosk.log', format='%(levelname)s:\t%(asctime)s\t{prog}\t%(message)s', level=logging.INFO)

    if isUpAlt():
        status = "&#11014; UP"
    else:
        status = "&#11015; DN"
    logging.info(f"status: {status}")

    print("Content-Type: text/plain\n")
    print(f"networkStatus {status}")
