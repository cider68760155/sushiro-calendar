handleClientLoad();

var btn = $('<input type="button" value="カレンダーに追加" style="display: none;">');
btn.appendTo($('input[name="btn_after"]').parent());
btn.click(update_event);
var authorizeButton = $('<button id="authorize_button" style="display: none;">Authorize</button>').click(handleAuthClick)
    .appendTo($('input[name="btn_after"]').parent());
var signoutButton = $('<button id="signout_button" style="display: none;">Sign Out</button>')
    .appendTo($('input[name="btn_after"]').parent());
$('<pre id="content"></pre>').appendTo($('input[name="btn_after"]').parent());

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
        clientId: CLIENT_ID,
        discoveryDocs: DISCOVERY_DOCS,
        scope: SCOPES
    }).then(function () {
        // Listen for sign-in state changes.
        gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);

        // Handle the initial sign-in state.公式版はここのコメントアウト外す
        //updateSigninStatus(gapi.auth2.getAuthInstance().isSignedIn.get());
        btn.show();
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
        btn.show();
    } else {
        authorizeButton.show();
        signoutButton.hide();
        btn.hide();
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

function update_event(){
    delete_existing();
    var events=det_add();
    console.log(events);
    events.forEach(function(event,index){
        setTimeout(add_event(event),1000*index);
    });
    alert("追加が完了しました！");
}

function det_add() {
    /*格納形式
    event:google calendar APIに投げつけるjsonのひな型。
    year=[月曜日の年,日曜日の年];ほとんど一緒やけど、年末だけ違う。
    year_sel:基本0。年越ししたら1になる。
    day=[m,d];
    start_time=hhmm;０パディングはされていない。
    end_time:start_timeに同じ。
    start:start_timeをDate型に変換したもの。
    end:startに同じ。
    */
    var events=[];

    //取得
    var year = $('.clr').text().match(/[0-9]{4}/g);
    $.each($('.def:eq(5) tr'), function (i, val) {
        var event = {
            'summary': 'バイト',
            'description': 'Made by userscript',
            'reminders': {
                'useDefault': false
            },
            'start': {
                'dateTime': '',
            },
            'end': {
                'dateTime': '',
            }
        };
        //一行目は読み飛ばす
        if (i == 0) return true;
        //バイトが無い日は読み飛ばす
        if (/\s/g.test($(val).children('td:eq(1)').text())) return true;
        var year_sel = 0;
        var day = $(val).children('th:eq(0)').text();
        var start_time = $(val).children('td:eq(0)').text();
        var end_time = $(val).children('td:eq(1)').text();

        //整形
        year[0] = year[0].replace(/\s/g, '');
        year[1] = year[1].replace(/\s/g, '');
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

        //追加
        event.start.dateTime = start.toISOString();
        event.end.dateTime = end.toISOString();
        console.log(end);
        events.push(event);
    });
    return events;
}

function add_event(event) {
    var request = gapi.client.calendar.events.insert({
        'calendarId': 'primary',
        'resource': event
    });
    request.execute().then(function(response){
        console.log(response);
    });
}

function hm(time) {
    return time.length == 4 ? [time.substr(0, 2), time.substr(2, 2)] : [time.substr(0, 1), time.substr(1, 2)];
}

function listUpcomingEvents() {
    gapi.client.calendar.events.list({
        'calendarId': 'primary',
        'timeMin': (new Date()).toISOString(),
        'showDeleted': false,
        'singleEvents': true,
        'maxResults': 10,
        'orderBy': 'startTime'
    }).then(function (response) {
        var events = response.result.items;
        appendPre('Upcoming events:');

        if (events.length > 0) {
            for (i = 0; i < events.length; i++) {
                var event = events[i];
                var when = event.start.dateTime;
                if (!when) {
                    when = event.start.date;
                }
                appendPre(event.summary + ' (' + when + ')')
            }
        } else {
            appendPre('No upcoming events found.');
        }
    });
}

function appendPre(message) {
    var pre = document.getElementById('content');
    var textContent = document.createTextNode(message + '\n');
    pre.appendChild(textContent);
}

function delete_existing() {
    var events_list = {
        'calendarId': 'primary',
        'timeMin': '',
        'timeMax': '',
        'showDeleted': false,
        'singleEvents': true,
        'maxResults': 10,
        'q': 'userscript',
        'orderBy': 'startTime'
    }
    var range = $('.clr').text().match(/[0-9]+/g);
    var sday = new Date(range[0], range[1] - 1, range[2], 0, 0);
    var eday = new Date(range[3], range[4] - 1, range[5], 23, 59);
    events_list.timeMin = sday.toISOString();
    events_list.timeMax = eday.toISOString();
    gapi.client.calendar.events.list(events_list).then(function (response) {
        response.result.items.forEach(function (event) {
            gapi.client.calendar.events.delete({ 'calendarId': 'primary', 'eventId': event.id }).then(function(response){
                console.log(response);
            });
        });
    });
}
