import os

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

BASE_URL = "http://localhost:5000"

ARCHIVE_URLS = [
    f"{BASE_URL}/",
    f"{BASE_URL}/index.html/",
    f"{BASE_URL}/artists.html",
    f"{BASE_URL}/artists.csv",
    f"{BASE_URL}/artists.xlsx",
]

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
