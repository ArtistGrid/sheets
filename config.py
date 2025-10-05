import os

SHEET_URL = "https://docs.google.com/spreadsheets/d/1Z8aANbxXbnUGoZPRvJfWL3gz6jrzPPrwVt3d0c1iJ_4"
ZIP_URL = SHEET_URL + "/export?format=zip"
XLSX_URL = SHEET_URL + "/export?format=xlsx"


ZIP_FILENAME = "Trackerhub.zip"
HTML_FILENAME = "Artists.html"
CSV_FILENAME = "artists.csv"
XLSX_FILENAME = "artists.xlsx"

exclude_names = {
    "🎹Worst Comps & Edits"
    "K4$H K4$$!n0",
    "K4HKn0",
    "AI Models",
    "🎹 BPM & Key Tracker",
    "🎹Comps & Edits"
    "🎹 Worst Comps & Edits",
    "🎹Worst Comps & Edits",
    "🎹 Yedits",
    "🎹Comps & Edits",
    "Allegations",
    "Rap Disses Timeline",
    "Underground Artists",
    "🎹 Comps & Edits",
    "🎹 Worst Comps & Edits"
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
