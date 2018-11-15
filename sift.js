import {CLIENT_ID} from '/passwords.js';
import {API_KEY} from '/passwords.js';
handleClientLoad();

var btn = $('<input type="button" value="カレンダーに追加">');
btn.appendTo($('input[name="btn_after"]').parent());
btn.click(det_add);
var authorizeButton = $('<button id="authorize_button" style="display: none;">Authorize</button>').click(handleAuthClick)
var signoutButton = $('<button id="signout_button" style="display: none;">Sign Out</button>')
    .appendTo($('input[name="btn_after"]').parent());

var SCOPES = "https://www.googleapis.com/auth/calendar";
var DISCOVERY_DOCS = ["https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"];

/**
 *  On load, called to load the auth2 library and API client library.
 */
function handleClientLoad() {
    gapi.load('client:auth2', initClient);
}

/**
 *  Initializes the API client library and sets up sign-in state
 *  listeners.
 */
function initClient() {
    gapi.client.init({
        apiKey: API_KEY,
        discoveryDocs: DISCOVERY_DOCS,
        scope: SCOPES
    }).then(function () {
        // Listen for sign-in state changes.
        gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);

        // Handle the initial sign-in state.
        updateSigninStatus(gapi.auth2.getAuthInstance().isSignedIn.get());
        authorizeButton.onclick = handleAuthClick;
        signoutButton.onclick = handleSignoutClick;
    });
}

/**
 *  Called when the signed in status changes, to update the UI
 *  appropriately. After a sign-in, the API is called.
 */
function updateSigninStatus(isSignedIn) {
    if (isSignedIn) {
        authorizeButton.hide();
        signoutButton.show();
    } else {
        authorizeButton.show();
        signoutButton.hide();
    }
}

/**
 *  Sign in the user upon button click.
 */
function handleAuthClick(event) {
    gapi.auth2.getAuthInstance().signIn();
}

/**
 *  Sign out the user upon button click.
 */
function handleSignoutClick(event) {
    gapi.auth2.getAuthInstance().signOut();
}

function det_add() {
    var event = {
        'summary': 'バイト',
        'description': 'Made by userscript',
        "reminders": {
            "useDefault": false
        },
        'start': {
            'dateTime': '',
        },
        'end': {
            'dateTime': '',
        }
    };
    //始まりと終わりの年が配列に格納されている
    var year = $('.clr').text().match(/[0-9]{4}/g);
    year[0] = year[0].replace(/\s/g, '');
    year[1] = year[1].replace(/\s/g, '');
    //yearのうちどちらを使うかを選ぶセレクタ
    var year_sel = 0;
    $.each($('.def:eq(5) tr'), function (i, val) {
        if (i == 0) return true;
        if (/\s/g.test($(val).children('td:eq(1)').text())) return true;
        var day = $(val).children('th:eq(0)').text();
        var start_time = $(val).children('td:eq(0)').text();
        var end_time = $(val).children('td:eq(1)').text();


        day = day.replace(/\s/g, '');
        day = day.split("/");
        start_time = hm(start_time.replace(/\s/g, ''));
        end_time = hm(end_time.replace(/\s/g, ''));

        if (year[0] != year[1]) {
            //年越し時期の処理
            if (/1\//.test(day)) year_sel = 1;
        }
        var start = new Date(year[year_sel], day[0] - 1, day[1], start_time[0], start_time[1]);
        var end = new Date(year[year_sel], day[0] - 1, day[1], end_time[0], end_time[1]);
        event.start.dateTime = start.toISOString();
        event.end.dateTime = end.toISOString();
        add_event(event);
    });
}

function add_event(event) {
    var request = gapi.client.calendar.events.insert({
        'calendarId': 'primary',
        'resource': event
    });
    request.execute();

}

function hm(time) {
    return time.length == 4 ? [time.substr(0, 2), time.substr(2, 2)] : [time.substr(0, 1), time.substr(1, 2)];
}
