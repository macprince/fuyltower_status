import os
import sys
import json
import time
import datetime

import requests

from flask import Flask
from flask import render_template
from markupsafe import escape

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

os.environ["TZ"] = "America/Chicago"
time.tzset()

# Load in config file
config = os.path.abspath(os.path.join(sys.path[0],"config.json"))
try:
    with open(config) as config_file:
        settings = json.load(config_file)
except IOError:
    logging.error("No config.json file found! Please create one!")
    sys.exit(2)

lnc_client = settings['lockncharge']
lnc_base_url = "https://api.lockncharge.io/v1"

def get_bearer_token():
    global token_data
    global lnc_auth

    token_data = requests.post(lnc_base_url+"/token", data = lnc_client).json()
    lnc_auth = {"Authorization": f"Bearer {token_data['access_token']}"}

def get_bays():
    response = requests.get(lnc_base_url+"/bays",headers=lnc_auth).json()
    bays = sorted(response['items'], key = lambda i: i['bayNumber'])
    return bays

def get_user_by_id(userId):
    user = requests.get(lnc_base_url+f"/station-users/{userId}",headers=lnc_auth).json()
    return user

def get_bay_user(bayNumber):
    bays = get_bays()
    bay = next(item for item in bays if item["bayNumber"] == int(bayNumber))
    user = get_user_by_id(bay['assignedUserId'])
    return user, bay

@app.before_request
def check_token():
    try:
        if "expires" in token_data:
            expires = token_data["expires"]
            now = int(time.time())
            if expires - now < (lnc_client['token_refresh_minutes'] * 60):
                print(f"Token is expiring in < {lnc_client['token_refresh_minutes']} min, requesting token...")
                get_bearer_token()
            #else:
                # print(f"Token still valid ({expires - now} seconds left)")
    except NameError:
        print("Token not found, requesting token...")
        get_bearer_token()


@app.route("/")
def show_bays_user():
    bays = get_bays()
    timestamp = datetime.datetime.now()
    return render_template('index.html', bays=bays, timestamp=timestamp)

@app.route("/admin")
def show_bays_admin():
    bays = get_bays()
    timestamp = datetime.datetime.now()
    return render_template('admin.html', bays=bays, timestamp=timestamp)

@app.route("/admin/<bayNumber>")
def show_bay(bayNumber):
    user, bay = get_bay_user(bayNumber)
    return render_template('user.html', user=user, bay=bay)
