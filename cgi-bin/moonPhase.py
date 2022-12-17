#!/usr/bin/env python3

# Launch the following simple server
# python -m http.server --bind localhost --cgi 8000

import cgi
import json
import numpy as np
import matplotlib.pyplot as plt
import os
import logging

pathToResources = "resources/"

##
# make a cartoon of a moon with beta % lit
# param beta is %lit.  -1<0 (waning) to 0 (new moon) to 0<1 (waxing)
##
def makeMoonLune(beta):
  logging.debug(f"\tgenerating lune: {beta}")

  t = np.linspace(0.0, 1.0, 100)

  def circFunc(t):
    return (np.sin(np.pi * t), np.cos(np.pi * t))

  def ellipFunc(t, b=0.0):
    if b>0:
      dir = -1.0
    else:
      dir = 1.0
    return (dir * 2 * (np.abs(b)-1/2) * np.sin(np.pi * t), np.cos(np.pi * t)) # was b <- np.cos(np.pi * b)

  plt.axes().set_aspect('equal')
  plt.xlim(left=-1.0, right=1.0)
  plt.ylim(bottom=-1.0, top=1.0)

  (xc, yc) = circFunc(t)
  plt.plot(xc, yc, "0.0")   # right half
  plt.plot(-xc, yc, "0.0")  # left half

  (xe, ye) = ellipFunc(t, beta)
  plt.plot(xe, ye, "0.2")
  if beta<=0:
    plt.fill_betweenx(yc, -xc, xe, facecolor="0.9")
    plt.fill_betweenx(yc, xe, xc, facecolor="0.1")
  else:
    plt.fill_betweenx(yc, -xc, xe, facecolor="0.1")
    plt.fill_betweenx(yc, xe, xc, facecolor="0.9")

  plt.axis('off')


###
# Entrypoint for the call. expected optional parameters for cgi-call are:
# fracillum=##
# stage=Waxing | Waning | Full | New | Last
# filename=
# coords=-###.###,+###.###
###
if __name__ == '__main__':                                                               #01234567890123
    logging.basicConfig(filename='WeatherKiosk.log', format='%(levelname)s:\t%(asctime)s\tmoonPhase     \t%(message)s', level=logging.INFO)

    fs = cgi.FieldStorage()  # this is a dictionary of storage objects not strings!
    # e.g. fs = { 'fracillum':   "23%", 'stage': "Waxing", 'filename': "moon_today.svg" }
    logging.info(f"\tfield storage: {fs}")

    # phase and fracillum is passed from javascript
    stage = ""
    fracillum = 0.5
    filename = pathToResources + "moon.svg"
    result = {'rc': 400, 'filename': filename, 'fracillum': fracillum, 'stage': stage, 'error':""}

    if "fracillum" in fs:
        fracillum = fs['fracillum'].value
        fracillum = int(fracillum)/100.  # drop the '%' and convert to fraction
        result['fracillium'] = fracillum
        logging.debug(f"\tfracillum updated: {fracillum}")

    if "stage" in fs:
        stage = fs['stage'].value
        result['stage'] = stage
        logging.debug(f"\tstage updated: {stage}")

    if "filename" in fs:
        filename = fs['filename'].value
        result['filename'] = pathToResources  + "tmp/" + filename
        logging.debug(f"\tfilename updated: {filename}")

    if stage.find("Waning")>=0 or stage.find("Last")>=0:
        fracillum = -fracillum
    else: # Waxing, First, New, Full
        fracillum = fracillum

    try:
        makeMoonLune(fracillum)
        plt.savefig(result['filename'], transparent=True)
        result['rc'] = 200

    except Exception as ex:
        result['rc'] = 400
        result['error'] = f"*{ex}*"

    logging.debug(f"\t json: {result}")
    # Return the content.
    print("Content-Type: application/json\n")
    print(json.dumps(result))

    # We're done here.
