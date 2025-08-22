# parser.py
import csv
import logging

from bs4 import BeautifulSoup

from config import CSV_FILENAME, HTML_FILENAME, exclude_names
from utils import clean_artist_name, force_star_flag

logger = logging.getLogger(__name__)


def generate_csv():
    logger.info(f"📝 Generating {CSV_FILENAME} from {HTML_FILENAME}...")
    try:
        with open(HTML_FILENAME, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except FileNotFoundError:
        logger.error(f"❌ {HTML_FILENAME} not found. Cannot generate CSV.")
        return

    table_body = soup.select_one("table.waffle tbody")
    if not table_body:
        logger.error("❌ Could not find the table body in HTML. Cannot generate CSV.")
        return

    rows = table_body.select("tr")
    data = []
    starring_section = True

    for row in rows[3:]:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue

        artist_name_raw = cells[0].get_text(strip=True)
        link_tag = cells[0].find("a")
        artist_url = link_tag.get("href") if link_tag else ""

        if not artist_name_raw or not artist_url:
            continue

        if "AI Models" in artist_name_raw:
            starring_section = False

        artist_name_clean = clean_artist_name(artist_name_raw)
        if artist_name_clean in exclude_names or "🚩" in artist_name_raw:
            continue

        data.append(
            [
                artist_name_clean,
                artist_url,
                cells[1].get_text(strip=True),
                cells[3].get_text(strip=True),
                cells[2].get_text(strip=True),
                force_star_flag(starring_section),
            ]
        )

    try:
        with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            writer.writerow(
                ["Artist Name", "URL", "Credit", "Links Work", "Updated", "Best"]
            )
            writer.writerows(data)
        logger.info(f"✅ Generated {CSV_FILENAME} with {len(data)} rows.")
    except IOError as e:
        logger.error(f"❌ Failed to write CSV file {CSV_FILENAME}: {e}")