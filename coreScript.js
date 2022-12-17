/**
 * Basic definitions for timing.
 */
const sec = 1000;
const min = 60 * sec;

/** astroData
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
    // holds the astronomical data for...
    yesterday: undefined,
    today: undefined,
    tomorrow: undefined,
};

/** moonImage
 * Similar to astroData, this object contains the lunar information including images of the 'lune'
 * cartoon that represents the degree of illumination of the moon. This is a great visual we all
 * experience which illustrates where the moon is in relation to the sun. As any es student will tell
 * you the magnitude of the tides is influenced by this relationship.
 * {rc: 200, filename: 'resources/tmp/moon_today.svg', fracillum: 0.5, stage: 'Waning', error: ''}
 */
let moonImage = {
    // holds the moon image data for...
    yesterday: undefined,
    today: undefined,
    tomorrow: undefined,
};

/** runClock
 * This is a self re-asserting timer that displays a running clock in the 'clock'
 * box as the web page is active. This fancyness should be unnecessary as we move to
 * a one page kiosk with mulitple divs
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

/** updateResources
 * update the graphs, tables and other media is less disruptive than refreshing the whole screen.
 * A different script updates the resources on a different schedule.
 * @param {'all' | 'tidegraph' | 'tidegraphic' | 'windgraph' | 'tidetable' | 'forecast' | 'timed'}
 * TODO: We shouldn't need to periodically rerun this method i.e. 'timed' is reserved for background updating
 *       when the resources are 'fetched' asynchronously.  We no longer do this so resources are updated when
 *       the promise is fufilled.
 */
function updateResources(what) {
    const now = new Date();
    if (!what) what = 'timed';

    // Note the trick to get the browser to refresh the images
    if (what === 'tidegraph' || what === 'all' || what === 'timed') {
        // clock graph
        document.getElementById('tidegraph').src = 'resources/tmp/tideGraph.png?' + now.getMilliseconds();
    }

    if (what === 'tidegraphic' || what === 'all' || what === 'timed') {
        // tide graphic: 'cartoon of depth'
        document.getElementById('tidegraphic').src = 'resources/tmp/tideGraphic.png?' + now.getMilliseconds();
    }

    if (what === 'windgraph' || what === 'all' || what === 'timed') {
        // wind graph
        document.getElementById('windgraph').src = 'resources/tmp/windGraph.png?' + now.getMilliseconds();
    }

    if (what === 'tidetable' || what === 'all' || what === 'timed') {
        // tide table
        document.getElementById('tidetable').src = 'resources/tmp/tideTable.html?' + now.getMilliseconds();
    }

    if (what === 'forecast' || what === 'all' || what === 'timed') {
        // tide table
        document.getElementById('forecast').src = 'resources/tmp/forecastGrid.html?' + now.getMilliseconds();
    }

    // TODO: Shouldn't need to asynchronously update.
    if (what === 'timed') {
        // auto updte in five minutes
        setTimeout(updateResources, 5 * min);
        console.log('rerunning updateResources in 5 minutes.');
    }
}

/** buildLunarData
 * fetch the lunar data slug. It also builds and works out the svg 'lune'
 * needed for displaying the moon based on the fracillum.
 * N.B.: if global `astroData` hasn't been populated, it will start the load and reschedule
 */
function buildLunarData() {
    // Make sure the astroData object is loaded
    if (!astroData || !astroData.yesterday || !astroData.today || !astroData.tomorrow) {
        buildAstroData();
        setTimeout(buildLunarData, 4 * sec);
        return; // do nothing because astroData hasn't been fully populated
    }

    // Make sure the moonImages object are loaded
    if (!moonImage || !moonImage.yesterday || !moonImage.today || !moonImage.tomorrow) {
        fetchMoonImage('today');
        fetchMoonImage('tomorrow');
        fetchMoonImage('yesterday');
        setTimeout(buildLunarData, 10 * sec);
        return; // do nothing the lunar data is loaded.
    }

    let now = new Date();
    document.getElementById('yesterday').getElementsByClassName('phase')[0].src =
        moonImage.yesterday.filename + '?' + now.getMilliseconds();
    document.getElementById('today').getElementsByClassName('phase')[0].src =
        moonImage.today.filename + '?' + now.getMilliseconds();
    document.getElementById('tomorrow').getElementsByClassName('phase')[0].src =
        moonImage.tomorrow.filename + '?' + now.getMilliseconds();
}

/** updateSunRiseSunset
 * update the sunrise sunset slug in the footer. It displays the current day's data
 * until after sunset when is switches to the next day.
 * N.B.: if global `astroData` hasn't been populated, it will start the load and reschedule
 */
function updateSunRiseSunset() {
    // We need these items to be populated so we exit quietly in case they are not.
    if (!astroData || !astroData.today.sundata || !astroData.tomorrow.sundata) {
        buildAstroData();
        setTimeout(updateSunRiseSunset, 3 * sec); // rerun in a few seconds or so
        return; // do nothing, yet, because astroData hasn't been fully populated
    }

    try {
        let now = new Date();
        now.setMinutes(now.getMinutes() + 20); // push it up by 20 minutes
        let theSunToday = astroData.today.sundata;
        let theSunTomor = astroData.tomorrow.sundata;

        document.getElementById('suncondition').innerHTML = `${theSunToday.time} ${theSunTomor.time}`;

        // DONE: When the DST parameter is used USNO server tacks on ' DT' or ' ST' to the time. Do I keep it?  Not always there.
        //       I am stripping it. This tool is only used during DST so having the designator clutters the display
        let setTime = theSunToday[3].time.replace(/ {2}[DS]T/, '').split(':'); // sometimes it is there and sometimes not, this takes care of both

        let todaySunset = new Date(now.getFullYear(), now.getMonth(), now.getDate(), setTime[0], setTime[1]);

        if (now > todaySunset) {
            // after sunset (see above) switch to tomorrow's datum
            document.getElementById('suncondition').innerHTML = `Tomorrow's Sunrise will be at ${theSunTomor[1].time.replace(
                / {2}[DS]T/,
                ''
            )}, Sunset at ${theSunTomor[3].time.replace(/ {2}[DS]T/, '')}`;
        } else {
            // present today's condition
            document.getElementById('suncondition').innerHTML = `Today's Sunrise is ${theSunToday[1].time.replace(
                / {2}[DS]T/,
                ''
            )}, Sunset at ${theSunToday[3].time.replace(/ {2}[DS]T/, '')}`;
        }
    } catch (err) {
        // whatever has gone wrong just try again in a couple of seconds
        setTimeout(updateSunRiseSunset, 3 * sec); // rerun in a few seconds or so
        return;
    }

    setTimeout(updateSunRiseSunset, 13 * min); // rerun every 12 minutes so we catch the change at sunset
}

/** fetchUSNavalObsData
 * As the name sez, gets the data from the US Naval Observatory, the
 * definitive reference for all daily information. We us an external
 * function through our server because of CORS restrictions within a
 * browser. THIS IS THE BUSINESS END of updating **astroData**, the
 * central database for astronomical data.
 * @param {Date} theDate
 * @param {'yesterday' | 'today' | 'tomorrow'} when
 */
async function fetchUSNavalDailyData(theDate, when) {
    const datestr = theDate.toLocaleDateString();
    let url = `http://localhost:8000/cgi-bin/usNavObsData.py?date=${datestr}`;

    await fetch(url)
        .then((response) => response.json())
        .then((data) => {
            data.properties.data.requestedDate = theDate;
            astroData[when] = data.properties.data;
        })
        .catch((error) => {
            console.error(`Failed to fetch ${url}`, error);
            astroData[when] = { error, response: null };
        });
}

/** fetchMoonImage
 * calls the cgi script to build the lunar svg images.
 * N.B. assumes astroData is fully loaded.
 * @param {'yesterday' | 'today' | 'tomorrow'} when
 */
async function fetchMoonImage(when) {
    const stage = astroData[when].curphase.split(' ')[0];
    const fracillum = astroData[when].fracillum.slice(0, -1); // Strip the % off.
    let url = `http://localhost:8000/cgi-bin/moonPhase.py?fracillum=${fracillum}&stage=${stage}&filename=moon_${when}.svg`;

    await fetch(url)
        .then((response) => response.json())
        .then((data) => {
            moonImage[when] = data;
        })
        .catch((error) => {
            console.error(`Failed to fetch ${url}`, error);
            moonImage[when] = { error, response: null };
        });
}

/** fetchResources
 * uses a cgi-calls to rebuild the various images, tables and media
 * @param {'all' | 'tidegraph' | 'tidegraphic' | 'windgraph' | 'tidetable' | 'forecast'} 'timed' is reserved for background
 * @param {'metric' | 'imperial' | null} if provided overrides automatic toggle.
 * trick for relaunching functions with parameters:
 *      // given a function fp(a, b)
 *      setTimeout(() => {fp(1, 'one'); fp(2, 'two');}, s*sec);
 */
let lastUnit = 0;
async function fetchResources(what, units) {
    if (!what) what = 'all';
    if (!units) units = lastUnit++ % 2 > 0 ? 'metric' : 'imperial';

    if (what === 'tidegraph' || what === 'all' || what === 'timed') {
        let url = `http://localhost:8000/cgi-bin/tidesGraph.py?units=${units}`;
        await fetch(url)
            .then((response) => response.text())
            .then((text) => {
                console.log(text);
                updateResources('tidegraph');
            })
            .catch((error) => {
                console.error(`Failed to fetch ${url}`, error);
            });
    }

    if (what === 'tidegraphic' || what === 'all' || what === 'timed') {
        let url = `http://localhost:8000/cgi-bin/tidesGraphic.py?units=${units}`;
        await fetch(url)
            .then((response) => response.text())
            .then((text) => {
                console.log(text);
                updateResources('tidegraphic');
            })
            .catch((error) => {
                console.error(`Failed to fetch ${url}`, error);
            });
    }

    if (what === 'tidetable' || what === 'all' || what === 'timed') {
        let url = `http://localhost:8000/cgi-bin/tidesTable.py?units=${units}`;
        await fetch(url)
            .then((response) => response.text())
            .then((text) => {
                console.log(text);
                updateResources('tidetable');
            })
            .catch((error) => {
                console.error(`Failed to fetch ${url}`, error);
            });
    }

    if (what === 'windgraph' || what === 'all' || what === 'timed') {
        let url = `http://localhost:8000/cgi-bin/windGraph.py`;
        await fetch(url)
            .then((response) => response.text())
            .then((text) => {
                console.log(text);
                updateResources('windgraph');
            })
            .catch((error) => {
                console.error(`Failed to fetch ${url}`, error);
            });
    }

    if (what === 'forecast' || what === 'all' || what === 'timed') {
        let url = `http://localhost:8000/cgi-bin/forecast.py`;
        await fetch(url)
            .then((response) => response.text())
            .then((text) => {
                console.log(text);
                updateResources('forecast');
            })
            .catch((error) => {
                console.error(`Failed to fetch ${url}`, error);
            });
    }

    if (what === 'timed') {
        setTimeout(fetchResources, 15 * min); // do it again in 15 minutes
    }
}

/** updateRadarView
 * update the NOAA NWS gif for current radar in KOKX
 * Initial image set in html should be...
 *    "https://radar.weather.gov/ridge/standard/KOKX_loop.gif"
 * TODO: Include in updateResources
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

    setTimeout(updateRadarView, 7 * min); // rerun in 7 minutes
}

/** buildAstroData
 * will load the global astroData parameter with the moon and solar data needed
 * for various display routines. This only needs to be done once per day. Since we restart the machine
 * every morning we run this when the kiosk is loaded. We only run if astroData is empty. This
 * costs nothing if we simpy run it at the head of any function that needs astroData to run.
 * @param {Date} testDate is an optional parameter to override the default of 'today'
 */
function buildAstroData(testDate) {
    let day = testDate;
    if (!testDate) day = new Date();

    // load if needed
    if (!astroData || !astroData.yesterday) {
        day.setDate(day.getDate() - 1);
        fetchUSNavalDailyData(day, 'yesterday');
    }

    // load if needed
    if (!astroData || !astroData.today) {
        day.setDate(day.getDate() + 1);
        fetchUSNavalDailyData(day, 'today');
    }

    // load if needed
    if (!astroData || !astroData.tomorrow) {
        day.setDate(day.getDate() + 1);
        fetchUSNavalDailyData(day, 'tomorrow');
    }
}

/**
 * This is the main entrypoint for populating all the content on this
 * page. I sets in motion all of the actions that need to be loaded to
 * complete the up to date content. Some routines will automatically
 * relaunch themselves if dependancies are not in place.  Otherwise
 * they set their own schedules for re-launching if needed.
 */
function buildWeatherPage() {
    /** Get and post the sunrise and sunset data */
    buildAstroData(); // Basic astronomical information all the other routines need.
    fetchResources(); // refresh all our various resources
    setTimeout(buildLunarData, 3 * sec); // hold off a bit and launch to
    setTimeout(updateSunRiseSunset, 5 * sec); // first run
    setTimeout(updateRadarView, 1 * min); // first run in a minutes
    setTimeout(updateResources, 2 * min); // first run in 2 minutes
}

/**
 * Test if the network is up or down.
 **/
async function networkStatus() {
    let url = `http://localhost:8000/cgi-bin/networkStatus.py`;
    await fetch(url)
        .then((response) => response.text())
        .then((text) => {
            console.log(text);
        })
        .catch((error) => {
            console.error(`Failed to fetch ${url}`, error);
        });
}

/** For Reservation Sheets Only
 * This is one of many attempts to fix the cache problem of retrieving the Google Sheets
 * page. I have tried to force updating according to recommendations in Stack Exchange to
 * no avail. The problem seems to be some interplay between the browser and Google and intermediate caches
 * PROBLEM MAY BE SOLVED. Instead of 'publishing' a sheet, make it public (which it is anyway) and
 * access the content as you would through any browser. It seems to work. No updating necessary.
 */
/**
// function refreshFrames() {
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
    // document.getElementById('dayboat').src += ''; // cache killer not needed
    // document.getElementById('ideal18').src += '';
    //    document.location.reload();

    // console.log('refresh frames NT');

    //setTimeout(refreshFrames, 2 * min);
// }
 */
