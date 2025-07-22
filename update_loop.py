import time

from downloader import download_zip_and_extract_html, download_xlsx
from parser import generate_csv
from diff import read_csv_to_dict, detect_changes
from archive import archive_all_urls
from notify import send_discord_message
from utils import hash_file

last_csv_hash = None
last_csv_data = {}

def update_loop():
    global last_csv_hash, last_csv_data

    while True:
        try:
            download_zip_and_extract_html()
            download_xlsx()
            generate_csv()

            current_hash = hash_file("artists.csv")
            current_data = read_csv_to_dict("artists.csv")

            if last_csv_hash is None:
                print("ℹ️ Initial CSV hash stored.")
            elif current_hash != last_csv_hash:
                print("🔔 CSV has changed! Archiving URLs...")

                changes = detect_changes(last_csv_data, current_data)
                if changes:
                    message = "**CSV Update Detected:**\n" + "\n".join(changes)
                    send_discord_message(message)
                else:
                    print("ℹ️ No detectable content changes found.")

                archive_all_urls()
            else:
                print("ℹ️ CSV unchanged. No archiving needed.")

            last_csv_hash = current_hash
            last_csv_data = current_data

        except Exception as e:
            print(f"⚠️ Error updating files: {e}")

        time.sleep(600)
