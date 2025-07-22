import requests, zipfile

from config import ZIP_URL, ZIP_FILENAME, HTML_FILENAME, XLSX_URL, XLSX_FILENAME

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
