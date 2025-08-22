# archive.py
import logging
import random
import time
from typing import List

from waybackpy import WaybackMachineSaveAPI

from config import ARCHIVE_URLS, USER_AGENT

logger = logging.getLogger(__name__)


def archive_url(url: str):
    logger.info(f"🌐 Archiving {url} ...")
    try:
        save_api = WaybackMachineSaveAPI(url, user_agent=USER_AGENT)
        save_api.save()
        logger.info(f"✅ Archived {url}")
    except Exception as e:
        logger.error(f"⚠️ Exception archiving {url}: {e}", exc_info=True)


def archive_all_urls():
    logger.info("--- Starting archival process for all URLs ---")
    for url in ARCHIVE_URLS:
        delay = 10 + random.uniform(-3, 3)
        logger.info(f"Waiting {delay:.2f} seconds before next archive...")
        time.sleep(delay)
        archive_url(url)
    logger.info("--- Archival process finished ---")


def test_archive():
    test_url = "https://httpbin.org/anything/foo/bar"
    archive_url(test_url)