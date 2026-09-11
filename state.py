import json
import os

PROCESSED_FILE = "processed.json"


def load_processed():
    """Read processed.json, returning {} if it doesn't exist."""
    if not os.path.exists(PROCESSED_FILE):
        return {}
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_processed(data):
    """Write data back to processed.json as pretty-printed JSON."""
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
