# downloader.py
import logging
import zipfile

import requests

from config import HTML_FILENAME, XLSX_FILENAME, XLSX_URL, ZIP_FILENAME, ZIP_URL

logger = logging.getLogger(__name__)


def _download_file(url: str, filename: str, timeout: int = 30) -> bool:
    logger.info(f"🔄 Downloading {filename}...")
    try:
        with requests.get(url, timeout=timeout) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                f.write(r.content)
        logger.info(f"✅ Saved {filename}")
        return True
    except requests.RequestException as e:
        logger.error(f"❌ Failed to download {filename}: {e}")
        return False


def download_zip_and_extract_html():
    if not _download_file(ZIP_URL, ZIP_FILENAME):
        return

    logger.info(f"📦 Extracting {HTML_FILENAME} from {ZIP_FILENAME}...")
    try:
        with zipfile.ZipFile(ZIP_FILENAME, "r") as z:
            html_content = z.read(HTML_FILENAME)
        with open(HTML_FILENAME, "wb") as f:
            f.write(html_content)
        logger.info(f"✅ Extracted {HTML_FILENAME}")
    except (zipfile.BadZipFile, KeyError, FileNotFoundError) as e:
        logger.error(f"❌ Failed to extract {HTML_FILENAME}: {e}")


def download_xlsx():
    _download_file(XLSX_URL, XLSX_FILENAME)