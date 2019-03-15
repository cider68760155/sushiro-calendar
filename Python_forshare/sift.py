from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import json
from pytz import timezone
from datetime import timedelta
from datetime import datetime

from selenium import webdriver
import chromedriver_binary

import re
import csv

from urls import url_generator

# If modifying these scopes, delete the file token.json.
#SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    service=buildCreds()
    for event in search_existing(service)["items"]:
        delete_event(service,event)
    for URL in url_generator():
        for event in det_add(URL):
            add_event(service,event)


def buildCreds():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def search_existing(service):
    today=datetime.now()
    events=service.events().list(
        calendarId="primary",
        timeMin=set_timezone(get_from_weeks(today,0,1)),
        timeMax=set_timezone(get_from_weeks(today,2,1)),
        showDeleted=False,
        singleEvents=True,
        q="auto generated"
    ).execute()
    return events

def delete_event(service,event):
    result=service.events().delete(calendarId='primary', eventId=event["id"]).execute()
    return result


def det_add(URL):
    events = []
    year_sel=0
    driver = webdriver.Chrome()
    driver.get(URL[1])
    year = re.findall(r'[0-9]{4}', driver.find_element_by_class_name('clr').text)
    year=[int(i) for i in year]
    sifts = get_sift(driver, URL[1])
    sifts.extend(get_sift(driver, URL[2]))
    for sift in sifts:
        if (sift[2] != '') & (sift[2] != '未作成'):
            event = json.loads('{\
                "summary": "",\
                "description": "auto generated",\
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
            event['summary']=URL[0]
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
