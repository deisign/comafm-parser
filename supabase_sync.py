import os
import requests
import json

# Отримуємо параметри з середовища
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
HISTORY_JSON_URL = os.getenv('HISTORY_JSON_URL')

# Заголовки для Supabase API
headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
}

def get_history():
    """Завантажити history.json"""
    response = requests.get(HISTORY_JSON_URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Не вдалося отримати history.json: {response.status_code}")

def track_exists(artist, title):
    """Перевірити чи є трек у Supabase"""
    params = {
        "artist": f"eq.{artist}",
        "title": f"eq.{title}",
        "select": "id"
    }
    response = requests.get(f"{SUPABASE_URL}/rest/v1/tracks", headers=headers, params=params)
    return bool(response.json())

def add_track(artist, title):
    """Додати новий трек у Supabase"""
    payload = {
        "artist": artist,
        "title": title,
        "score": 0
    }
    response = requests.post(f"{SUPABASE_URL}/rest/v1/tracks", headers=headers, json=payload)
    return response.status_code == 201

def main():
    history = get_history()
    unique_tracks = set((track['artist'], track['title']) for track in history)

    added = 0
    for artist, title in unique_tracks:
        if not track_exists(artist, title):
            if add_track(artist, title):
                added += 1

    print(f"Додано нових треків: {added}")

if __name__ == "__main__":
    main()
