"""
General imports needed.
"""
# foundational libraries
from datetime import datetime, timedelta
# from zoneinfo import ZoneInfo
import pytz  # may need to migrate to ZoneInfo  RaspberryPi OS doesn't have the latest Python and thus doesn't have ZoneInfo.  This is a workaround until we can upgrade the OS.
import requests

# OCR tools
import pytesseract
# Bridge to cli tool. Need to install tesseract-ocr CLI engine in the OS

# Managing images
from PIL import Image

# Data management
import numpy as np
import pandas as pd

import logging
import os

import argparse

### Global Structures and Configurations
# Timezone configuration OLD SCHOOL
UTC = pytz.utc
EST = pytz.timezone('US/Eastern')
# Timezone configuration NEW SCHOOL
# UTC = ZoneInfo('UTC')
# EST = ZoneInfo('US/Eastern')

"""
    Quick review: NERACOOS weather buoys are managed by the Univ. of Ct. Bridgeport. They have invested,
    heavily in a package (software and hardware) that provides real-time data on wind, waves and water
    quality for LI Sound. We are most interested in two buoys which are close by to our harbor:
    Execution Rocks [exrx] and Western LI Sound [wlis]. The devices with their software can deliver csv lists
    of their systems but it would appear that the servers that present the data are not set up for this or
    not properly installed.  Since trying to access this information doesn't resolve to a permissions error
    or a no-authorized response but just a blunt php crash I am assuming the later.

    Our only option is to read the data from the .png graphical screens that are presented on their
    website. Fortunately this is pretty straightforward. In addition the data is only updated every 15 minutes
    for the Wind information and 20min for wave information.  Pulling data once every 10min seems like an
    easy lift.
"""

######  vvvvvvvvvvvvv  ###### USER CONFIGURABLE ######  vvvvvvvvvvvvv  ######
# Global definition of no data.
NaN = float('nan')
INDEX = 'TimeStamp' # standard index label for dataframes

# image URIs for Wind information
EXRX_WIND_URL = "https://clydebank.dms.uconn.edu/exrx_wxSens2.png"  # Execution rocks
WLIS_WIND_URL = "https://clydebank.dms.uconn.edu/wlis_wxSens1.png"  # Western Long Island
CLIS_WIND_URL = "https://clydebank.dms.uconn.edu/clis_wxSens1.png"  # Central Long Island

windURLS = {
    'exrx': EXRX_WIND_URL,
    'wlis': WLIS_WIND_URL,
    'clis': CLIS_WIND_URL,
}

# dictionary of locations within the image of the data we want.
windSources = {
    INDEX:                {'bounds':(100,  62, 294,  78), 'value': NaN , 'range':           None}, #dateString for reading
    'WindSpeedAvg [kts]': {'bounds':( 21, 307,  63, 327), 'value': NaN , 'range':     (0.0,60.0)}, #kts
    'WindSpeedGst [kts]': {'bounds':(116, 307, 158, 327), 'value': NaN , 'range':     (0.0,60.0)}, #kts
    'WindSpeedAvg [mph]': {'bounds':( 21, 334,  63, 351), 'value': NaN , 'range':     (0.0,70.0)}, #mph
    'WindSpeedGst [mph]': {'bounds':(116, 332, 158, 351), 'value': NaN , 'range':     (0.0,70.0)}, #mph
    'WindSpeedAvg [m/s]': {'bounds':( 21, 358,  63, 375), 'value': NaN , 'range':     (0.0,31.0)}, #m/s
    'WindSpeedGst [m/s]': {'bounds':(116, 358, 158, 375), 'value': NaN , 'range':     (0.0,31.0)}, #m/s
    'WindDir [°]':        {'bounds':(230, 320, 287, 339), 'value': NaN , 'range':   (0,     360)}, #deg True
    'AirTemp [°F]':       {'bounds':(410, 169, 471, 188), 'value': NaN , 'range':  (-20.0,110.0)}, #deg Farenheit
    'AirTemp [°C]':       {'bounds':(409, 221, 471, 238), 'value': NaN , 'range':  (-30.0, 40.0)}, #deg Centegrade
    'BaromPres [mmHg]':   {'bounds':(391, 415, 449, 434), 'value': NaN , 'range':    (25.0,32.5)}, #barm in mmHg
    'BaromPres [mB]':     {'bounds':(467, 415, 537, 434), 'value': NaN , 'range': (850.0,1100.0)}, #barm in mBar
    'DewPoint [°F]':      {'bounds':(505, 322, 552, 341), 'value': NaN , 'range':  (-20.0,110.0)}, #dewpoint deg Farenheit
    'DewPoint [°C]':      {'bounds':(563, 322, 605, 341), 'value': NaN , 'range':  (-30.0, 40.0)}, #dewPoint degCentegrade
    'RelHum [%]':         {'bounds':(391, 323, 448, 341), 'value': NaN , 'range':    (0.0,100.0)}, #rel. humidity
    'WindSpeedM24 [kt]':  {'bounds':(112, 412, 150, 435), 'value': NaN , 'range':     (0.0,60.0)}, #kts max in last 24hrs
    'WindDirM24 [°]':     {'bounds':(271, 412, 300, 433), 'value': NaN , 'range':   (0,     360)}, #deg True in last 24hrs
    'WindTimeM24':        {'bounds':(114, 433, 299, 454), 'value': NaN , 'range':           None}, #dateString of 24Hr Max
}

# image URIs for Wave information
EXRX_WAVE_URL = "https://clydebank.dms.uconn.edu/exrx_wavs.png"
WLIS_WAVE_URL = "https://clydebank.dms.uconn.edu/wlis_wavs.png"
CLIS_WAVE_URL = "https://clydebank.dms.uconn.edu/clis_wavs.png"

waveURLS = {
    'exrx': EXRX_WAVE_URL,
    'wlis': WLIS_WAVE_URL,
    'clis': CLIS_WAVE_URL,
}

# dictionary of locations within the image of the data we want.
waveSources = {
    INDEX:                {'bounds':(100,  62, 294,  78), 'value': NaN, 'range':       None}, #dateString for reading
    'WaveHgtSig [ft]':    {'bounds':( 68, 329, 112, 346), 'value': NaN, 'range': (0.0,12.0)}, #ft
    'WaveHgtMax [ft]':    {'bounds':(168, 329, 212, 346), 'value': NaN, 'range': (0.0,12.0)}, #ft
    'WaveHgtSig [m]':     {'bounds':( 68, 353, 112, 371), 'value': NaN, 'range': (0.0, 3.7)}, #m
    'WaveHgtMax [m]':     {'bounds':(168, 353, 212, 371), 'value': NaN, 'range': (0.0, 3.7),}, #m
    'WaveDir [°]':        {'bounds':(292, 320, 347, 340), 'value': NaN, 'range': (  0, 360)}, #degT
    'WavPerAvg [s]':      {'bounds':(479, 193, 539, 211), 'value': NaN, 'range':       None}, #sec
    'WavPerDom [s]':      {'bounds':(479, 251, 539, 269), 'value': NaN, 'range':       None}, #sec
    'WaveHgt24 [ft]':     {'bounds':(169, 413, 207, 433), 'value': NaN, 'range': (0.0,12.0)}, #ft max in last 24hrs
    'WaveDirM24 [°]':     {'bounds':(327, 412, 354, 433), 'value': NaN, 'range': (  0, 360)}, #deg True in last 24hrs
    'WavePerAvgM24 [s]':  {'bounds':(440, 412, 468, 430), 'value': NaN, 'range':       None}, #avg period in last 24hrs
    'WavePerDomM24 [s]':  {'bounds':(540, 412, 570, 430), 'value': NaN, 'range':       None}, #dominant period in last 24hrs
    'WaveTimeM24':        {'bounds':(169, 433, 363, 455), 'value': NaN, 'range':       None}, #dateString of 24Hr Max
}
######  ^^^^^^^^^^^^^  ###### USER CONFIGURABLE ######  ^^^^^^^^^^^^^  ######

class BuoyDataCapture:
    """
    Class to capture data from NERACOOS weather buoys. NERACOOS (long acronym: https://neracoos.org/), capture data from
    floating environmental stations up and down the coast. Mostly, it standardardizes the data storage and engineering of
    these stations. The data can be made available via an API but for the last 18 mos. it has only been available through
    a graphical display. As a consequence, this class uses OCR to read data from images and store the results in this object.
    This class works for both wind and wave data sections.  They have similar layouts. The water chemistry and bathymetry panels
    are quite different and might need a different class but we have what we need for our use case.
    :param sourceImageURL: URL of the image to fetch.
    :param dataExtraction: Dictionary defining regions to extract and store results.
    """

    # Source for image to decode
    sourceURL = ""
    # Placeholder for results
    dataParts = {}
    # temporary holder for downloaded image (maybe keep in memory?)
    filename  = "image.png"
    # Tesseract works best when limiting the characters to look for.
    ocrLimits = { # 0 decode for numbers
        'numberlike': r'--psm 6 -c tessedit_char_whitelist=-0123456789.',
                  # 1 decode for date
        'datelike':   r'--psm 6 -c tessedit_char_whitelist=-0123456789,:\ APMSunMonTueWedThuFriSatJanFebMarAprMayJunJulAugSepOctNovDecESTGMT',
    }

    def __init__(self, sourceImageURL, dataExtraction, filename:None):
        """
        Initialize the class
        :param sourceImageURL: Where we get the original image. The last part of the path will be a valid .png file name.
        :param dataExtraction: The structure (see above) that delineates the bounds we are trying to capture along with a place to store the result.
        """
        dataExtraction = dataExtraction.copy()  # avoid mutating the input dictionary
        self.sourceURL = sourceImageURL
        self.dataParts = dataExtraction
        if filename == None:
            self.filename = sourceImageURL.split("/")[-1]
        else:
            self.filename = filename
        # self.df = pd.DataFrame(columns=dataExtraction.keys())

    def fetch_image(self, filename=None):
        """
        retrieve the png and store to a file
        :param filename:  An optional name for the capture.
        """
        # 1. Retrieve the image  n.b. add a "?###" random number to sidestep local caching (which probably doesn't happen on a direct fetch)
        response = requests.get(self.sourceURL + f"?{np.random.randint(1000)}")

        # 2. Change the stored filename
        if filename != None:
            self.filename = filename

        # Check if the request was successful (HTTP 200)
        if response.status_code == 200:
            # 3. Store to disk for a second step, the image is not large, maybe keep in memory?
            with open(self.filename, "wb") as f:
                f.write(response.content)
            # return filename  # Return path to the stored file
        else:
            raise requests.RequestException(f"Failed to retrieve image. Status code: {response.status_code}")

    def _preprocess_for_ocr(self, croppedImage):
        """
        Improve the image for the OCR process. Mostly used in internally.
        :param croppedImage: an image object retrieved from the cropping process.
        :return: adapted image for OCR step
        """
        # 1. Convert to Grayscale ('L' mode in Pillow)
        gray_crop = croppedImage.convert('L')

        # 2. Resize: Tesseract needs clear, large characters.
        # Upscaling by 2x or 3x often fixes issues with small regions.
        w, h = gray_crop.size

        if os.uname().nodename == "raspberrypi":
            # For RaspPi
            upscaledImage = gray_crop.resize((w * 2, h * 2), Image.LANCZOS)
        else:
            # For high end
            upscaledImage = gray_crop.resize((w * 2, h * 2), Image.Resampling.LANCZOS)

        # 3. Optional: Invert if text is light on a dark background
        # Tesseract expects dark text on a light background.
        # upscaled = ImageOps.invert(upscaled)
        return upscaledImage

    def ocr_numerals_only(self, image_crop, ocrCharacterLimit):
        """
        Processes a cropped image to extract only numbers and decimal points.
        :param image_crop: A single cropped image.
        :param ocrCharacterLimit: A set of characters to use when trying to decode the image
        :return: The value for the image.
        """
        # Configuration breakdown:
        # --psm 6: Assume a single uniform block of text (good for small crops)
        # tessedit_char_whitelist: Restrict characters to digits and dot

        # Perform OCR
        # text = pytesseract.image_to_string(image_crop, config=self.ocrLimits['numberLike'])
        # # Clean up whitespace/newlines
        # return float(text.strip())
        return self._ocr_values(image_crop, self.ocrLimits['numberlike'])

    def ocr_dates_only(self, image_crop):
        """
        Processes image crops to extract only numbers and decimal points.
        :param image_crops: List of PIL Image objects (from previous step).
        :return: List of extracted numeric strings.
        """
        logging.debug("--DATES ONLY--")
        # Configuration breakdown:
        # --psm 6: Assume a single uniform block of text (good for small crops)
        # tessedit_char_whitelist: Restrict characters to digits and dot

        # Perform OCR
        # text = pytesseract.image_to_string(image_crop, config=self.ocrLimits['dateLike'])
        # Clean up whitespace/newlines
        # return text.strip()
        return self._ocr_values(image_crop, self.ocrLimits['datelike'])

    def _ocr_values(self, image_crop, ocrCharacterLimit):
        """
        Processes a cropped image to extract only numbers and decimal points.
        :param image_crop: A single cropped image.
        :param ocrCharacterLimit: A set of characters to use when trying to decode the image
        :return: The value for the image.
        """
        # Perform OCR
        text = pytesseract.image_to_string(image_crop, config=ocrCharacterLimit)
        # Clean up whitespace/newlines
        return text.strip()

    def extract_regions(self):
        """
        Extracts multiple rectangular regions from a PNG.  Again, we store the result
        on disk but maybe we can get away with keeping in memory?
        :param image_path: Path to the retrieved PNG file.
        :param regions: List of 4-tuples (left, upper, right, lower) coordinates.
        :return: List of cropped Image objects.
        """
        # extracted_images = []

        with Image.open(self.filename) as img:
            # Standardize for OCR: convert to RGB and remove transparency
            img = img.convert("RGB")

            for key, item in self.dataParts.items():
                logging.debug(f"WRK: {key}: {item['bounds']} {key.find('Time')}")
                croppedImage = self._preprocess_for_ocr(img.crop(item['bounds']))

                if key.find("Time")>-1:
                    # Decoding the date can be tricky. Though the buoys are connected via cell their clocks can be wildly off.
                    data = self._ocr_values(croppedImage, self.ocrLimits['datelike']) + f", {datetime.now().year}"
                    logging.debug(f"\t\tTime string [raw]: {repr(data)}")
                    # Gemini recommends stripping the timezone from the string and then localizing it to EST. This is because the timezone is often captured as "EST" but the time is actually in EDT during daylight savings time. This is a common issue with OCR of time strings that include timezones. By stripping the timezone and then localizing to EST, we can ensure that we get the correct time regardless of whether it is currently EST or EDT.
                    data = data.replace("EST, ", "").replace("EDT, ", "")
                    logging.debug(f"\t\tTime string [raw]: {repr(data)}")
                    try:
                        data = datetime.strptime(data, "%I:%M:%S %p %a %b %d, %Y")  # even though it captures the EST it is naive
                    except ValueError:
                        try:
                            data = datetime.strptime(data, "%I:%M:%S %p %a%b %d, %Y")  # even though it captures the EST it is naive
                        except ValueError:
                            try:
                                data = datetime.strptime(data, "%I:%M:%S %p %b %d, %Y")  # even though it captures the EST it is naive
                            except ValueError:
                                logging.critical(f"Can't decode date string use current time'{repr(data)}'")
                                data = datetime.now(tz=EST)

                    data = data.replace(tzinfo=EST)
                    logging.debug(f"\t\tTime string [decoded]: {repr(data)}")
                    item['value'] = data + timedelta(minutes=4)
                    #ATTN: When testing this on Jan 02, 2026 the buoy's clock was 2hrs fast. This may be corrected later.
                    # if datetime.now(EST) < data:
                    #     # The buoy reports the wrong time every now and again probably 2 hours off. 1/7/26 Seems to have been fixed.
                    #     logging.debug(f"\t\tFixing time: {repr(data)}")
                    #     data = data - timedelta(hours=2)
                    #     logging.debug(f"\t\t{data}")
                    # else:
                    logging.debug(f"\t\tTime {key} is correct: {repr(item['value'])}")
                        # data = data
                else:
                    try:
                        data = self._ocr_values(croppedImage, self.ocrLimits['numberlike'])
                        data = float(data)
                        # New Feature as of 2/13/26: Test to see if the value is within the expected range. If not, do some additional processing.
                        # Often the OCR in this instance has missed a decimal point. We can try to fix this by dividing by 10 to see if it falls
                        # within the expected range. If not, we can be pretty sure the value is wrong and set it to NaN.  OCR optimization isn't
                        # an option beyond what we have done because of the hardware limitations of the the raspberry pi.  This is a workaround to improve data quality.
                        if 'range' in item and item['range'] is not None:
                            min_val, max_val = item['range']
                            if not (min_val <= data <= max_val):
                                logging.warning(f"Value {data} is outside expected range {item['range']} for key '{key}'")
                                # Try fixing by dividing by 10 and checking if it falls within the expected range
                                data_div10 = data / 10.  # Empirically this is the most common error we see in the OCR results.
                                                         # The OCRed value is 3 sig figs overall but should have 1 decimal value
                                if min_val <= data_div10 <= max_val:
                                    logging.warning(f"Value {data} fixed to {data_div10}")
                                    data = data_div10
                                else:
                                    data = np.nan  # give up and set to NaN if it is still out of range after the fix attempt
                    except:
                        data = np.nan
                item['value'] = data
        # self.df = pd.DataFrame([self.getDict()], index=self.getTime())

    def getDict(self):
        # return all the OCR data without the time index
        # return {k: self[k] for k in self.dataParts if k != INDEX}
        # return all the OCR data
        return {k: self[k] for k in self.dataParts}

    def getNewDFRecord(self):
        """
        Return the time index aware dataframe suitable for concatenation.
        """
        logging.debug(f"New DF Dict:\t{self.getDict()}")
        df = pd.DataFrame([self.getDict()])

        # Select columns with datetime types
        datetime_cols = df.select_dtypes(include=['datetime64[ns, US/Eastern]']).columns
        # Add 4 minutes to the US/Eastern tz columns
        df[datetime_cols] = df[datetime_cols] + pd.Timedelta(minutes=4)
        df[INDEX] = pd.to_datetime(df[INDEX]) # + pd.Timedelta(minutes=4)  # ensure the index is a datetime object and fix the LTZ issue

        df.set_index(INDEX, inplace=True)
        logging.debug(f"New DF Record:\n{df}")
        return df

        # return pd.DataFrame([self.getDict()], index=[self.getTime()])

    def getTime(self):
        return self[INDEX]

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key):
        return self.dataParts[key]['value']

class DataBuffer:
    """
    This class manages a ring buffer of data stored in a CSV file. The buffer retains data for the last 3 days (72 hours) only.
    It uses pandas DataFrame for efficient data handling and storage. As with the OCR class above, this class is agnostic toward
    the type of data being stored. It could be data from wind or wave panels. The user specifies the column labels and the class manages
    the rest.
    :param labels: List of strings for the column names. (usually just: `list[waveSources.keys()]` or `list[windSources.keys()]`)
    :param filepath: Path to the CSV file.
    """
    def __init__(self, labels, filepath="sensor_data.csv"):
        """
        :param labels: List of strings for the column names.
        :param filepath: Path to the CSV file.
        """
        self.filepath = filepath
        self.columns = labels

        if os.path.exists(self.filepath):
            # Load existing data and ensure the index is parsed as datetime
            self.df = pd.read_csv(self.filepath, index_col=0, parse_dates=True)
            # Ensure index is timezone-aware (EST) to match new records
            if self.df.index.tz is None:
                self.df.index = self.df.index.tz_localize(EST)
            # Ensure existing columns match the provided labels
            # self.df.columns = self.columns
        else:
            # Initialize empty DataFrame with custom labels and UTC timezone awareness
            #    - 'data=[]' ensures it is empty
            #    - 'tz="US/Eastern"' sets the timezone (you can use 'UTC', 'Asia/Tokyo', etc.)
            tz_aware_index = pd.DatetimeIndex([], dtype='datetime64[ns, US/Eastern]', name=INDEX)
            self.df = pd.DataFrame(columns=self.columns, index=tz_aware_index)

    def add_record(self, newRowDF):
        """
        Appends a dictionary to the dataframe in one step.
        :param data_dict: Dictionary where keys match self.columns.
        """
        # 1. Create a timezone-aware timestamp for the current moment
        # now = data_dict[INDEX]   #datetime.now(UTC)

        # 2. Single-step append: loc automatically maps dictionary keys to columns
        # self.df.loc[now] = data_dict
        #self.df.set_index(INDEX, inplace=True)

        if len(self.df)==0:
            self.df = newRowDF
        else:
            self.df = pd.concat([self.df, newRowDF])

        # 3. Maintain the 3-day ring buffer and save
        self._truncate_and_save()

    def _truncate_and_save(self):
        """Truncates data older than 3 days and saves to CSV to persist through reboots."""
        cutoff_time = datetime.now(EST) - timedelta(days=3)
        # Keep only records from the last 72 hours
        self.df = self.df[self.df.index >= cutoff_time]

        # Remove columns that are completely empty
        df_filtered = self.df.dropna(axis=1, how='all')

        # Export the cleaned DataFrame to CSV
        df_filtered.to_csv(self.filepath)

    def get_data(self):
        """Access the dataframe for graphing or analysis."""
        return self.df

def captureWindData(srcURL=EXRX_WIND_URL):
    """
    Docstring for captureWindData
    Capture information from the wind buoy graphical image
    and store it into a database.
    """
    logging.info("-----------------------------------------")
    logging.info("--- Execution Rocks Wind Data Read:")

    wind = BuoyDataCapture(srcURL, windSources, "../resources/tmp/wind_panel.png")
    wind.fetch_image()
    wind.extract_regions()

    logging.debug("time: %s @%s  ", wind[INDEX].strftime('%Y-%m-%d %I:%M:%S %P %Z'), wind[INDEX])

    # # I think this early problem was a one off.
    # if datetime.now(EST) < wind[INDEX]:
    #     logging.warning("Why is the time wrong?")

    logging.info("dataframe:  %s", wind.getNewDFRecord())
    ## Now we want to store this data in a CSV file or a database.
    #
    wind_buffer = DataBuffer(list(windSources.keys()), filepath="../resources/wind_data.csv")
    # Add the new record (automatically handles truncation and saving)
    wind_buffer.add_record(wind.getNewDFRecord())

def captureWaveData(srcURL=EXRX_WAVE_URL):
    """
    Docstring for captureWaveData
    Capture information from the wind buoy graphical image
    and store it into a database.
    """
    logging.info("----------------------------------------")
    logging.info("--- Execution Rocks Wave Data Read:")
    wave = BuoyDataCapture(srcURL, waveSources, "../resources/tmp/wave_panel.png")
    wave.fetch_image()
    wave.extract_regions()

    logging.debug("time: %s @%s", wave[INDEX].strftime('%Y-%m-%d %I:%M:%S %P %Z'), wave[INDEX])

    logging.debug("dataframe:  %s", wave.getNewDFRecord())
    ## Now we want to store this data in a CSV file or a database.
    #
    wave_buffer = DataBuffer(list(waveSources.keys()), filepath="../resources/wave_data.csv")
    # Add the new record (automatically handles truncation and saving)
    wave_buffer.add_record(wave.getNewDFRecord())

def main():
    prog = "captureBuoyData"
    parser = argparse.ArgumentParser(
                    prog=prog,
                    description='Fetches the wind and wave data from LIRACOOS Buoys using OCR techniques.',
                    epilog='')
    parser.add_argument("-z", "--wind",   help="Gather wind information", action='store_true')
    parser.add_argument("-w", "--wave",   help="Gather wave information", action='store_true')
    parser.add_argument("-s", "--source", help="Select buoy to farm", choices=['exrx', 'wlis', 'clis'], default='exrx')
    args = parser.parse_args()

    if args.wind:
        captureWindData(windURLS[args.source])

    if args.wave:
        captureWaveData(waveURLS[args.source])

if __name__ == "__main__":
    logging.basicConfig(filename='../resources/tmp/OCRDataCapture.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
