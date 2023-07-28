import requests
import uuid
import json
from datetime import datetime, timedelta
import time
from utils.utils import send_email
from config import CIVIC_EMAIL, CIVIC_PW


def get_date_time(start_time_str: str) -> str:
    reserve_date = datetime.today().date() + timedelta(days=3)
    timestamp = datetime.strptime(start_time_str, "%H:%M:%S").time()
    return datetime.combine(reserve_date, timestamp).strftime("%Y-%m-%dT%H:%M:%S")


def login(email, pw):
    session = requests.Session()
    data = {
        "email": email,
        "password": pw
    }
    response = session.post('https://rioc.civicpermits.com/Account/Login', headers={
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded"
    }, data=data, allow_redirects=False)
    if response.status_code == 302:
        if 'Set-Cookie' in response.headers:
            return response.headers['Set-Cookie']
        else:
            print("Set-Cookie header not found in the response.")
    else:
        print("Login failed")
        print(response.status_code, response.text)


def conflict_check() -> bool:
    check_url = "https://rioc.civicpermits.com/Permits/ConflictCheck"
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Cookie': auth_cookie
    }
    payload = {
        "FacilityNames": [
            "Tennis Courts"
        ],
        "FacilityIds": [
            "77c7f42c-8891-4818-a610-d5c1027c62fe"
        ],
        "Dates": [
            {
                "Start": start_time,
                "Stop": end_time
            }
        ]
    }
    response = requests.post(check_url, headers=headers, data=json.dumps(payload))
    # print(response, len(response.text))
    if (len(response.text)) > 2:
        return True
    else:
        return False


def post_reservation() -> str:
    post_url = 'https://rioc.civicpermits.com/Permits'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Cookie': auth_cookie
    }
    payload = {
        "Activity": "Tennis",
        "Events": [{
            "FacilityNames": ["Tennis Courts"],
            "FacilityIds": ["77c7f42c-8891-4818-a610-d5c1027c62fe"],
            "Dates": [{
                "Start": start_time,
                "Stop": end_time
            }
            ]
        }
        ],
        "Responses": [{
            "Id": uuid.uuid4().hex,
            "StringValue": "Tennis",
            "CheckboxValue": []
        }, {
            "Id": uuid.uuid4().hex,
            "StringValue": "4",
            "CheckboxValue": []
        }, {
            "Id": uuid.uuid4().hex,
            "StringValue": "No",
            "CheckboxValue": []
        }, {
            "Id": uuid.uuid4().hex,
            "StringValue": "No",
            "CheckboxValue": []
        }, {
            "Id": uuid.uuid4().hex,
            "StringValue": "Yes, weekdays evenings are good",
            "CheckboxValue": []
        }, {
            "Id": uuid.uuid4().hex,
            "StringValue": "Yes",
            "CheckboxValue": ["Yes"]
        }, {
            "Id": uuid.uuid4().hex,
            "StringValue": "No",
            "CheckboxValue": []
        }, {
            "Id": uuid.uuid4().hex,
            "StringValue": "No",
            "CheckboxValue": []
        }, {
            "Id": uuid.uuid4().hex,
            "StringValue": "No",
            "CheckboxValue": ["No"]
        }, {
            "Id": uuid.uuid4().hex,
            "StringValue": "No",
            "CheckboxValue": []
        }
        ]
    }
    # fetch_resp = requests.post(fetch_url, headers=headers, data={})
    post_resp = requests.post(post_url, headers=headers, data=json.dumps(payload))
    print(post_resp.status_code, post_resp.text, post_resp.content)
    if post_resp.status_code == 200:
        return f'{start_time} ~ {end_time} successfully booked.'
    if post_resp.status_code == 400:
        return 'Failed to book. Website is not available.'
    else:
        return f'Unknown error. Status code: {post_resp.status_code}, content: {post_resp.content}'


time.sleep(1)

subject = 'Tennis court reservation alert'

# reservation timestamp format: "2023-07-27T19:00:00"
start_time = get_date_time('19:00:00')
end_time = get_date_time('20:00:00')

auth_cookie = login(CIVIC_EMAIL, CIVIC_PW)
if_conflict = conflict_check()
if if_conflict:
    send_email(subject, f'{start_time} ~ {end_time} is already booked by someone else.')
else:
    res = post_reservation()
    send_email(subject, res)
