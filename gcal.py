

from __future__ import print_function
import httplib2
import json
import os, time, subprocess
from gpiozero import Button

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from datetime import datetime, timedelta

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Google Calendar Alarm'

# Global configuration settings
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()           # initiate Parser and read the configuration file
parser.read('gcal.cfg')

apiKey = parser.get('alarm','key')

try:
  sound = parser.get('alarm', 'sound')
except: sound = os.path.join('sounds','alarm.wav')
calendar = parser.get('alarm', 'calendar')

try:
  startSound = parser.get('alarm', 'sound')
except: startSound = os.path.join('sounds','carillon.wav')


try:
    import ssl
except ImportError:
    print ("error: no ssl support")

#Global variables
alarmLocation = 'Gliwice'
button = Button(4)
case = 'checkCalendar'
sleepTime = 60           #Time between calendar checking in seconds
reminderTime = 900      #Defualt reminder time in seconds; set to 15 minutes
ignoredEvents = []

def calendarReady():
    args = ["aplay",startSound]
    alarm = subprocess.Popen(args)
    return


def travelTimeTo(eventLocation):
    distanceURL = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=" + alarmLocation +"&destinations=" + eventLocation + "&key=" + apiKey
    h = httplib2.Http(".cache")
    (resp_headers, content) = h.request(distanceURL, "GET")
    contentJSON = json.loads(content)
    travelTime = contentJSON['rows'][0]['elements'][0]['duration']['value']
    return travelTime

def ignoreEvent():
    ignoredEvents.append(eventUID)
    return

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-alarm.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def playSound():
    global case
    case = 'sleep'
    args = ["aplay",sound]
    alarm = subprocess.Popen(args)
    global button
    button.when_pressed = alarm.terminate
    button.when_released = ignoreEvent
    return



def checkCalendar():
    global case
    case = 'sleep'

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    nowpt =(datetime.now()+timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    today,nowts = nowpt.split()
    nowts = datetime.strptime(nowts,'%H:%M:%S')

    eventsResult = service.events().list(
        calendarId=calendar, timeMin=now, maxResults=2, singleEvents=True,
        orderBy='startTime').execute()

    events = eventsResult.get('items', [])
    for event in events:
        eventLocation = event.get('location','Rybnik')
        global eventUID
        eventUID = event.get('iCalUID')
        travelTime = travelTimeTo(eventLocation) if eventLocation != 'Rybnik' else  0
        start = event['start'].get('dateTime', event['start'].get('date'))
        if len(start)<12: continue # all day event
        eventDay,est=start.split('T')
        ests = datetime.strptime(est.split('+')[0],'%H:%M:%S')
        alarmTime = travelTime + reminderTime
        if eventDay == today and (ests-nowts).seconds <= alarmTime and eventUID not in ignoredEvents:
            print(nowpt,"Sounding alarm for ", start, event['summary'])
            case = 'playSound'
            return

def switch():
    return {
        'playSound': playSound,
        'checkCalendar': checkCalendar,
        'sleep': sleep
    }[case]()

def sleep():
    global case
    case = 'checkCalendar'
    #print('sleeping')
    time.sleep(sleepTime)
    return

calendarReady()

def main():
    while True:
      switch()

if __name__ == '__main__':
    main()
