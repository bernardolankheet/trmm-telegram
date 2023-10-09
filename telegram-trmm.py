import requests
import os
import json
import time
import datetime
import logging
import configparser
from logging.handlers import RotatingFileHandler

config = configparser.ConfigParser()
config.read('/opt/trmm-telegram/configScrips.ini')

# Global variables, stored in the configuration file
sent_alerts_file = config.get('Config', 'sent_alerts_file')
url = config['TacticalRMM']['url']
print(f'URL: {url}')
alert_api_key = config['TacticalRMM']['alert_api_key']
print(f'KEY: {alert_api_key}')
updateinterval = int(config.get('Config', 'updateinterval'))
max_alerts = int(config.get('Config', 'max_alerts'))
bot_token = config['Telegram']['bot_token']
user_group_telegram = config['Telegram']['user_group_telegram']
log_dir = '/var/log/trmm-telegram'

# Set the path to the sent alert ID file
sent_alerts_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sent_alerts.json')

# Config Log
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, 'trmm-telegram.log')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=5)  # Logrotate
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for Tactical API header
headersalerts = {"Content-Type": "application/json", "X-API-KEY": alert_api_key}  # Token de acesso à API do domínio

# Creates a reusable HTTP session with connection pooling
http_session = requests.Session()

# Checking Alerts
def alertas():
    """
    Function that checks for new alerts and sends them via message on Telegram
    """
    # Defines the request body as a JSON object, being filtered for resolved, silenced alerts, and error, warning and info severities.
    data = {
        "resolvedFilter": True,
        "snoozedFilter": True,
        "timeFilter": 1,
        "severityFilter": ["error", "warning", "info"]
    }

    # Makes PATCH request to Tactical API using the HTTP session
    response = http_session.patch('https://' + 'api.' + url + '/alerts/', headers=headersalerts, json=data)

    # Checks whether the response was successful
    if response.status_code == 200:
        data = response.json()
        alerts = []

        # Reads the sent_alerts.json file
        if os.path.exists(sent_alerts_file) and os.path.getsize(sent_alerts_file) > 0:
            with open(sent_alerts_file, 'r') as f:
                sent_alerts = json.load(f)
        else:
            sent_alerts = {'sent': [], 'resolved': []}

        # Remove IDs excedentes
        if len(sent_alerts['sent']) > max_alerts:
            sent_alerts['sent'] = sent_alerts['sent'][-max_alerts:]
            logger.info("Old IDs Sent Successfully Cleared!")
        if len(sent_alerts['resolved']) > max_alerts:
            sent_alerts['resolved'] = sent_alerts['resolved'][-max_alerts:]
            logger.info("Old IDs Sent Successfully Cleared!")

        # Save and update the file sent_alerts_file
        with open(sent_alerts_file, 'w') as f:
            json.dump(sent_alerts, f, indent=2)

        for alert in data:
            resolved = alert['resolved']
            alert_id = alert['id']
            if not resolved and alert_id not in sent_alerts['sent']:
                if alert["alert_type"] == "check":
                    alert_str = f"Client: {alert['client']} - Site: {alert['site']}\n{alert['message']}\nStarted in: {datetime.datetime.strptime(alert['alert_time'], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(datetime.timezone(datetime.timedelta(hours=-3))).strftime('%d-%m-%Y as %H:%M:%S')}\n"
                    alerts.append(alert_str)
                    sent_alerts['sent'].append(alert_id)
                    try:
                        logger.info("New alert successfully sent!")
                    except Exception as e:
                        logger.error("Error sending new alert: %s", str(e))
            elif resolved and alert_id in sent_alerts['sent'] and alert_id not in sent_alerts['resolved']:
                alert_str = f"Cliente: {alert['client']} - Site: {alert['site']}\n{alert['message']} \nAlert resolved on: {datetime.datetime.strptime(alert['resolved_on'], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(datetime.timezone(datetime.timedelta(hours=-3))).strftime('%d-%m-%Y as %H:%M:%S')}\n"
                alerts.append(alert_str)
                sent_alerts['resolved'].append(alert_id)
                try:
                    logger.info("Recovery message sent successfully!")
                except Exception as e:
                    logger.error("Error sending recovery message: %s", str(e))
        if alerts:
            try:
                telegram_send_message("\n".join(alerts))
                logger.info("Alerts sent successfully!")
                # Saves the list of alerts IDs already sent in sent_alerts.json file
                with open(sent_alerts_file, 'w') as f:
                    json.dump(sent_alerts, f)
            except Exception as e:
                logger.error("Error sending alert: %s", str(e))
        else:
            logger.info("No new alerts.")
    else:
        logger.error("Error getting alerts: %s", response.text)

def telegram_send_message(message):
    """
    Send a message to Telegram
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": user_group_telegram, "text": message}
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Error sending message to Telegram: {response.status_code}, {response.text}")

if __name__ == '__main__':
    # Creates the sent alerts file in the same directory as the script, if it does not exist
    if not os.path.exists(sent_alerts_file):
        open(sent_alerts_file, 'w').close()

    # Function to store IDs of alerts already sent
    if os.path.exists(sent_alerts_file) and os.path.getsize(sent_alerts_file) > 0:
        with open(sent_alerts_file, 'r') as f:
            sent_alerts = json.load(f)
    else:
        sent_alerts = []

    # Looping based on the period defined in the updateinterval parameter
    while True:
        alertas()
        time.sleep(updateinterval)