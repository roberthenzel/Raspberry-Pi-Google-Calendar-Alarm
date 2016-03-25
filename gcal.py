# Simple calendar alarm
# Requires sound
# Author: Boyana Norris, brnorris03@gmail.com
#
# Disclaimer: Use at your own risk, no guarantees of continued or correct operation provided.

from __future__ import print_function
import httplib2
import os, time

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from datetime import datetime, timedelta
import logging

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

logging.basicConfig(filename='wakeup.log', filemode='w')

# Global configuration settings
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()           # initiate Parser and read the configuration file
parser.read('gcal.cfg')

q = parser.get('alarm','query')
try:
  sound = parser.get('alarm', 'sound')
except: sound = os.path.join('sounds','oceanwaves.wav')
calendar = parser.get('alarm', 'calendar')
date = (datetime.now() +timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
endDate = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

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
    command ="aplay" + " " + sound 
    os.system(command)
    return

def checkCalendar(service):
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    nowpt = time.strftime('%Y-%m-%d %H:%M:%S')
    today,nowts = nowpt.split()
    nowts = datetime.strptime(nowts,'%H:%M:%S')
    #print("Current time", nowpt)
    alarming = False

    #print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId=calendar, timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()

    events = eventsResult.get('items', [])
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if len(start)<12: continue # all day event
        day,ts=start.split('T')
        sts  = datetime.strptime(ts.split('-')[0],'%H:%M:%S')
        #print(start, event['summary'], (sts-nowts).seconds)
        if day == today and (sts-nowts).seconds <= 300:
            print(nowpt,"Sounding alarm for ", start, event['summary'])
            playSound()
            return  


def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    while True:
      checkCalendar(service)
      time.sleep(60)


if __name__ == '__main__':
    main()
