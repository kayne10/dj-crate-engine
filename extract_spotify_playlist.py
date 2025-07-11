import os
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

scope = "playlist-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope
))

def get_playlist_id_by_name(name):
    playlists = sp.current_user_playlists(limit=50)
    for pl in playlists['items']:
        if pl['name'].lower() == name.lower():
            return pl['id']
    raise ValueError(f"No playlist found with name '{name}'")

def extract_tracks(playlist_id):
    results = sp.playlist_items(playlist_id, additional_types=['track'])
    tracks = []

    for item in results['items']:
        track = item.get('track')
        if not track or track.get('id') is None:
            continue  # Skip non-tracks or local files

        # Basic info
        track_id = track['id']
        name = track['name']
        artist = track['artists'][0]['name']

        # NOTE: Audio features endpoint is no longer available for free https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api
        # Audio features
        # BPM would nice to have for organizing crates :(
        # features = sp.audio_features([track_id])[0]
        # if not features:
        #     continue

        track_data = {
            "track_id": track_id,
            "track_name": name,
            "artist": artist,
        }
        tracks.append(track_data)

    return tracks

if __name__ == "__main__":
    playlist_name = input("Enter Spotify playlist name: ")
    # playlist_name = "ESP 🕺 🪩 🎈"
    playlist_id = get_playlist_id_by_name(playlist_name)
    # playlist_id = "7emprb2X3hpLCMAZqZmuRF"

    print(f"Fetching tracks from: {playlist_name}")
    tracks = extract_tracks(playlist_id)
    print(f"Found a total of {len(tracks)} tracks")
    
    # Write to track names to a txt file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = Path(f"{base_dir}/output/spotify/{playlist_name.lower()}_tracks.txt")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        for t in tracks:
            f.write(f"{t['track_name']} by {t['artist']}\n")