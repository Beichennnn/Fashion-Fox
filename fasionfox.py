import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import requests
from datetime import datetime
import openai
import os
from PIL import Image

# Set up Azure OpenAI client with keys from environment variables
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_KEY")
openai.api_base = os.getenv("AZURE_ENDPOINT")
openai.api_version = "2023-10-01-preview"

# Load Spotify Credentials
with open("spotify_keys.json", "r") as keys_file:
    spotify_keys = json.load(keys_file)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=spotify_keys["client_id"],
    client_secret=spotify_keys["client_secret"],
    redirect_uri=spotify_keys["redirect"],
    scope="user-top-read"
))

with open("etsy_api.json", "r") as etsy_file:
    etsy_keys = json.load(etsy_file)

access_token = None
with open("refresh_token.txt") as refresh_code:
    refresh_token = refresh_code.read()

etsy_client_id = etsy_keys["client_id"]
etsy_client_secret = etsy_keys["client_secret"]
etsy_redirect_uri = etsy_keys["redirect"]

def get_top_songs():
    """Function to get user's top songs."""
    results = sp.current_user_top_tracks(limit=4)
    songs = []
    for track in results['items']:
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        songs.append({
            "track_name": track_name,
            "artist_name": artist_name
        })
    return songs

def analyze_song(song_index=0):
    """Function to analyze the user's favorite tracks and generate outfit suggestions based on the song index."""
    results = sp.current_user_top_tracks(limit=10)  # Ensure you fetch enough songs
    if song_index >= len(results['items']):
        return "Invalid song index"

    track = results['items'][song_index]
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    
    # Check if 'genres' key exists and if it has values
    genre = track['album'].get('genres', [])
    if genre:
        genre = genre[0]
    else:
        genre = "Unknown"
        
    tempo = 120  # Placeholder tempo value, consider integrating an API that can fetch actual tempo
    mood = "Happy"  # Placeholder mood value, consider using an analysis API for mood

    # Generate a detailed description using OpenAI Azure
    messages = [
        {"role": "system", "content": "Answer the question suitable to use for dalle prompt."},
        {"role": "user", "content": f"Based on the song '{track_name}' by {artist_name}, which is a {mood} song in the {genre} genre with a tempo of about {tempo} bpm, suggest an outfit style suitable for an adult."}
    ]

    response = openai.ChatCompletion.create(
        engine="GPT-4",
        messages=messages
    )

    outfit_style = response.choices[0].message['content'].strip()
    return outfit_style



def generate_outfit_image(description):
    """Generate an outfit image using DALL-E based on the outfit description."""

    response = openai.Image.create(
        model="Dalle3",  # Assuming you want to use DALL-E 2; adjust accordingly
        prompt=f"Fashion outfit that represents: {description}",
        n=1,
        size="1024x1024"  # You can specify the size as per the options available
    )

    # The URL of the generated image should be extracted from the response
    image_url = response['data'][0]['url']

# Save the image locally
    image_path = os.path.join('static', 'images', f'outfit_{datetime.now().strftime("%Y%m%d%H%M%S")}.png')
    if not os.path.exists(os.path.join('static', 'images')):
        os.makedirs(os.path.join('static', 'images'))

    image_data = requests.get(image_url).content
    with open(image_path, 'wb') as file:
        file.write(image_data)

    return f"/{image_path}"  # Return the path relative to the static folder


