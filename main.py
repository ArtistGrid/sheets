import requests
import zipfile
import threading
import time
import random
import hashlib
from bs4 import BeautifulSoup
import csv
import re
from flask import Flask, send_file, send_from_directory, abort
import os
import json
app = Flask(__name__)

ZIP_URL = "https://docs.google.com/spreadsheets/d/1S6WwM05O277npQbaiNk-jZlXK3TdooSyWtqaWUvAI78/export?format=zip"
XLSX_URL = "https://docs.google.com/spreadsheets/d/1S6WwM05O277npQbaiNk-jZlXK3TdooSyWtqaWUvAI78/export?format=xlsx"

ZIP_FILENAME = "Trackerhub.zip"
HTML_FILENAME = "Artists.html"
CSV_FILENAME = "artists.csv"
XLSX_FILENAME = "artists.xlsx"

exclude_names = {
    "AI Models",
    "Lawson",
    "BPM Tracker",
    "Worst Comps & Edits",
    "Allegations",
    "Rap Disses Timeline",
    "Underground Artists",
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"

# URLs to archive on changes — update these to your actual hosted domain
BASE_URL = "http://localhost:5000"  # Change this to your public domain when deployed

ARCHIVE_URLS = [
    f"{BASE_URL}/",
    f"{BASE_URL}/index.html/",
    f"{BASE_URL}/artists.html",
    f"{BASE_URL}/artists.csv",
    f"{BASE_URL}/artists.xlsx",
]

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def clean_artist_name(text):
    return re.sub(r'[⭐🤖🎭\u2B50\uFE0F]', '', text).strip()

def force_star_flag(starred=True):
    return "Yes" if starred else "No"

def download_zip_and_extract_html():
    print("🔄 Downloading ZIP...")
    r = requests.get(ZIP_URL)
    r.raise_for_status()
    with open(ZIP_FILENAME, "wb") as f:
        f.write(r.content)
    print(f"✅ Saved ZIP as {ZIP_FILENAME}")

    with zipfile.ZipFile(ZIP_FILENAME, "r") as z:
        with z.open(HTML_FILENAME) as html_file:
            html_content = html_file.read()
            with open(HTML_FILENAME, "wb") as f:
                f.write(html_content)
    print(f"✅ Extracted {HTML_FILENAME}")

def download_xlsx():
    print("🔄 Downloading XLSX...")
    r = requests.get(XLSX_URL)
    r.raise_for_status()
    with open(XLSX_FILENAME, "wb") as f:
        f.write(r.content)
    print(f"✅ Saved XLSX as {XLSX_FILENAME}")

def generate_csv():
    print("📝 Generating CSV...")
    with open(HTML_FILENAME, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    rows = soup.select("table.waffle tbody tr")[3:]  # skip headers and Discord

    data = []
    starring = True

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue

        link_tag = cells[0].find("a")
        artist_name_raw = link_tag.get_text(strip=True) if link_tag else cells[0].get_text(strip=True)
        artist_url = link_tag["href"] if link_tag else ""
        if not artist_url:
            continue

        if "AI Models" in artist_name_raw:
            starring = False

        artist_name_clean = clean_artist_name(artist_name_raw)
        if artist_name_clean in exclude_names:
            continue

        if "🚩" in artist_name_raw:
            continue

        best = force_star_flag(starring)
        credit = cells[1].get_text(strip=True)
        updated = cells[2].get_text(strip=True)
        links_work = cells[3].get_text(strip=True)

        data.append([artist_name_clean, artist_url, credit, links_work, updated, best])

    with open(CSV_FILENAME, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Artist Name", "URL", "Credit", "Links Work", "Updated", "Best"])
        writer.writerows(data)

    print(f"✅ CSV saved as {CSV_FILENAME}")

def hash_file(filename):
    hasher = hashlib.sha256()
    with open(filename, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def archive_url(url):
    print(f"🌐 Archiving {url} ...")
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(f"https://web.archive.org/save/{url}", headers=headers, timeout=30)
        if resp.status_code == 200:
            print(f"✅ Archived {url}")
        else:
            print(f"⚠️ Failed to archive {url}, status code {resp.status_code}")
    except Exception as e:
        print(f"⚠️ Exception archiving {url}: {e}")

def archive_all_urls():
    for url in ARCHIVE_URLS:
        delay = 10 + random.uniform(-3, 3)
        time.sleep(delay)
        archive_url(url)

def read_csv_to_dict(filename):
    """Read CSV into dict with artist_name as key, storing relevant fields."""
    d = {}
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            d[row["Artist Name"]] = row
    return d

def detect_changes(old_data, new_data):
    """
    Compare old and new data dictionaries.
    Returns a list of strings describing changes.
    """
    changes = []

    old_keys = set(old_data.keys())
    new_keys = set(new_data.keys())

    removed = old_keys - new_keys
    added = new_keys - old_keys
    common = old_keys & new_keys

    for artist in removed:
        changes.append(f"❌ Removed: **{artist}**")

    for artist in added:
        changes.append(f"➕ Added: **{artist}**")

    for artist in common:
        old_row = old_data[artist]
        new_row = new_data[artist]
        # Check if URL changed
        if old_row["URL"] != new_row["URL"]:
            changes.append(f"🔗 Link changed for **{artist}**")
        # Check other fields if needed (Credit, Updated, etc.)
        if old_row["Credit"] != new_row["Credit"]:
            changes.append(f"✏️ Credit changed for **{artist}**")
        if old_row["Links Work"] != new_row["Links Work"]:
            changes.append(f"🔄 Links Work status changed for **{artist}**")
        if old_row["Updated"] != new_row["Updated"]:
            changes.append(f"🕒 Updated date changed for **{artist}**")
        if old_row["Best"] != new_row["Best"]:
            changes.append(f"⭐ Best flag changed for **{artist}**")

    return changes

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

def update_loop():
    last_csv_hash = None
    last_csv_data = {}

    while True:
        try:
            download_zip_and_extract_html()
            download_xlsx()
            generate_csv()

            current_hash = hash_file(CSV_FILENAME)
            current_data = read_csv_to_dict(CSV_FILENAME)

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

        time.sleep(600)  # 10 minutes

@app.route("/artists.html")
def serve_artists_html():
    return send_file(HTML_FILENAME, mimetype="text/html")

@app.route("/artists.csv")
def serve_artists_csv():
    return send_file(CSV_FILENAME, mimetype="text/csv")

@app.route("/artists.xlsx")
def serve_artists_xlsx():
    return send_file(XLSX_FILENAME, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Serve index.html at "/", "/index", and "/index.html"
@app.route("/")
@app.route("/index")
@app.route("/index.html")
def serve_index():
    return send_file("templates/index.html", mimetype="text/html")

# Serve static files from templates/_next/ as /_next/...
@app.route("/_next/<path:filename>")
def serve_next_static(filename):
    return send_from_directory("templates/_next", filename)

# Custom 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return send_file("templates/404.html", mimetype="text/html"), 404

if __name__ == "__main__":
    threading.Thread(target=update_loop, daemon=True).start()
    try:
        download_zip_and_extract_html()
        download_xlsx()
        generate_csv()
    except Exception as e:
        print(f"⚠️ Initial update failed: {e}")

    app.run(host="0.0.0.0", port=5000)
