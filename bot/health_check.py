# health_check.py
import meraki_module
from intersight_auth import IntersightAuth
import math
import datetime
import json
import os
import re
import requests
import sys
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder


# A simple command that gets the computePhysicalSummary from Intersight
def get_intersight_operState_percent():
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    if INTERSIGHT_AUTH:
        api_response = requests.get(intersight_base_url + "compute/PhysicalSummaries" + "?$select=Name,Model,OperState", auth=INTERSIGHT_AUTH)
        json_response = api_response.json()
        ucsb_operStates = [result["OperState"] for result in json_response["Results"] if result["Model"].startswith('UCSB')]
        if len(ucsb_operStates) > 0:
            ucsb_percent_ok = round((ucsb_operStates.count('ok') / len(ucsb_operStates) * 100), 2)
        else:
            ucsb_percent_ok = "N/A"
        ucsc_operStates = [result["OperState"] for result in json_response["Results"] if result["Model"].startswith('UCSC')]
        if len(ucsc_operStates) > 0:
            ucsc_percent_ok = round((ucsc_operStates.count('ok') / len(ucsc_operStates) * 100), 2)
        else:
            ucsc_percent_ok = "N/A"
        hx_operStates = [result["OperState"] for result in json_response["Results"] if result["Model"].startswith('HX')]
        if len(hx_operStates) > 0:
            hx_percent_ok = round((hx_operStates.count('ok') / len(hx_operStates) * 100), 2)
        else:
            hx_percent_ok = "N/A"
        intersight_operState_percents = [ucsb_percent_ok, ucsc_percent_ok, hx_percent_ok]
        return intersight_operState_percents
    else:
        return "Authentication for Intersight is incomplete."
    return 


def get_meraki_deviceOnline_percent():
    response = meraki_module.get_device_statuses(meraki_api_key, meraki_org_id)
    devices_status = [device["status"] for device in response if device["name"]]
    percent_online = round((devices_status.count('online') / len(devices_status) * 100), 2)
    return percent_online


def get_meraki_wirelessHealth_percent():
    current_time_epoch = int(datetime.datetime.now().timestamp())
    yesterday_epoch = int((datetime.datetime.now() - datetime.timedelta(1)).timestamp())
    url = 'https://api.meraki.com/api/v0/organizations/' + meraki_org_id + '/networks/' + meraki_network_id + '/connectionStats?t0=' + str(yesterday_epoch) + '&t1=' + str(current_time_epoch)
    headers = { 'X-Cisco-Meraki-API-Key': meraki_api_key }
    response = requests.get(url, headers=headers)
    json_response = response.json()
    if json_response:
        total = json_response["assoc"] + json_response["auth"] + json_response["dhcp"] + json_response["dns"] + json_response["success"]
        percent_wirelessHealth = round((json_response["success"] / total * 100), 2)
    else:
        percent_wirelessHealth = "N/A"
    return percent_wirelessHealth


def write_current_percents(room_id, current_percents):
    prev_percents_filename = working_dir + '/data/' + room_id + ".txt"
    print(prev_percents_filename)
    with open(prev_percents_filename, "a") as f:
        current_percents_line = ",".join([str(p) for p in current_percents])
        f.write(current_percents_line + '\n')


def get_prev_percents(room_id):
    prev_percents_filename = working_dir + '/data/' + room_id + ".txt"
    print(prev_percents_filename)
    try:
        with open(prev_percents_filename) as f:
            prev_percents_list = f.readlines()
        print(prev_percents_list)
        prev_percents = prev_percents_list[len(prev_percents_list) - 1].strip().split(',')
    except:
        prev_percents = ["N/A"] * 5
    print(prev_percents)
    return prev_percents


def send_health_check(room_id, current_percents, prev_percents):
    # Determine Healthy or Unhealthy
    intersight_operState_threshold = 95.0
    meraki_deviceOnline_threshold = 90.0
    overallHealthy = True
    if any(percent < intersight_operState_threshold for percent in current_percents[:3] if percent != "N/A"):
        overallHealthy = False
    if any(percent < meraki_deviceOnline_threshold for percent in current_percents[3:] if percent != "N/A"):
        overallHealthy = False
    if overallHealthy:
        image_name = "healthy.png"
    else:
        image_name = "unhealthy.png"
    image_url = os.path.join(working_dir, image_name)
    # Determine change (if any)
    percent_diffs = []
    for i, current_p in enumerate(current_percents):
        if prev_percents[i] == "N/A" or current_p == "N/A":
                percent_diff = "+/-0"
        else:
            if current_p != float(prev_percents[i]):
                percent_diff = current_p - float(prev_percents[i])
                if percent_diff > 0:
                    percent_diff = "+" + str(percent_diff)
                else:
                    percent_diff = str(percent_diff)
            else:
                percent_diff = "+/-0"
        percent_diffs.append(percent_diff)
    print(current_percents)
    print(prev_percents)
    print(percent_diffs)
    # Assemble message and send
    m = MultipartEncoder({
        "roomId": room_id,
        "markdown": "[**Intersight:**](https://intersight.com/)  \n- UCS-B OperState 'ok': **" + str(current_percents[0]) + "%** (" + percent_diffs[0] + "%)  \n- UCS-C OperState 'ok': **" + str(current_percents[1]) + "%** (" + percent_diffs[1] + "%)  \n- HX OperState 'ok':     **" + str(current_percents[2]) + "%** (" + percent_diffs[2] + "%)\n\n[**Meraki**](https://meraki.cisco.com/)  \n- Organization Devices 'online': **" + str(current_percents[3]) + "%** (" + percent_diffs[3] + "%)  \n- 24 Hour Wireless Health:       **" + str(current_percents[4]) + "%** (" + percent_diffs[4] + "%)",
        "files": (image_name, open(image_url, 'rb'), 'image/png')
    })
    headers = {
        'Authorization': 'Bearer ' + teams_token,
        'Content-Type': m.content_type
    }
    teams_post_message_response = requests.post(
        'https://api.ciscospark.com/v1/messages',
        data=m,
        headers=headers
    )
    print(teams_post_message_response)


def do_health_check(room_id):
    # Get Health Percentages
    current_percents = get_intersight_operState_percent()
    current_percents.append(get_meraki_deviceOnline_percent())
    current_percents.append(get_meraki_wirelessHealth_percent())
    prev_percents = get_prev_percents(room_id)
    write_current_percents(room_id, current_percents)
    send_health_check(room_id, current_percents, prev_percents)


# Setup
load_dotenv(os.path.join('/home/bingersoprojects/fy19q4-asic-merakisight', '.env'))
working_dir = os.getenv("MERAKISIGHT_PATH")
intersight_base_url = 'https://www.intersight.com/api/v1/'
intersight_secret_file = os.path.join(working_dir, "SecretKey.txt")
intersight_api_key = os.getenv("INTERSIGHT_API_KEY")
INTERSIGHT_AUTH = IntersightAuth(
    secret_key_filename=intersight_secret_file,
    api_key_id=intersight_api_key
)
meraki_api_key = os.getenv("MERAKI_API_KEY")
teams_token = os.getenv("TEAMS_BOT_TOKEN")
meraki_org_id = os.getenv("MERAKI_ORG_ID")
meraki_network_id = os.getenv("MERAKI_NETWORK_ID")

prev_percents_regex = re.compile(r"Intersight: UCS-B OperState 'ok': (.+?)%.* UCS-C OperState 'ok': (.+?)%.* HX OperState 'ok': (.+?)%.* Meraki Organization Devices 'online': (.+?)%.* 24 Hour Wireless Health: (.+?)%.*")

if __name__ == "__main__":
    room_id = sys.argv[1]
    do_health_check(room_id)
    
    