import csv

def read_csv_to_dict(filename):
    d = {}
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            d[row["Artist Name"]] = row
    return d

def detect_changes(old_data, new_data):
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

        if old_row["URL"] != new_row["URL"]:
            changes.append(f"🔗 Link changed for **{artist}**")
        if old_row["Credit"] != new_row["Credit"]:
            changes.append(f"✏️ Credit changed for **{artist}**")
        if old_row["Links Work"] != new_row["Links Work"]:
            changes.append(f"🔄 Links Work status changed for **{artist}**")
        if old_row["Updated"] != new_row["Updated"]:
            changes.append(f"🕒 Updated date changed for **{artist}**")
        if old_row["Best"] != new_row["Best"]:
            changes.append(f"⭐ Best flag changed for **{artist}**")

    return changes
