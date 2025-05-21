import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from project root
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(message: str, blocks: list = None):
    """
    Sends a Slack message using the configured webhook URL.

    Args:
        message (str): The plain-text fallback message.
        blocks (list): Optional Slack block structure for rich formatting.
    """
    if not SLACK_WEBHOOK:
        print("[ERROR] Slack webhook not configured.")
        return

    payload = {
        "text": message,
        "blocks": blocks or [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("[INFO] Alert sent to Slack.")
        else:
            print(f"[ERROR] Slack error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Failed to send Slack alert: {e}")