const sec = 1000
const min = 60 * sec

function refreshFrames() {
    console.log(`refreshFrames diabled.`)
    return // may not be needed
    try {
      let id = "ideal18"
      document.getElementById(id).src = document.getElementById(id).src
      console.log(`${id} updated`)
      id = "dayboat"
      document.getElementById(id).src = document.getElementById(id).src
      console.log(`${id} updated`)
    } catch (error) {
      console.log(`Update frame failed \n ${error}`)
    }
    setTimeout(refreshFrames, 30 * sec)
}

/**
 * RunClock
 * This is a self re-asserting timer that displays a running clock in the 'clock'
 * box as the web page is active.
 */
function RunClock() {
    const today = new Date()
    document.getElementById('clock').innerHTML =  today.toLocaleTimeString('en-US')
    setTimeout(RunClock, 1 * sec)
}

/**
 * UpdateForecast
 * Use javascript to update forecast table
 */
function updateForecast() {
    document.getElementById('forecast').src = document.getElementById('forecast').src

    setTimeout(updateForecast, 15 * min) // reasonable update for updates
}


/**
 * UpdateGraphs
 * Using javascript to update graphs is less disruptive than refreshing the whole screen
 */
function updateGraphs() {
    const now = new Date()
    // Note the trick to get the browser to refresh the images
    document.getElementById('tidegraph').src = "resources/tideGraph.png?" + now.getMilliseconds()
    document.getElementById('tidegraphic').src = "resources/tideGraphic.png?" + now.getMilliseconds()
    document.getElementById('windgraph').src = "resources/windGraph.png?" + now.getMilliseconds()
    document.getElementById('tidetable').src = document.getElementById('tidetable').src

    setTimeout(updateGraphs, 5 * min) // five minutes
}

/**
 * Each of the tree entries below carry the following information returned from USNO:
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
}


/**
 * fetchUSNavalObsData
 * @param {Date} date
 * @param {function} callback  function to handle the json data
 */
function fetchUSNavalDailyData(theDate, when) {
    const datestr = theDate.toLocaleDateString()
    let url = `http://localhost:8000/cgi-bin/sunFetch.py?date=${datestr}`

    var xhr = new XMLHttpRequest()
    xhr.overrideMimeType("application/json")

    xhr.onerror = function() {
         console.log('There was an error!')
       };

    xhr.onreadystatechange = function () {
        astroData[when] = {error: xhr.status, response: xhr.responseText, state: xhr.readyState}
        if (xhr.readyState == 4 && xhr.status == "200") {  // if the final state is good store data.
            datum =  (JSON.parse(xhr.responseText)).properties.data
            datum.requestedDate = theDate
            astroData[when] = datum
            }
        }

    xhr.open('GET', url, true)
    xhr.send();
}

/**
 * NASA's Lookup Table
 * root: https://moon.nasa.gov/internal_resources/### where ### is based on lookup
 **/
imageTableNASA = {
    rootURL: "https://moon.nasa.gov/internal_resources/",
    // basic table
    newmoon: 366,
    waxingcrescent: 368,
    firstquarter: 367,
    waxinggibbous: 365,
    fullmoon: 364,
    waninggibbous: 363,
    lastquarter: 362,
    waningcrescent: 361,
}

/**
 * Mooninfo.org's table (more images)
 * root: local or https://www.mooninfo.org/images/50/{name}
 */
imageTableMoon = {
    rootURL: 'https://www.mooninfo.org/images/50/',
    // basic table
    newmoon:            'New_Moon.jpg',
    waxingcrescent:     'Waxing_Crescent_25.jpg',
    firstquarter:       'First_Quarter.jpg',
    waxinggibbous:      'Waxing_Gibbous_75.jpg',
    fullmoon:           'Full_Moon.jpg',
    waninggibbous:      'Waning_Gibbous_75.jpg',
    lastquarter:        'Last_Quarter.jpg',
    waningcrescent:     'Waning_Crescent_25.jpg',
    // extensions to above
    waxingcrescent_0:   'Waxing_Crescent_0.jpg',
    waxingcrescent_5:   'Waxing_Crescent_5.jpg',
    waxingcrescent_10:  'Waxing_Crescent_10.jpg',
    waxingcrescent_15:  'Waxing_Crescent_15.jpg',
    waxingcrescent_20:  'Waxing_Crescent_20.jpg',
    waxingcrescent_25:  'Waxing_Crescent_25.jpg',
    waxingcrescent_30:  'Waxing_Crescent_30.jpg',
    waxingcrescent_35:  'Waxing_Crescent_35.jpg',
    waxingcrescent_40:  'Waxing_Crescent_40.jpg',
    waxingcrescent_45:  'Waxing_Crescent_45.jpg',

    waxinggibbous_55:   'Waxing_Gibbous_55.jpg',
    waxinggibbous_60:   'Waxing_Gibbous_60.jpg',
    waxinggibbous_65:   'Waxing_Gibbous_65.jpg',
    waxinggibbous_70:   'Waxing_Gibbous_70.jpg',
    waxinggibbous_75:   'Waxing_Gibbous_75.jpg',
    waxinggibbous_80:   'Waxing_Gibbous_80.jpg',
    waxinggibbous_85:   'Waxing_Gibbous_85.jpg',
    waxinggibbous_90:   'Waxing_Gibbous_90.jpg',
    waxinggibbous_95:   'Waxing_Gibbous_95.jpg',

    waninggibbous_95:   'Waning_Gibbous_95.jpg',
    waninggibbous_90:   'Waning_Gibbous_90.jpg',
    waninggibbous_85:   'Waning_Gibbous_85.jpg',
    waninggibbous_80:   'Waning_Gibbous_80.jpg',
    waninggibbous_75:   'Waning_Gibbous_75.jpg',
    waninggibbous_70:   'Waning_Gibbous_70.jpg',
    waninggibbous_65:   'Waning_Gibbous_65.jpg',
    waninggibbous_60:   'Waning_Gibbous_60.jpg',
    waninggibbous_55:   'Waning_Gibbous_55.jpg',
    waninggibbous_50:   'Waning_Gibbous_50.jpg',

    waningcrescent_40:  'Waning_Crescent_40.jpg',
    waningcrescent_35:  'Waning_Crescent_35.jpg',
    waningcrescent_30:  'Waning_Crescent_30.jpg',
    waningcrescent_25:  'Waning_Crescent_25.jpg',
    waningcrescent_20:  'Waning_Crescent_20.jpg',
    waningcrescent_15:  'Waning_Crescent_15.jpg',
    waningcrescent_10:  'Waning_Crescent_10.jpg',
    waningcrescent_5:   'Waning_Crescent_5.jpg',
    waningcrescent_0:   'Waning_Crescent_0.jpg',
}

/**
 * update the lunar data slug (whereever I decide to put it). It calculates the icon to use
 * for displaying the moon based on the fracillum.
 * IMPORTANT: This presumes the global `astroData` has been populated
 */
function updateLunarData() {

    if (typeof astroData === 'undefined' || typeof astroData.today === 'undefined') {
        setTimeout(updateLunarData, 1*sec)
        return // do nothing because astroData hasn't been fully populated
	}
    let currentdata = astroData.today
    let closestdata = astroData.today.closestphase  // BTW this could be in the past!
    let imageTable = imageTableMoon

    let rootURL = imageTable.rootURL

    console.log(`Lunar update ${currentdata.curphase}`)

    // console.log(currentdata.fracillum.slice(0,-1)) // cut off %
    // the basic shape is from the library
    let namedPhase = currentdata.curphase.toLocaleLowerCase().replace(' ','')

    let fracillum = 1.0 * currentdata.fracillum.slice(0,-1)
    fracillum = Math.round(fracillum/5)*5 // round to the nearest 5%
    // console.log(` ${currentdata.fracillum} -> ${fracillum}`)

    if (typeof imageTable[namedPhase + '_' + fracillum] !== 'undefined') {
    // console.log(rootURL + imageTable[namedPhase + '_' + fracillum])
        document.getElementById("moon").src =  rootURL + imageTable[namedPhase + '_' + fracillum]
    // console.log(namedPhase)
    }
    else {
    // console.log(rootURL + imageTable[namedPhase])
        document.getElementById("moon").src =  rootURL + imageTable[namedPhase]
    // console.log(namedPhase)
    }

    setTimeout(updateLunarData, 10*min)

}

/**
 * update the sunrise sunset slug in the footer. It displays the current day's data
 * until after sunset when is switches to the next day.
 * IMPORTANT: This presumes the global `astroData` has been populated
 */
function updateSunRiseSunset() {

    // We need these items to be populated so we exit quietly in case they are not.
    if (typeof astroData === 'undefined' || typeof astroData.today === 'undefined' || typeof astroData.tomorrow === 'undefined') {
        setTimeout(updateSunRiseSunset, 1*sec) // rerun in a second or so
        return // do nothing because astroData hasn't been fully populated
	}

    let now = new Date()
    now.setMinutes(now.getMinutes()+20) // push it up by 20 minutes
    let theSunToday = astroData.today.sundata
    let theSunTomor = astroData.tomorrow.sundata

    document.getElementById("suncondition").innerHTML = `${theSunToday.time} ${theSunTomor.time}`

    // TODO: When the DST parameter is used USNO server tacks on ' DT' or ' ST' to the time. Do I keep it?  Not always there.
    //       I am stripping it. This tool is only used during DST so having the designator clutters the display
//    let setTime = theSunToday[3].time.slice(0,5).split(':') // sometimes it is there and sometimes not, this takes care of both
    let setTime = theSunToday[3].time.replace(/  [DS]T/,'').split(':') // sometimes it is there and sometimes not, this takes care of both

    let todaySunset = new Date(now.getFullYear(), now.getMonth(), now.getDate(), setTime[0], setTime[1])
    // console.log(`${setTime}`)
    // console.log(`${todaySunset} ${now} rel ${now>todaySunset}`)

    if (now > todaySunset) // 20 min after sunset (see above) switch to tomorrow's datum
        document.getElementById("suncondition").innerHTML = `Tomorrow's Sunrise will be at ${theSunTomor[1].time.replace(/  [DS]T/,'')}, Sunset at ${theSunTomor[3].time.replace(/  [DS]T/,'')}`
    else
        document.getElementById("suncondition").innerHTML = `Today's Sunrise is ${theSunToday[1].time.replace(/  [DS]T/,'')}, Sunset at ${theSunToday[3].time.replace(/  [DS]T/,'')}`  

    setTimeout(updateSunRiseSunset, 10 * min) // rerun in 10 minutes
}

/**
 * will load the global astroData parameter with the moon and solar data needed for various 
 * display routines.
 * @param {Date} testDate is an optional parameter to override the default of 'today'
 */
function loadAstroData(testDate) {
    if (testDate === undefined) day = new Date()
    else day = testDate
    day.setDate(day.getDate()-1)
    fetchUSNavalDailyData(day, 'yesterday')
    day.setDate(day.getDate()+1)
    fetchUSNavalDailyData(day, 'today' )
    day.setDate(day.getDate()+1)
    fetchUSNavalDailyData(day, 'tomorrow' )
}

function PostDataWeather() {
    /** Get and post the sunrise and sunset data */
    loadAstroData()
    updateGraphs()
    setTimeout(updateSunRiseSunset, 10*sec) // first run
    setTimeout(updateLunarData, 10*sec) // first run
}

function PostDataSchedule() {
    /** Get and post the sunrise and sunset data */
    loadAstroData()

    setTimeout(updateSunRiseSunset, 5*sec) // first run
//    setTimeout(updateLunarData, 5*sec) // first run
}
