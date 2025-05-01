import os
import requests

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')


def get_spotify_token():
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
        timeout=10
    )
    response.raise_for_status()
    return response.json()["access_token"]


def query_spotify(artist, title):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    query = f"{artist} {title}"

    r = requests.get(
        "https://api.spotify.com/v1/search",
        params={"q": query, "type": "track", "limit": 1},
        headers=headers,
        timeout=10
    )
    r.raise_for_status()
    results = r.json()["tracks"]["items"]
    if not results:
        return None

    track = results[0]
    album = track["album"]

    return {
        "album": album.get("name", ""),
        "year": int(album.get("release_date", "0000")[:4]) if album.get("release_date") else None,
        "artwork_url": album["images"][0]["url"] if album.get("images") else "",
        "spotify_url": track["external_urls"]["spotify"],
        "genres": []  # Spotify не повертає жанри напряму для треків
    }


def query_lastfm(artist, title):
    r = requests.get(
        "http://ws.audioscrobbler.com/2.0/",
        params={
            "method": "track.getInfo",
            "api_key": LASTFM_API_KEY,
            "artist": artist,
            "track": title,
            "format": "json"
        },
        timeout=10
    )
    r.raise_for_status()
    data = r.json().get("track", {})

    album = data.get("album", {})
    images = album.get("image", [])
    artwork_url = images[-1]["#text"] if images else ""

    tags = data.get("toptags", {}).get("tag", [])
    genres = [tag["name"] for tag in tags[:5]] if tags else []

    return {
        "album": album.get("title", ""),
        "year": None,
        "artwork_url": artwork_url,
        "spotify_url": "",
        "genres": genres
    }


def lookup_track(artist, title):
    try:
        print(f"[lookup] Trying Spotify for: {artist} — {title}")
        data = query_spotify(artist, title)
        if data:
            print(f"[Spotify] OK: {artist} — {title}")
            return data
    except Exception as e:
        print(f"[Spotify] Failed: {e}")

    try:
        print(f"[lookup] Fallback to Last.fm for: {artist} — {title}")
        data = query_lastfm(artist, title)
        if data:
            print(f"[Last.fm] OK: {artist} — {title}")
            return data
    except Exception as e:
        print(f"[Last.fm] Failed: {e}")

    return {
        "album": "",
        "year": None,
        "artwork_url": "",
        "spotify_url": "",
        "genres": []
    }
