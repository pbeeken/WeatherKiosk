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
    complete: false,
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
    complete: false,
    // holds the moon image data for...
    yesterday: undefined,
    today: undefined,
    tomorrow: undefined,
};

/** runClock
 * This is a self re-asserting timer that displays a running clock in the 'clock'
 * box as the web page is active. This fancyness shouldn't be unnecessary as we move to
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
 * @param {'all' | 'tides' | 'tidecartoon' | 'windgraph' | 'forecast' | 'radar' | 'boats' | 'porch' }

 */
function updateResources(what) {
    if (!what) what = 'timed';

    // Note the trick to get the browser to refresh the images
    if (what === 'tides' || what === 'all') {
        // these guys work together.
        // clock graph
        document.getElementById('tidegraph').src = 'resources/tmp/tideGraph.png' + randomSuffix();
        // tide table
        document.getElementById('tideTable').src = 'resources/tmp/tideTable.html' + randomSuffix();
    }

    if (what === 'tidecartoon' || what === 'all') {
        // tide graphic: 'cartoon of depth'
        document.getElementById('tidecartoon').src = 'resources/tmp/tideCartoon.png' + randomSuffix();
    }

    if (what === 'windgraph' || what === 'all') {
        // wind graph
        document.getElementById('windgraph').src = 'resources/tmp/windGraph.png' + randomSuffix();
    }

    if (what === 'forecast' || what === 'all') {
        // tide table
        document.getElementById('forecast').src = 'resources/tmp/forecastGrid.html' + randomSuffix();
    }

    if (what === 'radar' || what === 'all') {
        // animated gif from NOAA
        try {
            let origImg = document.getElementById('radar').src;
            origImg = origImg.split('?')[0]; // get rid of random bit at the end.
            document.getElementById('radar').src = origImg + randomSuffix(); // force an image refresh with the same URL
        } catch (err) {
            // whatever has gone wrong just try again in a little later
            setTimeout(() => {
                updateResources('radar');
            }, 31 * sec);
        }
    }

    if (what === 'boats' || what === 'all') {
        // update porch stuff.
        let origSrc = document.getElementById('dayboat').src;
        origSrc = origSrc.replace(/(.+)&.+/, '$1');
        document.getElementById('dayboat').src = origSrc + randomSuffix('&');
        origSrc = document.getElementById('ideal18').src;
        origSrc = origSrc.replace(/(.+)&.+/, '$1');
        document.getElementById('ideal18').src = origSrc + randomSuffix('&');
    }

    if (what === 'porch' || what === 'all') {
        // update porch stuff.
        let origSrc = document.getElementById('day1').src;
        origSrc = origSrc.replace(/(.+)&.+/, '$1');
        document.getElementById('day1').src = origSrc + randomSuffix('&');
        origSrc = document.getElementById('day2').src;
        origSrc = origSrc.replace(/(.+)&.+/, '$1');
        document.getElementById('day2').src = origSrc + randomSuffix('&');
    }
}

/** buildLunarData
 * fetch the lunar data slug. It also builds and works out the svg 'lune'
 * needed for displaying the moon based on the fracillum.
 * N.B.: if global `astroData` hasn't been populated, it will start the load and reschedule
 */
function buildLunarData() {
    // Make sure the astroData object is loaded
    if (!astroData.complete) {
        setTimeout(buildLunarData, 9 * sec); // one offs
        return; // do nothing because astroData hasn't been fully populated
    }

    // build and load the lunar images
    fetchMoonImage('today');
    fetchMoonImage('tomorrow');
    fetchMoonImage('yesterday');
}

/** updateSunEphemeris
 * update the sunrise sunset slug in the footer. It displays the current day's data
 * until after sunset when is switches to the next day.
 * N.B.: if global `astroData` hasn't been populated, it will start the load and reschedule
 */
function updateSunEphemeris() {
    // We need these items to be populated so we exit quietly in case they are not.
    if (!astroData.complete) {
        setTimeout(updateSunEphemeris, 7 * sec); // rerun in a few seconds or so
        return; // do nothing, yet, because astroData hasn't been fully populated
    }

    try {
        let now = new Date();
        now.setMinutes(now.getMinutes() + 20); // push it up by 20 minutes
        let theSunToday = astroData.today.sundata;
        let theSunTomor = astroData.tomorrow.sundata;

        document.getElementById('ephemeris').innerHTML = `${theSunToday.time} ${theSunTomor.time}`;

        // DONE: When the DST parameter is used USNO server tacks on ' DT' or ' ST' to the time. Do I keep it?  Not always there.
        //       I am stripping it. This tool is only used during DST so having the designator clutters the display
        let setTime = theSunToday[3].time.replace(/ {2}[DS]T/, '').split(':'); // sometimes it is there and sometimes not, this takes care of both

        let todaySunset = new Date(now.getFullYear(), now.getMonth(), now.getDate(), setTime[0], setTime[1]);

        if (now > todaySunset) {
            // after sunset (see above) switch to tomorrow's datum
            document.getElementById('ephemeris').innerHTML = `Tomorrow's Sunrise will be at ${theSunTomor[1].time.replace(
                / {2}[DS]T/,
                ''
            )}, Sunset at ${theSunTomor[3].time.replace(/ {2}[DS]T/, '')}`;
        } else {
            // present today's condition
            document.getElementById('ephemeris').innerHTML = `Today's Sunrise is ${theSunToday[1].time.replace(
                / {2}[DS]T/,
                ''
            )}, Sunset at ${theSunToday[3].time.replace(/ {2}[DS]T/, '')}`;
        }
    } catch (err) {
        // whatever has gone wrong just try again in a couple of seconds
        setTimeout(updateSunEphemeris, 7 * sec); // rerun in a few seconds or so
        return;
    }
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
    if (astroData.complete) return; // if we are complete we are done.
    const datestr = theDate.toLocaleDateString();
    let url = `http://localhost:8000/cgi-bin/usNavObsData.py?date=${datestr}`;
    toastStatus('↣astro', 'add');

    await fetch(url)
        .then((response) => response.json())
        .then((data) => {
            data.properties.data.requestedDate = theDate;
            astroData[when] = data.properties.data;
            astroData.complete = astroData.yesterday && astroData.today && astroData.tomorrow ? true : false;
            toastStatus('↣astro', 'rem');
        })
        .catch((error) => {
            console.error(`Failed to fetch ${url}`, error);
            networkStatus();
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
    toastStatus('↣moon', 'add');

    await fetch(url)
        .then((response) => response.json())
        .then((data) => {
            moonImage[when] = data;
            toastStatus('↣moon', 'rem');
            document.getElementById(when).getElementsByClassName('phase')[0].src = moonImage[when].filename + randomSuffix();
            moonImage.complete = moonImage.yesterday && moonImage.today && moonImage.tomorrow ? true : false;
        })
        .catch((error) => {
            console.error(`Failed to fetch ${url}`, error);
            networkStatus();
            moonImage[when] = { error, response: null };
        });
}

/** fetchResources
 * uses a cgi-calls to rebuild the various images, tables and media
 * @param {'all' | 'tides' | 'tidecartoon' | 'windgraph' | 'forecast' | 'radar'}
 * @param {'metric' | 'imperial' | null} if provided, overrides automatic toggle.
 * trick for relaunching functions with parameters:
 *      // given a function fp(a, b)
 *      setTimeout(() => {fp(1, 'one'); fp(2, 'two');}, s*sec);
 * another tricky part: tide graph and tide table need to get the same units when running
 *      looks funny if one is in metric and the other imperial. So we run them together.
 */
let lastUnit = 0;
async function fetchResources(what, units) {
    if (!what) what = 'all';
    if (!units) units = lastUnit % 2 > 0 ? 'metric' : 'imperial';

    if (what === 'tides' || what === 'all') {
        let url = `http://localhost:8000/cgi-bin/tidesGraph.py?units=${units}`;
        toastStatus('↣tides', 'add');
        await fetch(url)
            .then((response) => response.text())
            .then((text) => {
                console.log(text);
                updateResources('tides');
                lastUnit++;
            })
            .catch((error) => {
                console.error(`Failed to fetch ${url}`, error);
                networkStatus();
            });
        url = `http://localhost:8000/cgi-bin/tidesTable.py?units=${units}`;
        await fetch(url)
            .then((response) => response.text())
            .then((text) => {
                console.log(text);
                updateResources('tides');
                toastStatus('↣tides', 'rem');
            })
            .catch((error) => {
                console.error(`Failed to fetch ${url}`, error);
                networkStatus();
            });
    }

    if (what === 'tidecartoon' || what === 'all') {
        let url = `http://localhost:8000/cgi-bin/tidesCartoon.py?clock=12hour`;
        toastStatus('↣tgraphic', 'add');
        await fetch(url)
            .then((response) => response.text())
            .then((text) => {
                console.log(text);
                updateResources('tidecartoon');
                toastStatus('↣tgraphic', 'rem');
            })
            .catch((error) => {
                console.error(`Failed to fetch ${url}`, error);
                networkStatus();
            });
    }

    if (what === 'windgraph' || what === 'all') {
        let url = `http://localhost:8000/cgi-bin/windGraph.py`;
        toastStatus('↣wind', 'add');
        await fetch(url)
            .then((response) => response.text())
            .then((text) => {
                console.log(text);
                updateResources('windgraph');
                toastStatus('↣wind', 'rem');
            })
            .catch((error) => {
                console.error(`Failed to fetch ${url}`, error);
                networkStatus();
            });
    }

    if (what === 'forecast' || what === 'all') {
        let url = `http://localhost:8000/cgi-bin/forecast.py`;
        toastStatus('↣forecast', 'add');
        await fetch(url)
            .then((response) => response.text())
            .then((text) => {
                console.log(text);
                updateResources('forecast');
                toastStatus('↣forecast', 'rem');
            })
            .catch((error) => {
                console.error(`Failed to fetch ${url}`, error);
                networkStatus();
            });
    }

    if (what === 'radar' || what === 'all') {
        toastStatus('↣radar', 'add');
        updateResources('radar');
        toastStatus('↣radar', 'rem');
    }
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

    // load only if needed
    if (!astroData.complete || !astroData.yesterday) {
        day.setDate(day.getDate() - 1);
        fetchUSNavalDailyData(day, 'yesterday');
    }

    // load only if needed
    if (!astroData.complete || !astroData.today) {
        day.setDate(day.getDate() + 1);
        fetchUSNavalDailyData(day, 'today');
    }

    // load only if needed
    if (!astroData.complete || !astroData.tomorrow) {
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
function buildWeatherKiosk() {
    networkStatus();
    /** Get and post the sunrise and sunset data */
    buildAstroData(); // Basic astronomical information all the other routines need.
    buildLunarData(); // hold off a bit and launch to
    // Now we can get everything else
    fetchResources('all'); // refresh all our various resources

    // we updte the sunrise sunset after a while to make sure astroData is packed.
    setTimeout(updateSunEphemeris, 13 * sec); // first run

    // this can run a little later so we have a chance to see that the first, busiest, screen is set.
    setTimeout(setTimers, 15 * sec);
}

function setTimers() {
    // debugging we can manually cycle panels
    setInterval(cyclePanels, 20 * sec);

    // Tides Elements includes both table and graph
    setInterval(() => {
        fetchResources('tides');
    }, 10 * min);

    // Sunrise-Sunset
    setInterval(() => {
        updateSunEphemeris();
    }, 7 * min);

    // Tide Graphic
    setInterval(() => {
        // rinse and repeat
        fetchResources('tidecartoon');
    }, 10 * min);

    // windgraph
    setInterval(() => {
        // rinse and repeat
        fetchResources('windgraph');
    }, 13 * min);

    // forecast
    setInterval(() => {
        // rinse and repeat
        fetchResources('forecast');
    }, 15 * min);

    // animated radar gif
    setInterval(() => {
        // rinse and repeat
        fetchResources('radar');
    }, 7 * min);

    // network status (useful to know if our connection has issues)
    setInterval(() => {
        networkStatus();
    }, 15 * min);

    // boat reservations
    setInterval(() => {
        // rinse and repeat
        updateResources('boats');
    }, 4 * min);

    // porch reservations
    setInterval(() => {
        // rinse and repeat
        updateResources('porch');
    }, 5 * min);
}

/**
 * Useful tool for changing the title
 * @param {string} the title after the boilerplate
 */
function changePageTitle(title) {
    document.getElementById('title').innerHTML = `Horseshoe Harbor Yacht Club ${title}`;
}

/**
 * post a message in the toast panel
 * @param {string} info
 * @param {string} what = undefined | 'add' | 'rem' | 'clr'
 *    where undefined completely replaces the toast
 */
function toastStatus(info, what) {
    let currentToast = document.getElementById('toast').innerHTML;

    if (!what || what === 'clr') {
        // completely replace the toast screen
        currentToast = info;
    } else if (what === 'add') {
        currentToast = `${currentToast} ${info}`;
    } else if (what === 'rem') {
        currentToast = currentToast.replace(` ${info}`, '');
    }
    document.getElementById('toast').innerHTML = currentToast;
}

/**
 * Test if the network is up or down.
 **/
async function networkStatus() {
    let url = `http://localhost:8000/cgi-bin/networkStatus.py`;
    document.getElementById('network').innerHTML = '.❓.'; // 🟠
    await fetch(url)
        .then((response) => response.text())
        .then((text) => {
            console.log(text);
            text = text.trim().replace('networkStatus ', '');
            document.getElementById('network').innerHTML = text;
        })
        .catch((error) => {
            console.log(`Failed to fetch ${url}`, error);
            document.getElementById('network').innerHTML = '&#x2753; ERR'; // ❓
        });
}

/**
 * randomSuffix
 * Creates a random suffix to force an update of the visual resources.
 * This trick works with images and iframes to force a reload of the resource.
 * @param {string} [opt] a single character, usually to prefix the random value
 * @returns {string} random url mod
 */
function randomSuffix(prefix) {
    if (!prefix) prefix = '?';
    let now = new Date();
    return prefix + now.getMilliseconds();
}

/**
 * cycleVisuals
 * cycle between divs. We do this by setting the style.display value to 'none' to hide
 * and to 'block' to show. We have 3 panels (weather, boatRes, and porchRes). On Friday,
 * Saturday and Sunday we show all three.  The rest of the days we just show the weather
 * and boat reservations.
 */
/** @type {HTMLDivElement[]} */
let panelList = [];
let currentPanel = 0;
let transitionTime = 1.5;

/**
 * Cycle through the panels using transitions set in the css file.
 * The first time this runs it initializes the above globals.
 * @returns nothing
 */
function cyclePanels() {
    // Is this the first time we are running?
    if (panelList.length === 0) {
        // First time we enter this method we store all the 'screens' (read: slides we want to manipulate.)
        // This is done once per load, on most days this is done once every 24 hout period.
        const dow = new Date().getDay();

        // get the transition time from the css file
        let trans = document.querySelector('.enterScreen');
        transitionTime = sec * getComputedStyle(trans).transitionDuration.replace('s', ''); // remove the trailing 's'

        // store the two 'always shown' panels
        panelList.push(document.getElementById('weatherScreen'));
        panelList.push(document.getElementById('boatScreen'));

        // only on thursdays through sunday store the third panel and prepare it's appearance
        if (dow === 4 || dow === 5 || dow === 6 || dow === 0) {
            panelList.push(document.getElementById('porchScreen'));
            //   There are two panels: today[day1Box] and tomorrow[day2Box]
            // On Thursdays:  today is hidden,  tomorrow is visible  n.b. visibility doesn't affect spacing
            // On Fridays:    today is visible, tomorrow is visible
            // On Saturday:   today is visible, tomorrow is visible
            // On Sunday:     today is visible, tomorrow is hidden
            if (dow === 4) {
                // bad practice, I know. Only place where we override the computed css settings.
                document.getElementById('porchToday').style.visibility = 'hidden';
            }
            if (dow === 0) {
                // bad practice, I know. Only place where we override the computed css settings.
                document.getElementById('porchTomorrow').style.visibility = 'hidden';
            }
        }
    }

    // DEBUGING EasterEgg
    // This is a flag to stop the rotation so we can examine
    // a specific panel. Tap 'S' when focused on the web page to toggle.
    if (currentPanel < 0) return; // don't do anything.

    // find the index of the next panel
    const nextPanel = (currentPanel + 1) % panelList.length;

    panelList[currentPanel].classList.add('exitScreen');
    panelList[nextPanel].classList.add('enterScreen');
    changePageTitle(panelList[nextPanel].getAttribute('alt'));

    // In a time just under the transition dwell
    //      hide the current panel after it is covered.
    const lastPanel = currentPanel; // preserve the current panel for later hidding
    setTimeout(() => {
        panelList[lastPanel].classList.remove('enterScreen');
        panelList[lastPanel].classList.remove('exitScreen');
    }, transitionTime); // css has the 1.5 sec as the transition

    currentPanel = nextPanel;
}
