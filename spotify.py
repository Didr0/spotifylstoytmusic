import os
import time
from spotipy import SpotifyOAuth
import spotipy
from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials

SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'

def get_spotify_liked_songs(spotify_client_id, spotify_client_secret):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope='user-library-read')
    )

    results = sp.current_user_saved_tracks()
    tracks = results['items']
    
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
        time.sleep(0.5)

    return [{
        'artist': item['track']['artists'][0]['name'],
        'title': item['track']['name'],
        'album': item['track']['album']['name']
    } for item in tracks]

def search_and_add_ytmusic(tracks, ytmusic_client_id, ytmusic_client_secret):
    ytmusic = YTMusic("oauth.json", oauth_credentials=OAuthCredentials(client_id=ytmusic_client_id, client_secret=ytmusic_client_secret))
    playlist_id = ytmusic.create_playlist("Spotify Liked Songs", "Songs imported from Spotify")
    
    added = 0
    skipped = []

    for track in tracks:
        query = f"{track['artist']} - {track['title']}"
        search_results = ytmusic.search(query, filter='songs')
        
        if search_results:
            video_id = search_results[0]['videoId']
            ytmusic.add_playlist_items(playlist_id, [video_id])
            added += 1
        else:
            skipped.append(query)
        
        time.sleep(1)

    return added, skipped

if __name__ == "__main__":
    spotify_client_id = input("Enter Spotify Client ID: ")
    spotify_client_secret = input("Enter Spotify Client Secret: ")
    
    ytmusic_client_id = input("Enter YouTube Music Client ID: ")
    ytmusic_client_secret = input("Enter YouTube Music Client Secret: ")

    print("Fetching liked songs from Spotify...")
    spotify_tracks = get_spotify_liked_songs(spotify_client_id, spotify_client_secret)
    print(f"Found {len(spotify_tracks)} songs")
    
    print("Starting transfer to YouTube Music...")
    added, skipped = search_and_add_ytmusic(spotify_tracks, ytmusic_client_id, ytmusic_client_secret)
    
    print(f"\nTransfer completed!")
    print(f"Songs added: {added}")
    print(f"Songs skipped: {len(skipped)}")
    if skipped:
        print("\nSongs not found:")
        for song in skipped:
            print(f"- {song}")
