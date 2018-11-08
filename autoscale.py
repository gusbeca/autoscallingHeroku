#!/usr/bin/env python3
import os
APP = "auto-s-w"
KEY = os.environ['H_API_KEY']
PROCESS = "worker"

def scale(size):
    payload = {'quantity': size}
    json_payload = json.dumps(payload)
    url = "https://api.heroku.com/apps/" + APP + "/formation/" + PROCESS
    try:
        result = requests.patch(url, headers=HEADERS, data=json_payload)
    except:
        print("test!")
        return None
    if result.status_code == 200:
        return "Success!"
    else:
        return "Failure"
