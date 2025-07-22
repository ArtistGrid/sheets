import os, json, requests

from config import DISCORD_WEBHOOK_URL

def send_discord_message(content):
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ Discord webhook URL not set in env")
        return

    headers = {"Content-Type": "application/json"}
    data = {"content": content}

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, headers=headers, data=json.dumps(data), timeout=10)
        if resp.status_code in (200, 204):
            print("✅ Discord notification sent")
        else:
            print(f"⚠️ Failed to send Discord notification, status code {resp.status_code}")
    except Exception as e:
        print(f"⚠️ Exception sending Discord notification: {e}")
