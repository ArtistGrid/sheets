# diff.py
import csv
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def read_csv_to_dict(filename: str) -> Dict[str, Dict[str, str]]:
    data = {}
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "Artist Name" in row and row["Artist Name"]:
                    data[row["Artist Name"]] = row
    except FileNotFoundError:
        logger.warning(f"CSV file not found: {filename}")
    except Exception as e:
        logger.error(f"Error reading CSV file {filename}: {e}", exc_info=True)
    return data


def detect_changes(
    old_data: Dict[str, Dict[str, str]], new_data: Dict[str, Dict[str, str]]
) -> List[str]:
    changes = []

    old_keys = set(old_data.keys())
    new_keys = set(new_data.keys())

    removed = sorted(list(old_keys - new_keys))
    added = sorted(list(new_keys - old_keys))
    common = sorted(list(old_keys & new_keys))

    for artist in removed:
        changes.append(f"❌ Removed: **{artist}**")

    for artist in added:
        changes.append(f"➕ Added: **{artist}**")

    for artist in common:
        old_row = old_data[artist]
        new_row = new_data[artist]

        if old_row.get("URL") != new_row.get("URL"):
            changes.append(f"🔗 Link changed for **{artist}**")
        if old_row.get("Credit") != new_row.get("Credit"):
            changes.append(f"✏️ Credit changed for **{artist}**")
        if old_row.get("Links Work") != new_row.get("Links Work"):
            changes.append(f"🔄 Links Work status changed for **{artist}**")
        if old_row.get("Updated") != new_row.get("Updated"):
            changes.append(f"🕒 Updated date changed for **{artist}**")
        if old_row.get("Best") != new_row.get("Best"):
            changes.append(f"⭐ Best flag changed for **{artist}**")

    return changes