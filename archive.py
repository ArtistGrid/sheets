import requests, time, random

from config import ARCHIVE_URLS, USER_AGENT

def archive_url(url):
    print(f"🌐 Archiving {url} ...")
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(f"https://web.archive.org/save/{url}", headers=headers, timeout=30)
        if resp.status_code == 200:
            print(f"✅ Archived {url}")
        else:
            print(f"⚠️ Failed to archive {url}, status code {resp.status_code}")
    except Exception as e:
        print(f"⚠️ Exception archiving {url}: {e}")

def archive_all_urls():
    for url in ARCHIVE_URLS:
        delay = 10 + random.uniform(-3, 3)
        time.sleep(delay)
        archive_url(url)
