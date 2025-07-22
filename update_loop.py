import json
import os
import time
from datetime import datetime

from downloader import download_zip_and_extract_html, download_xlsx
from parser import generate_csv
from diff import read_csv_to_dict, detect_changes
from archive import archive_all_urls
from notify import send_discord_message
from utils import hash_file

last_html_hash = None
last_csv_data = {}
INFO_PATH = "info/status.json"

def write_info(html_hash, csv_hash, xlsx_hash):
    os.makedirs("info", exist_ok=True)
    info = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "files": {
            "Artists.html": {
                "hash": html_hash,
                "last_archived": datetime.utcnow().isoformat() + "Z"
            },
            "artists.csv": {
                "hash": csv_hash
            },
            "artists.xlsx": {
                "hash": xlsx_hash
            }
        }
    }
    with open(INFO_PATH, "w") as f:
        json.dump(info, f, indent=2)

def update_loop():
    global last_html_hash, last_csv_data

    while True:
        try:
            download_zip_and_extract_html()
            download_xlsx()
            generate_csv()

            html_hash = hash_file("Artists.html")
            csv_hash = hash_file("artists.csv")
            xlsx_hash = hash_file("artists.xlsx")

            current_data = read_csv_to_dict("artists.csv")

            if last_html_hash is None:
                print("ℹ️ Initial HTML hash stored.")
            elif html_hash != last_html_hash:
                print("🔔 Artists.html has changed! Archiving URLs...")

                changes = detect_changes(last_csv_data, current_data)
                if changes:
                    message = "**CSV Update Detected:**\n" + "\n".join(changes)
                    send_discord_message(message)
                else:
                    print("ℹ️ No detectable content changes found in CSV.")

                archive_all_urls()
            else:
                print("ℹ️ Artists.html unchanged. No archiving needed.")

            write_info(html_hash, csv_hash, xlsx_hash)

            last_html_hash = html_hash
            last_csv_data = current_data

        except Exception as e:
            print(f"⚠️ Error updating files: {e}")

        time.sleep(600)
