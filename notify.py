# notify.py
import json
import logging

import requests

from config import DISCORD_WEBHOOK_URL

logger = logging.getLogger(__name__)


def send_discord_message(content: str):
    if not DISCORD_WEBHOOK_URL:
        logger.warning("Discord webhook URL not set. Skipping notification.")
        return

    if len(content) > 2000:
        content = content[:1990] + "\n... (truncated)"

    headers = {"Content-Type": "application/json"}
    data = {"content": content}

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL, headers=headers, data=json.dumps(data), timeout=10
        )
        response.raise_for_status()
        logger.info("✅ Discord notification sent successfully.")
    except requests.RequestException as e:
        logger.error(f"⚠️ Exception sending Discord notification: {e}")