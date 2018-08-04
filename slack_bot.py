# Slack bot 1
# Function: Starterbot

import os
import time
import datetime
import re
import requests
from slackclient import SlackClient


slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
starterbot_id = None

# RTM read delay
RTM_read_delay = 1
example_command = "do"
Mention_regex = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """

    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """

    matches = re.search(Mention_regex, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else None


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """

    # Default command to help user
    default_response = "Not sure what you mean. Try *{}*.".format(example_command)
    response = None

    # This is where you implement commands!
    if command.startswith(example_command):
        response = "Sure...Write some more code then I can do that!"
    if command == "time": response = datetime.datetime.now()
    if command == "who are you?": response = "I'm Harsh's first bot!"
    if command == "weather":
        weather_api_key = os.environ.get("WEATHER_API_KEY")
        url = "http://api.openweathermap.org/data/2.5/weather?q=pittsburgh&units=imperial&APPID=" + weather_api_key
        reply = requests.post(url)
        response = reply.json()["main"]["temp"]

    # Sends response back to channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        starterbot_id = slack_client.api_call('auth.test')["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                    handle_command(command,channel)
                    time.sleep(RTM_read_delay)
    else:
        print("Connection Failed. Exception traceback printed above.")

# END