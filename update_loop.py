import time

from downloader import download_zip_and_extract_html, download_xlsx
from parser import generate_csv
from diff import read_csv_to_dict, detect_changes
from archive import archive_all_urls
from notify import send_discord_message
from utils import hash_file

last_html_hash = None
last_csv_data = {}

def update_loop():
    global last_html_hash, last_csv_data

    while True:
        try:
            download_zip_and_extract_html()
            download_xlsx()
            generate_csv()

            # Hash the Artists.html instead of artists.csv
            current_hash = hash_file("Artists.html")
            current_data = read_csv_to_dict("artists.csv")

            if last_html_hash is None:
                print("ℹ️ Initial HTML hash stored.")
            elif current_hash != last_html_hash:
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

            last_html_hash = current_hash
            last_csv_data = current_data

        except Exception as e:
            print(f"⚠️ Error updating files: {e}")

        time.sleep(600)
