import os

SHEET_URL = "https://docs.google.com/spreadsheets/d/1S6WwM05O277npQbaiNk-jZlXK3TdooSyWtqaWUvAI78"
ZIP_URL = SHEET_URL + "/export?format=zip"
XLSX_URL = SHEET_URL + "/export?format=xlsx"


ZIP_FILENAME = "Trackerhub.zip"
HTML_FILENAME = "Artists.html"
CSV_FILENAME = "artists.csv"
XLSX_FILENAME = "artists.xlsx"

exclude_names = {
    "AI Models",
    "🎹 BPM & Key Tracker",
    "🎹 Worst Comps & Edits",
    "Allegations",
    "Rap Disses Timeline",
    "Underground Artists",
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"

BASE_URL = "https://sheets.artistgrid.cx"

ARCHIVE_URLS = [
    f"{BASE_URL}/",
    f"{BASE_URL}/artists.html",
    f"{BASE_URL}/artists.csv",
    f"{BASE_URL}/artists.xlsx",
    f"https://artistgrid.cx",
]

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
