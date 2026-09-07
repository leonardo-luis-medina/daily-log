import hashlib
import json
import random
import urllib.request
from datetime import datetime, timezone

API_URL = "https://labs.bible.org/api/?passage=random&type=json"
CONTENT_FILE = "VERSE.md"
FIRE_CHANCE = 0.20  # ~20% chance per hourly check


def daily_target(date_str):
    seed = int(hashlib.sha256(date_str.encode()).hexdigest(), 16) % (2**32)
    return random.Random(seed).randint(2, 4)


def count_today(date_str):
    try:
        with open(CONTENT_FILE, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return 0
    return content.count(f"## {date_str}")


def fetch_verse():
    with urllib.request.urlopen(API_URL, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    verse = data[0]
    reference = f"{verse['bookname']} {verse['chapter']}:{verse['verse']}"
    text = verse["text"].strip()
    return reference, text


def main():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    target = daily_target(date_str)
    done_today = count_today(date_str)

    if done_today >= target:
        print(f"Target ({target}) already reached today. Skipping.")
        return

    if random.SystemRandom().random() >= FIRE_CHANCE:
        print("Not this hour. Skipping.")
        return

    reference, text = fetch_verse()
    timestamp = now.strftime("%H:%M UTC")
    entry = f"\n## {date_str} {timestamp}\n\n**{reference}**\n\n> {text}\n"

    with open(CONTENT_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"Added {reference} ({done_today + 1}/{target} today)")


if __name__ == "__main__":
    main()