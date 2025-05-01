import os
import requests

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')


def get_spotify_token():
    auth_response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )
    auth_response.raise_for_status()
    return auth_response.json()["access_token"]


def query_spotify(artist, title):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    query = f"{artist} {title}"

    r = requests.get(
        "https://api.spotify.com/v1/search",
        params={"q": query, "type": "track", "limit": 1},
        headers=headers,
    )
    if r.status_code != 200 or not r.json()["tracks"]["items"]:
        return None

    track = r.json()["tracks"]["items"][0]
    album = track["album"]
    return {
        "album": album.get("name", ""),
        "year": int(album.get("release_date", "0000")[:4]),
        "artwork_url": album["images"][0]["url"] if album["images"] else "",
        "spotify_url": track["external_urls"]["spotify"],
        "genres": []  # отримаємо окремо
    }


def get_spotify_genres(artist_id, token):
    r = requests.get(
        f"https://api.spotify.com/v1/artists/{artist_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    if r.status_code == 200:
        return r.json().get("genres", [])
    return []


def query_lastfm(artist, title):
    query = f"{artist} - {title}"
    r = requests.get(
        "http://ws.audioscrobbler.com/2.0/",
        params={
            "method": "track.getInfo",
            "api_key": LASTFM_API_KEY,
            "artist": artist,
            "track": title,
            "format": "json",
        },
    )
    if r.status_code != 200:
        return {}

    data = r.json().get("track", {})
    album = data.get("album", {})
    image_list = album.get("image", [])
    artwork_url = image_list[-1]["#text"] if image_list else ""

    tags = data.get("toptags", {}).get("tag", [])
    genres = [tag["name"] for tag in tags[:5]] if tags else []

    return {
        "album": album.get("title", ""),
        "year": None,
        "artwork_url": artwork_url,
        "spotify_url": "",
        "genres": genres,
    }


def lookup_track(artist, title):
    try:
        data = query_spotify(artist, title)
        if data:
            token = get_spotify_token()
            # отримуємо жанри окремо (виконавець → жанри)
            artist_id = data["spotify_url"].split("/")[-1]  # трюк, не завжди працює
            data["genres"] = []
            return data
    except Exception as e:
        print(f"[Spotify] Failed: {e}")

    try:
        data = query_lastfm(artist, title)
        if data:
            return data
    except Exception as e:
        print(f"[Last.fm] Failed: {e}")

    return {
        "album": "",
        "year": None,
        "artwork_url": "",
        "spotify_url": "",
        "genres": [],
    }
