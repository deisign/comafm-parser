import os
import requests
import json
from lookup_track import lookup_track

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
HISTORY_JSON_URL = os.getenv('HISTORY_JSON_URL')

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
}


def get_history():
    response = requests.get(HISTORY_JSON_URL, timeout=10)
    response.raise_for_status()
    return response.json()


def track_exists(artist, title):
    params = {
        "artist": f"eq.{artist}",
        "title": f"eq.{title}",
        "select": "id"
    }
    r = requests.get(f"{SUPABASE_URL}/rest/v1/tracks", headers=headers, params=params, timeout=10)
    if r.status_code == 200 and r.json():
        return True
    return False


def add_track(payload):
    response = requests.post(f"{SUPABASE_URL}/rest/v1/tracks", headers=headers, json=payload, timeout=10)
    if response.status_code != 201:
        print(f"[ERROR] Failed to insert: {payload['artist']} - {payload['title']}")
        print(response.text)
    return response.status_code == 201


def main():
    history = get_history()
    print(f"[DEBUG] Отримано треків з history.json: {len(history)}")

    seen = set()
    added = 0

    for track in history:
        artist = track.get("artist")
        title = track.get("title")
        key = (artist, title)

        print(f"[DEBUG] Трек: {artist} — {title}")

        if not artist or not title or key in seen:
            continue
        seen.add(key)

        if not track_exists(artist, title):
            payload = {
                "artist": artist,
                "title": title,
                "score": 0
            }

            enriched = lookup_track(artist, title)
            payload.update(enriched)

            print("[ENRICHED]", json.dumps(payload, ensure_ascii=False))

            if add_track(payload):
                print(f"[ADD] {artist} - {title}")
                added += 1

    print(f"Додано нових треків: {added}")


if __name__ == "__main__":
    main()
