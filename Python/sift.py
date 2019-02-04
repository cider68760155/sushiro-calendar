from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json
from pytz import timezone
from datetime import timedelta
# If modifying these scopes, delete the file token.json.
#SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = 'https://www.googleapis.com/auth/calendar'


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    det_add(service)


def det_add(service):
    event = json.loads('{\
        "summary": "サンプルの予定",\
        "description": "Made by userscript",\
        "reminders": {\
            "useDefault": false\
        },\
        "start": {\
            "dateTime": ""\
        },\
        "end": {\
            "dateTime": ""\
        }\
    }')
    event["start"]["dateTime"] = set_timezone(2019,2,5,0,0).isoformat()
    event["end"]["dateTime"] = set_timezone(2019,2,5,0,0).isoformat()
    #タイムゾーン指定必要か確認！
    add_event(service,event)


def set_timezone(year, month, day, hour, minute):
    tz_tokyo = timezone("Asia/Tokyo")
    # naiveのdatetime作成
    datetime_naive = datetime.datetime(year, month, day, hour, minute)

    # datetime(naive) -> datetime(Asia/Tokyo)
    datetime_tokyo = tz_tokyo.localize(datetime_naive)
    return datetime_tokyo

def add_event(service,event):
    result=service.events().insert(calendarId='primary', body=event).execute()
    

if __name__ == '__main__':
    main()
