/**
 * Common code between kiosk pages that controls the presentation.
 * TODO: Improve cross platfrom modelling so we can test here and at destination.
 */
const sec = 1000;
const min = 60 * sec;

/**
 * RunClock
 * This is a self re-asserting timer that displays a running clock in the 'clock'
 * box as the web page is active.
 */
function runClock(start) {
    function clockRunner(time) {
        const elapsed = time - start;
        const seconds = Math.round(elapsed / sec);
        document.getElementById('clock').innerHTML = new Date().toLocaleTimeString('en-US');
        const targetNext = (seconds + 1) * sec + start;
        setTimeout(() => requestAnimationFrame(clockRunner), targetNext - performance.now());
    }
    clockRunner();
}

/**
 * UpdateForecast
 * Use javascript to update forecast table
 */
function updateForecast() {
    document.getElementById('forecast').src = document.getElementById('forecast').src;
    setTimeout(updateForecast, 15 * min); // reasonable update for updates
}

/**
 * UpdateGraphs
 * Using javascript to update graphs is less disruptive than refreshing the whole screen
 */
function updateGraphs() {
    const now = new Date();
    // Note the trick to get the browser to refresh the images
    document.getElementById('tidegraph').src = 'resources/tideGraph.png?' + now.getMilliseconds();
    document.getElementById('tidegraphic').src = 'resources/tideGraphic.png?' + now.getMilliseconds();
    document.getElementById('windgraph').src = 'resources/windGraph.png?' + now.getMilliseconds();
    document.getElementById('tidetable').src = document.getElementById('tidetable').src;

    setTimeout(updateGraphs, 5 * min); // five minutes
}

/**
 * Each of the three entries below carry the following information returned from USNO:
 * { closestphase: { day: 1, month: 2, phase: 'New Moon', time: '00:46', year: 2022 },
 *   curphase: 'Waxing Crescent',  day: 4, day_of_week: 'Friday',  fracillum: '15%', isdst: false, label: null, month: 2,
 *   moondata: [ { phen: 'Rise', time: '09:17' }, { phen: 'Upper Transit', time: '15:12' }, { phen: 'Set', time: '21:19' } ],
 *   sundata:  [ { phen: 'Begin Civil Twilight', time: '06:34' }, { phen: 'Rise', time: '07:02' }, { phen: 'Upper Transit', time: '12:09' },
 *               { phen: 'Set', time: '17:16' }, { phen: 'End Civil Twilight', time: '17:45' } ],
 *   tz: -5,
 *   year: 2022 }
 */
let astroData = {
    yesterday: undefined,
    today: undefined,
    tomorrow: undefined,
};

let moonImage = {
    yesterday: undefined,
    today: undefined,
    tomorrow: undefined,
};

/**
 * fetchUSNavalObsData
 * @param {Date} theDate
 * @param {'yesterday' | 'today' | 'tomorrow'} when
 */
async function fetchUSNavalDailyData(theDate, when) {
    const datestr = theDate.toLocaleDateString();
    let url = `http://localhost:8000/cgi-bin/usNavObsData.py?date=${datestr}`;

    try {
        const response = await fetch(url);
        const sunFetch = await response.json();
        sunFetch.properties.data.requestedDate = theDate;
        astroData[when] = sunFetch.properties.data;
    } catch (error) {
        console.error(`Failed to fetch ${url}`, error);
        astroData[when] = { error, response: null };
    }
}

/**
 * fetchMoonImage calls the cgi script to build the lunar svg images. N.B. assumes astroData is fully loaded.
 * @param {'yesterday' | 'today' | 'tomorrow'} when
 */
async function fetchMoonImage(when) {
    const stage = astroData[when].curphase.split(' ')[0];
    const fracillum = astroData[when].fracillum.slice(0, -1); // Strip the % off.
    let url = `http://localhost:8000/cgi-bin/moonPhase.py?fracillum=${fracillum}&stage=${stage}&filename=resources%2Fmoon_${when}.svg`;
    //console.log(url);

    try {
        const response = await fetch(url);
        const moonFetch = await response.json();
        moonImage[when] = moonFetch;
    } catch (error) {
        console.error(`Failed to fetch ${url}`, error);
        moonImage[when] = { error, response: null };
    }
}

/**
 * update the lunar data slug (whereever I decide to put it). It calculates the icon to use
 * for displaying the moon based on the fracillum.
 * IMPORTANT: This presumes the global `astroData` has been populated
 */
function updateLunarData() {
    // Make sure the astroData object is loaded
    if (astroData == null || astroData.today == null) {
        loadAstroData();
        setTimeout(updateLunarData, 4 * sec);
        return; // do nothing because astroData hasn't been fully populated
    }

    // Make sure the moonImages object are loaded  TODO: May be necessary to load these sequentially.
    if (moonImage == null || moonImage.today == null || moonImage.tomorrow == null || moonImage.yesterday == null) {
        fetchMoonImage('today');
        fetchMoonImage('tomorrow');
        fetchMoonImage('yesterday');
        setTimeout(updateLunarData, 10 * sec);
    }

    document.getElementById('moonYD').getElementsByClassName('phase')[0].src = moonImage.yesterday.filename;
    document.getElementById('moonTD').getElementsByClassName('phase')[0].src = moonImage.today.filename;
    document.getElementById('moonTM').getElementsByClassName('phase')[0].src = moonImage.tomorrow.filename;

    // Reassert for update
    setTimeout(updateLunarData, 10 * min);
}

/**
 * update the sunrise sunset slug in the footer. It displays the current day's data
 * until after sunset when is switches to the next day.
 * IMPORTANT: This presumes the global `astroData` has been populated
 */
function updateSunRiseSunset() {
    // We need these items to be populated so we exit quietly in case they are not.
    if (astroData?.today == null || astroData?.tomorrow == null) {
        loadAstroData();
        setTimeout(updateSunRiseSunset, 3 * sec); // rerun in a second or so
        return; // do nothing because astroData hasn't been fully populated
    }

    try {
        let now = new Date();
        now.setMinutes(now.getMinutes() + 20); // push it up by 20 minutes
        let theSunToday = astroData.today.sundata;
        let theSunTomor = astroData.tomorrow.sundata;

        document.getElementById('suncondition').innerHTML = `${theSunToday.time} ${theSunTomor.time}`;

        // TODO: When the DST parameter is used USNO server tacks on ' DT' or ' ST' to the time. Do I keep it?  Not always there.
        //       I am stripping it. This tool is only used during DST so having the designator clutters the display
        let setTime = theSunToday[3].time.replace(/ {2}[DS]T/, '').split(':'); // sometimes it is there and sometimes not, this takes care of both

        let todaySunset = new Date(now.getFullYear(), now.getMonth(), now.getDate(), setTime[0], setTime[1]);
        // console.log(`${setTime}`)
        // console.log(`${todaySunset} ${now} rel ${now>todaySunset}`)

        if (now > todaySunset)
            // 20 min after sunset (see above) switch to tomorrow's datum
            document.getElementById('suncondition').innerHTML = `Tomorrow's Sunrise will be at ${theSunTomor[1].time.replace(
                / {2}[DS]T/,
                ''
            )}, Sunset at ${theSunTomor[3].time.replace(/ {2}[DS]T/, '')}`;
        else
            document.getElementById('suncondition').innerHTML = `Today's Sunrise is ${theSunToday[1].time.replace(
                / {2}[DS]T/,
                ''
            )}, Sunset at ${theSunToday[3].time.replace(/ {2}[DS]T/, '')}`;
    } catch (err) {
        // whatever has gone wrong just try again in a couple of seconds
        setTimeout(updateSunRiseSunset, 1 * sec); // rerun in a second or so
        return;
    }

    setTimeout(updateSunRiseSunset, 10 * min); // rerun in 10 minutes
}

/**
 * update the NOAA NWS gif for current radar in KOKX
 * Initial image set in html should be...
 *    "https://radar.weather.gov/ridge/standard/KOKX_loop.gif"
 */
function updateRadarView() {
    try {
        let now = Date.now();
        let origImg = document.getElementById('radar').src;
        origImg = origImg.split('?')[0];
        document.getElementById('radar').src = origImg + '?' + now; // trick to force an image refresh with the same URL
    } catch (err) {
        // whatever has gone wrong just try again in a couple of seconds
        setTimeout(updateRadarView, 20 * sec); // rerun in a second or so
        return;
    }

    setTimeout(updateRadarView, 5 * min); // rerun in 10 minutes
}

/**
 * will load the global astroData parameter with the moon and solar data needed for various
 * display routines.
 * @param {Date} testDate is an optional parameter to override the default of 'today'
 */
function loadAstroData(testDate) {
    let day;
    if (testDate == null) day = new Date();
    else day = testDate;
    day.setDate(day.getDate() - 1);
    fetchUSNavalDailyData(day, 'yesterday');
    day.setDate(day.getDate() + 1);
    fetchUSNavalDailyData(day, 'today');
    day.setDate(day.getDate() + 1);
    fetchUSNavalDailyData(day, 'tomorrow');
}

/**
 * Post the weather information gained from NWS marine forecast
 */
function postDataWeather() {
    /** Get and post the sunrise and sunset data */
    loadAstroData();
    updateGraphs();
    setTimeout(updateSunRiseSunset, 5 * sec); // first run
    setTimeout(updateLunarData, 3 * sec); // first run
    setTimeout(updateRadarView, 2 * min); // first run in 2 minutes
}

/**
 * Schedule the updates needed for a webpage
 */
function postDataSchedule() {
    /** Get and post the sunrise and sunset data */
    loadAstroData();
    setTimeout(updateSunRiseSunset, 10 * sec); // first run
}

/**
 * Test if the network is up or down.
 **/
async function networkUpDown() {
    let url = `http://localhost:8000/cgi-bin/networkStatus.sh`;

    try {
        const response = await fetch(url);
        const data = await response.text();
        console.log(data.split(' '));
    } catch (error) {
        console.error('Cannot check the network status', error);
    }
}

let dayBoatSheet = '';
let ideal18Sheet = '';

/** For Reservation Sheets Only
 * This is one of many attempts to fix the cache problem of retrieving the Google Sheets
 * page. I have tried to force updating according to recommendations in Stack Exchange to
 * no avail. The problem seems to be some interplay between the browser and Google and intermediate caches
 */
function refreshFrames() {
    // const change = '&cachekiller=' + Math.floor(Date.time()/1000); // we need to force the cache to update by passing a bogus tag.

    //save the source of the iframe minus the unique identifier
    // I already have this saved
    // const dayBoatSrc = dayBoatSheet + change;
    // console.log(dayBoatSrc.substring(dayBoatSrc.length - 20));
    // const ideal18Src = ideal18Sheet + change;
    // console.log(ideal18Src.substring(ideal18Src.length - 20));

    // METHOD 1: simply update the source with the 'dummy' to fool the cache into reloading.
    // document.getElementById('dayboat').src = dayBoatSrc;
    // document.getElementById('ideal18').src = ideal18Src;

    // METHOD 2: remove the iframe and rebuild. (Can't seem to get this to work right)
    // document.getElementById('dayboat').remove();
    // document.getElementById('ideal18').remove();

    // const dbFrame = document.createElement('<iframe id="dayboat" class="import" src="' + dayBoatSrc + '">');
    // const idFrame = document.createElement('<iframe id="ideal18" class="import" src="' + ideal18Src + '">');

    // //re-add the iframe with the new source including random query string
    // document.getElementById('dayboat').append(dbFrame);
    // document.getElementById('ideal18').append(idFrame);

    // METHOD 3: simply add an empty string.
    document.getElementById('dayboat').src += ''; // cache killer not needed
    document.getElementById('ideal18').src += '';
    //    document.location.reload();

    console.log('refresh frames NT');

    setTimeout(refreshFrames, 2 * min);
}
