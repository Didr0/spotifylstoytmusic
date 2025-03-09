# spotify_to_ytmusic
transfer any playlist from spotify to ytmusic

SETUP

1. Spotify Developer Dashboard
Go to: https://developer.spotify.com/

Create an API:

Redirect URL: http://localhost:8888/callback

API Type: Web API

2. Google Cloud Console
Go to: https://console.cloud.google.com/auth

Create an app:

Enable "YouTube Data API v3".

Create an OAuth Client ID (Type: TVs and Limited Input devices).

Add your email address to the list of test accounts that can access this app.

3. Install Python
Download and install Python from the official website: https://www.python.org/

4. Install ytmusicapi (in the terminal)

pip install ytmusicapi

5. Generate OAuth Credentials (in the terminal)

ytmusicapi oauth
Enter the Client ID and Client Secret from Step 2.

The terminal will return a code. Paste this code into the login screen that appears.

6. Locate oauth.json
Use Everything (or any file search tool) to search for the file oauth.json.

7. Copy the File
Copy the oauth.json file from Step 6 into a folder.

8. Copy the Python Code
Copy the provided Python script (spotify.py) into the same folder as oauth.json.

9. Run the Script (in the terminal)
Navigate to the folder containing the files and run:

python spotify.py

10. Enter Required Data
Input the requested data (e.g., Spotify and YouTube Music credentials).

Wait for the process to complete.
