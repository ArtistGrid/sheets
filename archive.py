import logging
from waybackpy import WaybackMachineSaveAPI
import time
import random

from config import ARCHIVE_URLS, USER_AGENT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def archive_url(url):
    logger.info(f"🌐 Archiving {url} ...")
    try:
        save_api = WaybackMachineSaveAPI(url, user_agent=USER_AGENT)
        save_api.save()
        logger.info(f"✅ Archived {url}")
    except Exception as e:
        logger.error(f"⚠️ Exception archiving {url}: {e}")

def archive_all_urls():
    for url in ARCHIVE_URLS:
        delay = 10 + random.uniform(-3, 3)
        time.sleep(delay)
        archive_url(url)

def test_archive():
    test_url = "https://httpbin.org/anything/foo/bar"
    archive_url(test_url)
