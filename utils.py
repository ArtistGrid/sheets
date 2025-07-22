import re, hashlib

def clean_artist_name(text):
    return re.sub(r'[⭐🤖🎭\u2B50\uFE0F]', '', text).strip()

def force_star_flag(starred=True):
    return "Yes" if starred else "No"

def hash_file(filename):
    hasher = hashlib.sha256()
    with open(filename, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()
