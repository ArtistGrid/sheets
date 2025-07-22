from bs4 import BeautifulSoup
import csv

from config import HTML_FILENAME, CSV_FILENAME, exclude_names
from utils import clean_artist_name, force_star_flag

def generate_csv():
    print("📝 Generating CSV...")
    with open(HTML_FILENAME, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    rows = soup.select("table.waffle tbody tr")[3:]

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
        if artist_name_clean in exclude_names or "🚩" in artist_name_raw:
            continue

        best = force_star_flag(starring)
        credit = cells[1].get_text(strip=True)
        updated = cells[2].get_text(strip=True)
        links_work = cells[3].get_text(strip=True)

        data.append([artist_name_clean, artist_url, credit, links_work, updated, best])

    with open(CSV_FILENAME, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(["Artist Name", "URL", "Credit", "Links Work", "Updated", "Best"])
        writer.writerows(data)

    print(f"✅ CSV saved as {CSV_FILENAME}")
