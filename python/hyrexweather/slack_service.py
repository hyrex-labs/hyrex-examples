import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the webhook URL from environment
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def post_to_slack():
    pass

def send_weather_notification(alerts):
    """Send weather alerts to Slack"""
    if not alerts:
        return
    
    # Format the message
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🌦️ San Francisco Weather Alert 🌦️"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Weather update as of {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
            }
        }
    ]
    
    for alert in alerts:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{alert['period']}*: {alert['forecast']}"
            }
        })
    
    message = {
        "blocks": blocks
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        response.raise_for_status()
        print("✓ Weather notification sent to Slack successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"× Error sending to Slack: {e}")
        return False