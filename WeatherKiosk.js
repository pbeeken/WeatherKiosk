/**
 * RunClock
 * This is a self re-asserting timer that displays a running clock in the 'clock'
 * box as the web page is active.
 */
 function RunClock() {
    const today = new Date()
    document.getElementById('clock').innerHTML =  today.toLocaleTimeString('en-US')
    setTimeout(startTime, 1000)
    }

/**
 * FetchCSV
 * Quick and dirty retrieval of csv data from self updating server that gives useful information
 * The caller provides the call back function which is taylored to digest the information
 * @param {function} callback is the function that accepts an array of an array of strings of the content of the csv sources  
*/
function FetchCSV(callback) {   
    var xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    let url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNicoE1m6n7XfxcWa-inkdc0RmE_QcWepnUa4PxKFA3UB-uzMvCsUhAjsl9cc8IPQT6Fct4wKMvm4N/pub?gid=281261321&single=true&output=csv"
    xobj.open('GET', url, true);
    xobj.onreadystatechange = function () {
        if (xobj.readyState == 4 && xobj.status == "200") {
            //callback(JSON.parse(xobj.responseText))
            let resp = (xobj.responseText).replace(/\r/g,"") // eliminate the lf
            resp = resp.split("\n")
            for (i in resp)
                resp[i] = resp[i].split(",").slice(1) // I built the sources so that the first column is always empty (or unimportant)
            callback(resp.slice(2))
            }
        }
    xobj.send(null);  
    }

/**
 * SunriseSunset
 * A call back that processes the table of information fetched to pull and populate the appropiate fields
 * @param {Array<Array<string>>} csvData is an array of an array of strings that represent the 
 */
function SunriseSunset(csvData) {
    let now = new Date()
    let time = now.getHours()*60. + now.getMinutes()  // minutes past midnight
    let todaySunset = 60. * parseInt(csvData[2][4].slice(0,2)) + parseInt(csvData[2][4].slice(3,5)) // minutes past midnight
    //console.log(`-${time}-${todaySunset}- ${time > (20 + todaySunset)}`)
    if (time < (20 + todaySunset)) // 20 min after sunset switch to tomorrow's datum
        document.getElementById("suncondition").innerHTML = `${csvData[1][0]}, ${csvData[1][1]} Sunrise is at ${csvData[1][3].slice(0,-3)}, Sunset at ${csvData[1][4].slice(0,-3)}`  // today
    else
        document.getElementById("suncondition").innerHTML = `${csvData[2][0]}, ${csvData[2][1]} Sunrise is at ${csvData[2][3].slice(0,-3)}, Sunset at ${csvData[2][4].slice(0,-3)}`  // tomorrow

    }

function PostData() {
    /** Get and post the sunrise and sunset data */
    FetchCSV(SunriseSunset)
    }