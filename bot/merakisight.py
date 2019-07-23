# -*- coding: utf-8 -*-
"""
Sample code for using webexteamsbot
"""

import json
import os
import requests
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response
from health_check_demo import demo_health_check
from health_check import do_health_check
from intersight_auth import IntersightAuth


# Create a custom bot greeting function returned when no command is given.
# The default behavior of the bot is to return the '/help' command response
def greeting(incoming_msg):
    # Loopkup details about sender
    sender = bot.teams.people.get(incoming_msg.personId)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = "Hello {}, I'm a chat bot. ".format(sender.firstName)
    response.markdown += "See what I can do by asking for **/help**."
    return response


# Start the Merakisight monitoring
def add_scheduled_task(room_id, frequency):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    headers = {'Authorization': 'Token ' + bot.pythonanywhere_token}
    if frequency == "daily":
        payload = {
            "interval":"daily",
            "hour":"12", # This is in UTC
            "minute":"00",
            "command":"/home/" + bot.pythonanywhere_username + "/.virtualenvs/mysite-virtualenv/bin/python " + bot.path + "health_check.py " + room_id,
            "enabled":True
        }
    elif frequency == "hourly":
        payload = {
            "interval":"hourly",
            "hour":None, # This is in UTC
            "minute":"00",
            "command":"/home/" + bot.pythonanywhere_username + "/.virtualenvs/mysite-virtualenv/bin/python " + bot.path + "health_check.py " + room_id,
            "enabled":True
        }
    else:
        return "Invalid frequency: " + frequency
    api_response = requests.post(
        'https://www.pythonanywhere.com/api/v0/user/' + bot.pythonanywhere_username + '/schedule/',
        data=payload,
        headers=headers
    )
    if api_response.status_code == 201:
        return "Merakisight " + frequency + " monitoring has started."
    else:
        return "An error occurred while starting Merakisight monitoring."


# Start the Merakisight monitoring
def start_monitoring(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    frequency = None
    room_id = incoming_msg.roomId
    if room_id in bot.frequency:
        frequency = bot.frequency[room_id]
    else:
        frequency = "daily"
        bot.frequency[room_id] = frequency
    response = add_scheduled_task(room_id, frequency)
    return response


# A simple command that returns a basic string that will be sent as a reply
def check_existing_monitoring(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    room_id = incoming_msg.roomId
    headers = {'Authorization': 'Token ' + bot.pythonanywhere_token}
    api_response = requests.get(
        'https://www.pythonanywhere.com/api/v0/user/' + bot.pythonanywhere_username + '/schedule/',
        headers=headers
    )
    existing_tasks = [task['id'] for task in api_response.json() if room_id in task['command']]
    if len(existing_tasks) > 0:
        return (True, existing_tasks)
    else:
        return (False, None)


# A simple command that returns a basic string that will be sent as a reply
def stop_monitoring(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    headers = {'Authorization': 'Token ' + bot.pythonanywhere_token}
    monitoring_exists, existing_tasks = check_existing_monitoring(incoming_msg)
    response = None
    if monitoring_exists:
        for task_id in existing_tasks:
                task_delete_url = 'https://www.pythonanywhere.com/api/v0/user/' + bot.pythonanywhere_username + '/schedule/' + str(task_id)
                api_response_2 = requests.delete(task_delete_url, headers=headers)
        return "Monitoring has been stopped."
    else:
        return "There was no monitoring to stop at this time." 


# Change the Merakisight monitoring
def change_monitoring_frequency(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    user_frequency = bot.extract_message("/changefrequency", incoming_msg.text).strip()
    room_id = incoming_msg.roomId
    if user_frequency == "daily" or user_frequency == "hourly":
        if room_id in bot.frequency:
            if user_frequency == bot.frequency[room_id]:
                return "Merakisight is already configured to monitor " + user_frequency
        bot.frequency[room_id] = user_frequency
        # Check for existing monitoring and stop-->start with new frequency
        # Do nothing if not started
        monitoring_exists, existing_tasks = check_existing_monitoring(incoming_msg)
        if monitoring_exists:
            stop_monitoring(incoming_msg)
            start_monitoring(incoming_msg)
        return "Merakisight has been set to monitor " + user_frequency
    else:
        return "Invalid frequency: '" + user_frequency + "'. Please say **/changefrequency daily** or **/changefrequency hourly**"


def run_health_check(incoming_msg):
    do_health_check(incoming_msg.roomId)


def run_demo_health_check(incoming_msg):
    demo_health_check(incoming_msg.roomId)


# Retrieve required details from environment variables
bot_email = os.getenv("TEAMS_BOT_EMAIL")
teams_token = os.getenv("TEAMS_BOT_TOKEN")
bot_url = os.getenv("TEAMS_BOT_URL")
bot_app_name = os.getenv("TEAMS_BOT_APP_NAME")

# Create a Bot Object
#   Note: debug mode prints out more details about processing to terminal
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True,
)

# Setup API required info
bot.intersight_base_url = 'https://www.intersight.com/api/v1/'
bot.pythonanywhere_username = os.getenv("PYTHONANYWHERE_USER")
bot.pythonanywhere_token = os.getenv("PYTHONANYWHERE_API_KEY")
bot.path = os.getenv("MERAKISIGHT_PATH")
bot.secret_file = os.path.join(bot.path, "SecretKey.txt")
bot.intersight_api_key = os.getenv("INTERSIGHT_API_KEY")
bot.meraki_api_key = os.getenv("MERAKI_API_KEY")
bot.INTERSIGHT_AUTH = IntersightAuth(
    secret_key_filename=bot.secret_file,
    api_key_id=bot.intersight_api_key
)

bot.frequency = {}
bot.prev_percents = {}

# Set the bot greeting.
bot.set_greeting(greeting)

# Add new commands to the box.
bot.add_command("/changefrequency", "Set the frequency (**hourly** or **daily**) for Merakisight reporting", change_monitoring_frequency)
bot.add_command("/startmonitoring", "Tell Merakisight to start monitoring at the configured interval", start_monitoring)
bot.add_command("/stopmonitoring", "Tell Merakisight to stop monitoring", stop_monitoring)
bot.add_command("/healthcheck", "Run a health check right now", run_demo_health_check)

# Every bot includes a default "/echo" command.  You can remove it, or any
# other command with the remove_command(command) method.
bot.remove_command("/echo")


if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=5000)