from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import json
from pytz import timezone
from datetime import timedelta
from datetime import datetime

from selenium import webdriver
import chromedriver_binary

import re

from urls import URL1,URL2,URL3

# If modifying these scopes, delete the file token.json.
#SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = 'https://www.googleapis.com/auth/calendar'


def main():
    service=buildCreds()
    for event in search_existing(service)["items"]:
        delete_event(service,event)
    for event in det_add():
        add_event(service,event)


def buildCreds():
    store = file.Storage('dist/token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('dist/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    return build('calendar', 'v3', http=creds.authorize(Http()))


def search_existing(service):
    today=datetime.now()
    events=service.events().list(
        calendarId="primary",
        timeMin=set_timezone(get_from_weeks(today,0,1)),
        timeMax=set_timezone(get_from_weeks(today,3,1)),
        showDeleted=False,
        singleEvents=True,
        q="made by python script"
    ).execute()
    return events

def delete_event(service,event):
    result=service.events().delete(calendarId='primary', eventId=event["id"]).execute()
    return result


def det_add():
    events = []
    year_sel=0
    driver = webdriver.Chrome()
    driver.get(URL1)
    year = re.findall(r'[0-9]{4}', driver.find_element_by_class_name('clr').text)
    year=[int(i) for i in year]
    sifts = get_sift(driver, URL1)
    sifts.extend(get_sift(driver, URL2))
    sifts.extend(get_sift(driver, URL3))
    for sift in sifts:
        if (sift[2] != '') & (sift[2] != '未作成'):
            event = json.loads('{\
                "summary": "バイト",\
                "description": "Made by python script",\
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
            monthDay = sift[0].split('/')
            monthDay=[int(n) for n in monthDay]
            #年末用処理
            if (year[0]!=year[1])&(monthDay[0]=='1'):
                year_sel=1
            start = hm(sift[2])
            end = hm(sift[3])
            event["start"]["dateTime"] = set_timezone(datetime(year[year_sel], monthDay[0], monthDay[1], start[0], start[1]))
            event["end"]["dateTime"] = set_timezone(datetime(year[year_sel], monthDay[0], monthDay[1], end[0], end[1]))
            events.append(event)
    driver.close()
    return events


def add_event(service, event):
    result = service.events().insert(calendarId='primary', body=event).execute()
    return result


def get_sift(driver, url):
    ret = []
    driver.get(url)
    sift_table = driver.find_elements_by_class_name("def")[5]
    for row in sift_table.find_elements_by_tag_name("tr")[1:]:
        ret.append(row.text.split(' ')[:4])
    return ret


def get_from_weeks(today,delta,weekday):
    #todayのdelta週後のweekday曜日のdatetimeオブジェクトを返す
    today=today.isocalendar()
    return datetime.strptime("{} {} {}".format(today[0],today[1]-1+delta,weekday),"%Y %W %w")


def set_timezone(datetime_naive):
    tz_tokyo = timezone("Asia/Tokyo")
    # datetime(naive) -> datetime(Asia/Tokyo)
    datetime_tokyo = tz_tokyo.localize(datetime_naive)
    return datetime_tokyo.isoformat()


def hm(time):
    if len(time) == 3:
        return [int(time[0]), int(time[1:3])]
    else:
        return [int(time[0:2]), int(time[2:4])]


if __name__ == '__main__':
    main()
