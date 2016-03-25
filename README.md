# GoogleCalendarAlarm

Follow the directions [here](https://developers.google.com/google-apps/calendar/quickstart/python#prerequisites) to create a ```client_id.json``` file containing authentication credentials for your google calendar account. Place the file in the same directory as the gcal.py script.

Some basic settings are in the ```gcal.cfg``` file, which you can edit to specify a different sound file or calendar.

The first time you run it, use ```python gcal.py --noauth_local_webserver``` and follow the instructions.

Subsequently, run with ```python gcal.py```.
