# Before to run this program, run this commands
# python -m venv
# pip3 install requests
# pip3 install bs4
# pip3 install python-dotenv
import os
from dotenv import load_dotenv
import requests 
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
SPOTIPY_CLIENT_ID = str(os.getenv('SPOTIPY_CLIENT_ID')) #Your spotify client id
SPOTIPY_CLIENT_SECRET = str(os.getenv('SPOTIPY_CLIENT_SECRET')) #Your spotify client secret
SPOTIPY_REDIRECT_URI = str(os.getenv('SPOTIPY_REDIRECT_URI')) #Your spotify redirect uri
SCOPE = str(os.getenv('SCOPE')) #Your spotify spotify scope

print("Welcome to the time machine!\nThis program has the task of creating a playlist on Spotify with the best 100 songs of the year, the month, and the day you enter.\n")

# Get the date from the user
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD:\n")

# Billboard data scraping 
BILLBOARD_HOT_ENDPOINT = f"https://www.billboard.com/charts/hot-100/{date}"
response = requests.get(url=BILLBOARD_HOT_ENDPOINT)
response.raise_for_status()
yc_web_page = response.text

# Scrape the data from billboard and gets the top 100 songs in {date}
soup = BeautifulSoup(yc_web_page, "html.parser")
all_songs = soup.select(selector="li h3#title-of-a-story")
song_names = [s.get_text().strip() for s in all_songs]

# Create an instance of SpotifyOAuth with your client ID, client secret and redirection URI
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID, 
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

# Loops through the song_names scraped from billboard, to find the corrispective song in Spotify
song_uris = []
year = date.split("-")[0]
for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

#Creating a new private playlist in Spotify
playlist_name = f"{date} Billboard 100"
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
#Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)