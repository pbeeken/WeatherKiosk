#!/usr/bin/python

import numpy as np
from html.parser import HTMLParser
import logging

import os
import sys

pathToResources = "resources/"

"""
MarineHTMLParser
    custom extension of HTMLParser to extract informaion from
    NOAA/NWS Marine Forecasts
"""
class MarineHTMLParser(HTMLParser):
  """
    custom class to parse the marine weather forecast for our area
  """
  # an array of dictionaries
  forecasts = []

  def __init__(self):
    """
        init the parser elements
    """
    super(MarineHTMLParser, self).__init__()
    self.inPreString = False
    self.forecast = dict()

  def handle_starttag(self, tag, attrs):
    """
      handle any starting html tag, we are only looking for the <pre> tags
      we initialize the forecast dictionary and the data counter index
    """
    if tag.lower() == "pre":
      self.inPreString = True
      self.forecast = dict()
      self.count = 0

  def handle_endtag(self, tag):
    """
      handle the closing </pre> tag and add the dict to the array
    """
    if tag.lower() == "pre":
      if self.inPreString:  # obviously
        self.forecasts.append(self.forecast)
        self.inPreString = False

  def handle_data(self, data):
    """
      this is the business end, there are a series of data elements
      (I play the cards I'm dealt) the first is a REGION while the second
      is a SYNOPSIS slug, the third is the OVERVIEW. Subsequent data
      pieces are a sequence of TIME and ADVISORY sequences which seem to
      number around 11.
    """
    if self.inPreString:
      if self.count == 0:
        self.forecast['REGION'] = data.strip()
      elif self.count > 0 and self.count % 2 == 1:
        idx = f"TIME{int((self.count+1)/2):02d}"
        self.forecast[idx] = data.strip()
      else:
        idx = f"ADVISORY{int((self.count)/2):02d}"
        self.forecast[idx] = data.strip().replace('\n',' ')
      self.count += 1


"""
We want to run this command peridoically to update the clock. I run it within python
we run the risk of memory leaks so I will run it from a fork from the kisok
"""
if __name__ == '__main__':                                                               #01234567890123
    prog = "Forecast     "
    logging.basicConfig(filename='WeatherKiosk.log', format=f'%(levelname)s:\t%(asctime)s\t{prog}\t%(message)s', level=logging.INFO)
    logging.info("Build marine forecast table...")

    forecastFile = "forecastGrid.html"
    templateFile = "_" + forecastFile

    # url of marine forecast in our area
    url = "https://www.ndbc.noaa.gov/data/Forecasts/FZUS51.KOKX.html"

    # creating HTTP response object from given url
    parser = MarineHTMLParser()

    import urllib.request
    with urllib.request.urlopen(url) as resp:
        parser.feed(resp.read().decode("utf-8"))

    """
    The first record is special, it contains general information about the region
    """
    logging.info(parser.forecasts[0]['REGION']) # Official designation for covered area
    logging.info(parser.forecasts[0]['TIME01']) # Short version of location
    logging.info(parser.forecasts[0]['ADVISORY01']) # Reason for following forecasts

    """
    The subsequent records follow the pattern of REGION and a sequence of
    Times and Advisories
    """
#    for j in range(len(parser.forecasts)):

    designation = (parser.forecasts[6]['REGION']).replace('\n',' ').split('- ')
    try:
        specialWarning = designation[2].split("...")[1]
        designation[2] = designation[2].split("...")[0]
    except:
        specialWarning = ""

            # Off. designation for covered area
    titleArea = f'''
        <p class="where">{designation[1]}</p>
        <p class="when">{designation[2]}</p>
        '''
    forecastBox = []
    for i in range(np.min([6, len(parser.forecasts)-1]) ):
        logging.info(parser.forecasts[6][f"TIME{i+1:02d}"]) # Short version of location

        tmeidx = f"TIME{i+1:02d}"
        advidx = f"ADVISORY{i+1:02d}"
        forecastBox.append(f'''
                <p class="what">{parser.forecasts[6][tmeidx]}</h3>
                <p  class="how">{parser.forecasts[6][advidx]}</p>
            ''')

    #open and read the template file
    with open(pathToResources + templateFile, "r") as template:
        templateHtml = template.readlines()

    # Title Information
    templateHtml = ("".join(templateHtml)).replace('<!--Forecast Title-->', titleArea)
    # Forecast Boxes
    for i in range(len(forecastBox)):
        templateHtml = templateHtml.replace(f'<!--Forecast Box_{i}-->', forecastBox[i])

    templateHtml = templateHtml.replace('<!--Special Warning-->', specialWarning)


    # copy the html table into the text and write out a new file
    with open(pathToResources + "tmp/" + forecastFile, "w") as htmlFile:
        htmlFile.write(templateHtml)


    print("Content-Type: text/plain\n")
    print("forecast done.")
