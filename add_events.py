########################################
# Adding Events into Google Calendar
# Mohammad Mahdavi
# moh.mahdavi.l@gmail.com
# January 2019
# Big Data Management Group
# TU Berlin
# All Rights Reserved
########################################


########################################
import os
import datetime
import pickle
import pandas
import googleapiclient.discovery
import google_auth_oauthlib.flow
import google.auth.transport.requests
########################################


########################################
def add_event(event_dictionary):
    credentials = None
    if os.path.exists("token.pickle"):
        token = open("token.pickle", "rb")
        credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server()
        pickle.dump(credentials, open("token.pickle", "wb"))
    service = googleapiclient.discovery.build("calendar", "v3", credentials=credentials)
    event_result = service.events().insert(calendarId="primary", sendNotifications=True, sendUpdates="all", body=event_dictionary).execute()
    print "Event created: {}".format(event_result.get("htmlLink"))
########################################


########################################
if __name__ == "__main__":

    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    INPUT_FILE = "exam_events.csv"

    exam_events = pandas.read_csv(INPUT_FILE, sep=",", header="infer", encoding="utf-8", dtype=str,
                                  keep_default_na=False, low_memory=False).apply(lambda x: x.str.strip())

    for exam_event in exam_events.get_values():
        if exam_event[-1] == "Not answered yet":
            continue
        surname = exam_event[0]
        date, time_period = exam_event[-1].split(" ")
        start = datetime.datetime.strptime(date + " " + time_period.split("-")[0], "%d.%m.%y %H:%M").strftime("%Y-%m-%dT%H:%M:%S+01:00")
        end = datetime.datetime.strptime(date + " " + time_period.split("-")[1], "%d.%m.%y %H:%M").strftime("%Y-%m-%dT%H:%M:%S+01:00")

        event = {
            "summary": "DI Exam ({})".format(surname),
            "location": "EN 704",
            "description": "",
            "start": {
                "dateTime": "{}".format(start),
                "timeZone": "Europe/Berlin",
            },
            "end": {
                "dateTime": "{}".format(end),
                "timeZone": "Europe/Berlin",
            },
            "attendees": [
                {"email": "abedjan@tu-berlin.de"},
            ],
            "guestsCanModify": True,
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 1},
                ],
            },
        }

        add_event(event)
########################################
