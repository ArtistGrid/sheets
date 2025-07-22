import requests, zipfile

from config import ZIP_URL, ZIP_FILENAME, HTML_FILENAME, XLSX_URL, XLSX_FILENAME

def download_zip_and_extract_html():
    print("🔄 Downloading ZIP...")
    try:
        with requests.get(ZIP_URL, timeout=30) as r:
            r.raise_for_status()
            with open(ZIP_FILENAME, "wb") as f:
                f.write(r.content)
        print(f"✅ Saved ZIP as {ZIP_FILENAME}")
    except requests.RequestException as e:
        print(f"❌ Failed to download ZIP: {e}")
        return

    try:
        with zipfile.ZipFile(ZIP_FILENAME, "r") as z:
            with z.open(HTML_FILENAME) as html_file:
                html_content = html_file.read()
            with open(HTML_FILENAME, "wb") as f:
                f.write(html_content)
        print(f"✅ Extracted {HTML_FILENAME}")
    except (zipfile.BadZipFile, KeyError) as e:
        print(f"❌ Failed to extract {HTML_FILENAME}: {e}")

def download_xlsx():
    print("🔄 Downloading XLSX...")
    try:
        with requests.get(XLSX_URL, timeout=30) as r:
            r.raise_for_status()
            with open(XLSX_FILENAME, "wb") as f:
                f.write(r.content)
        print(f"✅ Saved XLSX as {XLSX_FILENAME}")
    except requests.RequestException as e:
        print(f"❌ Failed to download XLSX: {e}")
