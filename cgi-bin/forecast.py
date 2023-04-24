#!/usr/bin/python

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
    self.inForecast = False
    self.inMain = False
    self.inParagraph = False
    self.warning = False
    self.dayMark = False
    self.newEntry = False
    self.forecasts = dict()
    self.forecast = None

  def handle_starttag(self, tag, attrs):
    """
      handle any starting html tag, we are only looking for a div with the attribute 'fcst'
      to start collecting then we accumulate paragraphs afterward.
    """
    tag = tag.lower()

    if tag == 'main':
      # 'main' tag starts the data area
      self.inMain = True
      return

    if not self.inMain:
      return # don't bother doing anything else we don't care!

    if self.inMain and tag == 'div' and self.findAttribute('class', attrs) == 'fcst':
      # 'div' with class='fcst' begins the list of paragraphs with forcasting
      self.inForecast = True
      return

    if not self.inForecast:
      return # don't bother doing anything else we don't care!

    if self.inForecast and tag == 'hr':
      # isolated <hr> tags indicate a seperation between regions use this to flag new regions
      self.newEntry = True
      if self.forecast != None:
        # Store the complete forecast
        self.forecasts[self.forecast['code'][:6]] = self.forecast
      # Create a new empty
      self.forecast = dict()
      return

    if self.inForecast and tag == 'p':
      # begin to collect paragraphs into the dictionary remembering that we can encounter spans and br.
      self.inParagraph = True
      self.breakCount = 0
      if self.findAttribute('class', attrs) == 'warn-highlight':
        # special warning (not always present)
        self.warning = True
      if self.findAttribute('class', attrs) == 'fcst-hdr':
        # one time marker for the codes for this forecast area
        self.masterheader = True

    if tag == 'span' and self.findAttribute('class', attrs) == 'fcst-day':
      self.dayMark = True
      return

    if tag == 'br':
      self.breakCount = 1 + self.breakCount

    return

  def handle_endtag(self, tag):
    """
      handle the closing tags and close any implied hierarchy
    """
    tag = tag.lower()

    if tag == 'main':
      # this is the ultimate end
      self.inMain = False
      self.inForecast = False
      self.inParagraph = False
      self.breakCount = 0
      self.dayMark = False

    if tag == 'div' and self.inForecast:
      # we are in the forecast structure
      self.inForecast = False
      self.inParagraph = False
      self.breakCount = 0
      self.dayMark = False

    if tag == 'p':
      self.inParagraph = False
      self.breakCount = 0
      self.dayMark = False


  def findAttribute(self, kind, attrs):
    """
    Extract the value for an attribute 'type' in the list of attrs provided by
    a 'tag',

    Args:
        type (string): the title of the attribute we wish to extract
        attrs (string): the attrs argument provided from handle_starttag
    """
    for attr in attrs:
      if attr[0].lower() == kind:
        return attr[1]
    return None

  def handle_data(self, data):
    """
      This is where we handle the contents of the tags
      We are processing paragraphs within the forecast div
    """
    if not self.inForecast:
      # Exit we are not in forecast
      return

    if not self.inParagraph:
      # Exit as we are not dealing with paragraph contents.
      return

    data = data.strip()
    if data == "":
      return # nothing to store

    # From here on down we are in a paragraph which may contain internal elements
    if self.masterheader:
      # flagged at entry wuth 'fcst-hdr'
      self.forecasts['header'] = data # get the master header and ignore the code after the <br>
      self.masterheader = False # reset
      return

    # Paragraphs from here on down are not special...
    if self.newEntry:
      # We are in a paragraph right after a horizontal rule
      # This means that we are starting a new regional forecast
      if self.breakCount == 0:
        self.forecast['code'] = data
      elif self.breakCount == 1:
        self.forecast['locale'] = data
      elif self.breakCount == 2:
        self.forecast['datetime'] = data
        self.forecast['days']  = []
        self.newEntry = False  # reset

    if self.warning and self.lasttag == 'p':
      # We have a special warning for this forecast
      self.forecast['warning'] = data # get special warning
      self.warning = False  # reset
      return

    if self.dayMark and self.lasttag=='span':
      # This is a span the next paragraph will be the forecast
      self.report = data

    if self.dayMark and self.lasttag=='br':
      self.forecast['days'].append((self.report, data))
      self.dayMark = False


    # if self.inForecast:
    #   if self.count == 0:
    #     self.forecast['REGION'] = data.strip()
    #   elif self.count > 0 and self.count % 2 == 1:
    #     idx = f"TIME{int((self.count+1)/2):02d}"
    #     self.forecast[idx] = data.strip()
    #   else:
    #     idx = f"ADVISORY{int((self.count)/2):02d}"
    #     self.forecast[idx] = data.strip().replace('\n',' ')
    #   self.count += 1


"""
We want to run this command peridoically to update the clock. I run it within python
we run the risk of memory leaks so I will run it from a fork from the kisok
"""
if __name__ == '__main__':                                                               #01234567890123
    prog = 'Forecast     '
    logging.basicConfig(filename='WeatherKiosk.log', format=f'%(levelname)s:\t%(asctime)s\t{prog}\t%(message)s', level=logging.INFO)
    logging.info("Build marine forecast table...")

    forecastFile = 'forecastGrid.html'
    templateFile = '_' + forecastFile

    # url of marine forecast in our area
    url = 'https://www.ndbc.noaa.gov/data/Forecasts/FZUS51.KOKX.html'

    # creating HTTP response object from given url
    parser = MarineHTMLParser()

    import urllib.request
    with urllib.request.urlopen(url) as resp:
        parser.feed(resp.read().decode("utf-8"))

    """
    The first record is special, it contains general information about the region
    """
    # 'ANZ335': 'Long Island Sound West of New Haven CT/Port Jefferson NY'
    logging.info(parser.forecasts.keys())
    ourForcasts = parser.forecasts['ANZ335']
    logging.info(ourForcasts['locale']) # Official designation for covered area
    logging.info(ourForcasts['datetime']) # Short version of location
    if 'warning' in ourForcasts:
      logging.info(ourForcasts['warning']) # Reason for following forecasts

    """
    The subsequent records follow the pattern of REGION and a sequence of
    Times and Advisories
    """
    # To
#    for j in range(len(parser.forecasts)):

    try:
        specialWarning = ourForcasts['warning']
    except:
        specialWarning = ""

    # Off. designation for covered area
    titleArea = f'''
        <p class="where">{ourForcasts['locale']}</p>
        <p class="when">{ourForcasts['datetime']}</p>
        '''
    forecastBox = []
    for i in range(min([6, len(ourForcasts['days'])-1])):
        logging.info(ourForcasts['days']) # Short version of location

        # tmeidx = f"TIME{i+1:02d}"
        # advidx = f"ADVISORY{i+1:02d}"
        forecastBox.append(f'''
                <p class="what">{ourForcasts['days'][i][0]}</h3>
                <p class="how" >{ourForcasts['days'][i][1]}</p>
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
