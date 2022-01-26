# Weather Kiosk
This is an experiment to build a tide/weather viewer for a specific location using a Raspberry Pi connected to an old display.
The display will be encased in a weatherproof box an mounted outside a boatyard office. (Assuming everything else goes well)

## Beginnings
This started out as a quick and dirty experiment with a little used older model RasPi B model that I had gotten for a different purpose.
I had an old monitor with a DVI input which I could cheaply adapt to HDMI.  We had a mechanical tide clock that was never accurate at a boat
club where I teach sailing and thought, there has to be a better system.  Discovering that tide information is readily available from NOAA I
decided to give it a try.  I could always fall back on harmonic parameters (also available from NOAA) if the source became unavailable.

This is a complete refactoring of the original design. I learned a lot about html5 layouts and how to to keep screens from blinking and such.

## Methods
Being very comfortable with python, matplotlib, numpy and a desire to learn how to make effective use of pandas dataframes I figured I could
grab the data with a short program, build a graph (.png) and use a web browser to arrange and display the results. I do these projects for the learning experience as much as for anything else.  I didn't want to just pull the data from the website because there is s a bunch of other graphics and materials I didn't want cluttering the screen.  It went so successfully I started to expand the project.

## Considerations
I use a web page that self updates and thus picks up any changes to the graphics.  Once I got the tide part working I realized I had a lot more screen real estate and wanted to provide other useful tidbits.  There are nearby weather buoys which record wind and, in some case, wave information.  The national weather service provides a very elegant REST interface to fetch forcast information, although at the time of this writing no marine forcasts as of yet.  Being a club mostly devoted to stick and rag people this is nice to have to remind people of what conditions are like outside the sheltered cove where we sit.

Another important part to make this project a reality is to turn the whole machine into a 'kiosk' that can be reset by simply turning it off and then on again. This part turned out not to be as straightforward as I originally thought.  It took me a day to get the details right to pull this part of it together.

Finally is the building of a weatherproof case that allows the Pi to not get too hot. (Fortunately the wall where this is likely to be mounted is just inside a covered area out of direct weather.)  For me, this is the easy part.

## Making the $\Pi$ into a kiosk device
There is a [seperate document on this](RaspberryPiKiosk.md). There is a lot of helpful information out there but, really, every setup is different and each use case requires tinkering, experimentation and testing. After starting with a full copy of Raspbian and peeling away unneeded software, I downgraded to Raspian Lite and built up.  Because I am running python I needed to get a few important libraries installed that worked correctly on a RPi (*hint, don't use pip in this situation, matplotlib, numpy and pandas need to be built specifically for the arm processor*).  Could I have used node? Sure, but because I am gathering data from disparate sources and wanted the convenience of pandas' robust importing to read and formatting data.  I was even able to write a simple caching tool so I wouldn't be rude to the NWS and NOAA servers.  In short: not a learning curve I wanted to go up right now.

## Some of the tools I needed to build
While I had some familiarity with html from back in the days where all pages were built by hand, the huge addition of new tags and 'best practices' of how to set up css was new.  The idea was to let the html do the layout while asynchronous background processes kept the graphics up to date. The main processes that I planed to have running:

This was my big growth curve. When I made the original set I 

  - `Tides.py` : generates two graphs and a table of tide information that is laid out on the screen. Since it is a clock I run this about once every five minutes (I cache the data once per day since the update only looks out about 2 days)
  - `Winds.py` : generates a wind graph of average and max wind for display. It is run about once every 15 minutes. Since the download is just a csv file it doesn't hammer too much. The tricky part here is that the buoy data can be unreliable. There are blank spots that have to be filtered, sometimes there is nothing at all so I had to devise a scheme to fall back to more reliable but not necessarily proximate sources to populate the chart.
  - `Forcast.py` : work in progress.  Right now I grab land information using the inagurated REST calls once an hour but what I want is are the nice marine forcast graphics that I can get in a web page.  
  - `chromium-browser` with a whole bunch of command line settings to run in a kiosk mode (a minimal Xwindows framework has to be installed, of course)

Because this is a kiosk I don't want to have to manage potential memory issues with handling and massaging data sets so I launch the above routines using a crontab.  This way I don't have to deal with any potential leaks.

## TODO:
 - I would like to have the screen shut down in the evening and start up at around dawn. I might even want it to turn off and turn on based on an external clock?  This may require some electronic tinkering.
 - Explore some hidden ways to put error messages into the screen, display some icons in discrete locations that indicate the health of the system.



## Additional notes

 - `README.md` : This overview
 - `RaspberryPiKiosk.md` : Work toward the kiosk setup