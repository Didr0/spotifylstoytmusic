import os
import time
from spotipy import SpotifyOAuth
import spotipy
from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials

SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'
CREDENTIALS_FILE = "idauth.txt"

def load_credentials_from_file():
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "w") as f:
            f.write('Spotify_Client_ID="xxxx"\n')
            f.write('Spotify_Client_Secret="xxxx"\n')
            f.write('Youtube_Client_ID="xxxx"\n')
            f.write('Youtube_Client_Secret="xxxx"\n')
        print(f"File {CREDENTIALS_FILE} created. Please add your credentials to the file and try again.")
        exit()

    credentials = {}
    with open(CREDENTIALS_FILE, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=")
                credentials[key] = value.strip('"')

    return credentials

def get_credentials():
    choice = input("Do you want to load credentials from a file? (y/n): ").lower()
    
    if choice == 'y':
        credentials = load_credentials_from_file()
        spotify_client_id = credentials['Spotify_Client_ID']
        spotify_client_secret = credentials['Spotify_Client_Secret']
        ytmusic_client_id = credentials['Youtube_Client_ID']
        ytmusic_client_secret = credentials['Youtube_Client_Secret']
    else:
        spotify_client_id = input("Enter Spotify Client ID: ")
        spotify_client_secret = input("Enter Spotify Client Secret: ")
        ytmusic_client_id = input("Enter YouTube Music Client ID: ")
        ytmusic_client_secret = input("Enter YouTube Music Client Secret: ")
    
    return spotify_client_id, spotify_client_secret, ytmusic_client_id, ytmusic_client_secret

def get_user_playlists(sp):
    playlists = sp.current_user_playlists()
    print("\nYour Spotify Playlists:")
    for i, playlist in enumerate(playlists['items']):
        print(f"{i + 1}. {playlist['name']} ({playlist['tracks']['total']} tracks)")
    return playlists['items']

def get_spotify_playlist_tracks(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
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

def search_and_add_ytmusic(tracks, playlist_name, ytmusic_client_id, ytmusic_client_secret):
    ytmusic = YTMusic("oauth.json", oauth_credentials=OAuthCredentials(client_id=ytmusic_client_id, client_secret=ytmusic_client_secret))
    playlist_id = ytmusic.create_playlist(playlist_name, "Playlist imported from Spotify")
    
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

def transfer_playlists(sp, playlists, selected_indices, ytmusic_client_id, ytmusic_client_secret):
    playlist_names = {}
    for index in selected_indices:
        playlist = playlists[index]
        playlist_name = playlist['name']
        new_playlist_name = input(f"Enter a name for the new YouTube Music playlist (or press Enter to use '{playlist_name}'): ")
        if not new_playlist_name:
            new_playlist_name = playlist_name
        playlist_names[index] = new_playlist_name

    for index in selected_indices:
        playlist = playlists[index]
        playlist_id = playlist['id']
        playlist_name = playlist_names[index]

        print(f"\nFetching tracks from the playlist '{playlist['name']}'...")
        spotify_tracks = get_spotify_playlist_tracks(sp, playlist_id)
        print(f"Found {len(spotify_tracks)} tracks in the playlist.")

        print(f"Starting transfer to YouTube Music as '{playlist_name}'...")
        added, skipped = search_and_add_ytmusic(spotify_tracks, playlist_name, ytmusic_client_id, ytmusic_client_secret)
        
        print(f"\nTransfer completed for '{playlist['name']}'!")
        print(f"Songs added: {added}")
        print(f"Songs skipped: {len(skipped)}")
        if skipped:
            print("\nSongs not found:")
            for song in skipped:
                print(f"- {song}")

def main():
    spotify_client_id, spotify_client_secret, ytmusic_client_id, ytmusic_client_secret = get_credentials()

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope='playlist-read-private'
    ))

    playlists = get_user_playlists(sp)

    while True:
        selection = input("\nEnter the numbers of the playlists you want to import (e.g., '1, 4, 7'), 'all' to transfer all, or 'q' to quit: ").strip().lower()
        
        if selection == 'q':
            print("Exiting...")
            break
        elif selection in ['all', 'a']:
            selected_indices = range(len(playlists))
        else:
            try:
                selected_indices = [int(i.strip()) - 1 for i in selection.split(",")]
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas.")
                continue

        transfer_playlists(sp, playlists, selected_indices, ytmusic_client_id, ytmusic_client_secret)

        another = input("\nDo you want to transfer more playlists? (y/n): ").lower()
        if another != 'y':
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
