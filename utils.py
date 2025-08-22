# utils.py
import hashlib
import re


def clean_artist_name(text: str) -> str:
    return re.sub(r"[⭐🤖🎭\u2B50\uFE0F]", "", text).strip()


def force_star_flag(starred: bool = True) -> str:
    return "Yes" if starred else "No"


def hash_file(filename: str, block_size: int = 65536) -> str:
    hasher = hashlib.sha256()
    try:
        with open(filename, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                hasher.update(block)
    except FileNotFoundError:
        return "file_not_found"
    return hasher.hexdigest()