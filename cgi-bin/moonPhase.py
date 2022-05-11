#!/usr/bin/env python3

# Launch the following simple server
# python -m http.server --bind localhost --cgi 8000

import numpy as np
import matplotlib.pyplot as plt

##
# make a cartoon of a moon with beta % lit
# param beta is %lit.  -1<0 (waning) to 0 (new moon) to 0<1 (waxing)
##
def makeMoonLune(beta):
  t = np.linspace(0.0, 1.0, 100)

  def circFunc(t):
    return (np.sin(np.pi * t), np.cos(np.pi * t))

  def ellipFunc(t, b=0.0):
    if b>0:
      dir = 1.0
    else:
      dir = -1.0
    return (dir *  b * np.sin(np.pi * t), np.cos(np.pi * t))

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
# Entrypoint for cgi
###
if __name__ == '__main__':
  #   first fetch the strings passed to us with the fields outlined
  fs = cgi.FieldStorage()  # this is a dictionary of storage objects not strings!
  # fs = { "fracillum":   "23%", "stage": "waxing" }

  # phase and fracillum is passed from javascript
  stage = ""
  fracillum = 0
  filename = "moon.svg"
  result = {'rc': 400, 'filename': None, 'beta': None, 'stage': None}

  if "fracillum" in fs:
    fracillum = fs['fracillum'].value
    fracillum = int(fracillum)/100.  # drop the '%' and convert to fraction

  if "stage" in fs:
    stage = fs['stage'].value
    result['stage'] = stage

  if "filename" in fs:
    filename = fs['filename'].value
    result['filename'] = filename

  if stage.find("Waning")>=0 or stage.find("Last")>=0:
    fracillum = -fracillum
  else: # Waxing, First, New, Full
    fracillum = fracillum

  result['beta'] = fracillum

  makeMoonLune(fracillum)

  plt.savefig(filename, transparent=True)

  print("Content-Type: application/json\n")
  print(json.dumps(result))
