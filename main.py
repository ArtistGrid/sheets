import os
import threading
import time
import requests
import zipfile
import csv
from bs4 import BeautifulSoup
from flask import Flask, send_file, render_template

app = Flask(__name__, template_folder="templates")

# Constants
ZIP_URL = "https://docs.google.com/spreadsheets/d/1zoOIaNbBvfuL3sS3824acpqGxOdSZSIHM8-nI9C-Vfc/export?format=zip"
ZIP_FILE = "sheet.zip"
EXTRACT_FOLDER = "sheet"
HTML_FILE = os.path.join(EXTRACT_FOLDER, "Artists.html")
CSV_FILE = "artists.csv"

def fetch_and_process():
    try:
        print("[*] Downloading ZIP...")
        r = requests.get(ZIP_URL)
        with open(ZIP_FILE, "wb") as f:
            f.write(r.content)

        print("[*] Extracting ZIP...")
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_FOLDER)

        print("[*] Parsing HTML...")
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        table = soup.find("table", class_="waffle")
        if not table:
            print("[!] Table not found.")
            return

        rows = table.find_all("tr")[4:]  # Skip first 4 rows

        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            artist_cell = cols[0]
            a_tag = artist_cell.find("a")
            artist_name = a_tag.text.strip() if a_tag else artist_cell.text.strip()
            artist_url = a_tag['href'] if a_tag and a_tag.has_attr('href') else ""
            credits = cols[1].get_text(strip=True)
            updated = cols[2].get_text(strip=True)
            links_work = cols[3].get_text(strip=True)

            data.append([artist_name, artist_url, credits, updated, links_work])

        print(f"[*] Writing {len(data)} rows to CSV...")
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["artist name", "URL", "credits", "updated", "links work"])
            writer.writerows(data)

        print("[✓] Done! CSV updated.")

    except Exception as e:
        print(f"[!] Error: {e}")

def background_updater():
    while True:
        fetch_and_process()
        time.sleep(600)  # 10 minutes

# Routes
@app.route("/")
@app.route("/index")
@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/artists.csv")
def serve_csv():
    if os.path.exists(CSV_FILE):
        return send_file(CSV_FILE, mimetype="text/csv", as_attachment=False)
    return "CSV not ready yet.", 503

@app.route("/<path:path>")
def catch_all(path):
    if os.path.exists(CSV_FILE):
        return send_file(CSV_FILE, mimetype="text/csv", as_attachment=False)
    return "CSV not ready yet.", 503

if __name__ == "__main__":
    # Start background thread
    thread = threading.Thread(target=background_updater, daemon=True)
    thread.start()

    # Start Flask app
    app.run(host="0.0.0.0", port=5000)
