import os
import sys
import json
import time

import requests
import emoji

from flask import Flask
from markupsafe import escape

app = Flask(__name__)

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

@app.before_request
def get_bearer_token():
    global token_data
    global lnc_auth
    
    try:
        if "expires" in token_data:
            expires = token_data["expires"]
            now = int(time.time())
            if expires - now < 300:
                print("Token is expiring in < 5 min, requesting token...")
                token_data = requests.post(lnc_base_url+"/token", data = lnc_client).json()
                lnc_auth = {"Authorization": f"Bearer {token_data['access_token']}"}
            else:
                print(f"Token still valid ({expires - now} seconds left)")
    except NameError:
        print("Token not found, requesting token...")
        token_data = requests.post(lnc_base_url+"/token", data = lnc_client).json()
        lnc_auth = {"Authorization": f"Bearer {token_data['access_token']}"}

        


@app.route("/")
def show_bays():
    status_html = ""
    response = requests.get(lnc_base_url+"/bays",headers=lnc_auth).json()
    bays = sorted(response['items'], key = lambda i: i['bayNumber'])
    for bay in bays:
        if bay['assigned']:
            status = emoji.emojize(':white_large_square: In Use')
        else:
            status = emoji.emojize(':green_square: Available')
        status_html = status_html + f"<tr><td>{bay['bayNumber']}</td><td>{status}</td></tr>"
    output = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta http-equiv="x-ua-compatible" content="ie=edge">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

      <title>Charging Locker Status</title>


    </head>
    <body>
    <table>
    {status_html}
    </table>
    </body>
    </html>
    
    
    """
    return output