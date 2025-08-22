# update_loop.py
import json
import logging
import os
import time
from datetime import datetime, timezone

from archive import archive_all_urls
from config import CSV_FILENAME, HTML_FILENAME, XLSX_FILENAME
from diff import detect_changes, read_csv_to_dict
from downloader import download_xlsx, download_zip_and_extract_html
from notify import send_discord_message
from parser import generate_csv
from utils import hash_file

logger = logging.getLogger(__name__)

last_html_hash = None
last_csv_data = {}
INFO_PATH = os.path.join("info", "status.json")
UPDATE_INTERVAL_SECONDS = 600


def write_info(html_hash: str, csv_hash: str, xlsx_hash: str, is_archived: bool):
    os.makedirs("info", exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat()

    try:
        with open(INFO_PATH, "r") as f:
            info = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        info = {"files": {HTML_FILENAME: {}}}

    info["last_updated"] = now_iso
    info["files"][HTML_FILENAME]["hash"] = html_hash
    if is_archived:
        info["files"][HTML_FILENAME]["last_archived"] = now_iso

    info["files"][CSV_FILENAME] = {"hash": csv_hash}
    info["files"][XLSX_FILENAME] = {"hash": xlsx_hash}

    with open(INFO_PATH, "w") as f:
        json.dump(info, f, indent=2)


def update_loop():
    global last_html_hash, last_csv_data

    while True:
        logger.info("--- Starting update cycle ---")
        try:
            download_zip_and_extract_html()
            download_xlsx()
            generate_csv()

            if not all(
                os.path.exists(f) for f in [HTML_FILENAME, CSV_FILENAME, XLSX_FILENAME]
            ):
                logger.warning(
                    "One or more files are missing after download/parse. Skipping this cycle."
                )
                time.sleep(UPDATE_INTERVAL_SECONDS)
                continue

            html_hash = hash_file(HTML_FILENAME)
            csv_hash = hash_file(CSV_FILENAME)
            xlsx_hash = hash_file(XLSX_FILENAME)
            current_csv_data = read_csv_to_dict(CSV_FILENAME)

            archived_this_cycle = False
            if last_html_hash is None:
                logger.info("First run: storing initial file hashes.")
            elif html_hash != last_html_hash:
                logger.info("🔔 Artists.html has changed! Checking for data differences.")
                changes = detect_changes(last_csv_data, current_csv_data)
                if changes:
                    message = "**Tracker Update Detected:**\n" + "\n".join(changes)
                    send_discord_message(message)
                    archive_all_urls()
                    archived_this_cycle = True
                else:
                    logger.info("ℹ️ HTML hash changed, but no data differences found.")
            else:
                logger.info("ℹ️ Artists.html is unchanged.")

            write_info(html_hash, csv_hash, xlsx_hash, is_archived=archived_this_cycle)
            last_html_hash = html_hash
            last_csv_data = current_csv_data
            logger.info("--- Update cycle finished ---")

        except Exception as e:
            logger.critical(
                f"An unexpected error occurred in the update loop: {e}", exc_info=True
            )

        logger.info(f"Sleeping for {UPDATE_INTERVAL_SECONDS} seconds...")
        time.sleep(UPDATE_INTERVAL_SECONDS)