import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import requests
from datetime import datetime
import openai
import os

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
        {"role": "system", "content": "You are an assistant that provides detailed outfit suggestions based on music mood and style."},
        {"role": "user", "content": f"Based on the song '{track_name}' by {artist_name}, which is a {mood} song in the {genre} genre with a tempo of about {tempo} bpm, suggest an outfit style suitable for an adult."}
    ]

    response = openai.ChatCompletion.create(
        engine="GPT-4",
        messages=messages
    )

    outfit_style = response.choices[0].message['content'].strip()
    return outfit_style



def exchange_code_for_token(authorization_code):
    token_url = "https://api.etsy.com/v3/public/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": etsy_redirect_uri,
        "client_id": etsy_client_id,
        "client_secret": etsy_client_secret
    }

    response = requests.post(token_url, data=data)
    print("Token Exchange Response:", response.status_code, response.text)
    if response.status_code == 200:
        token_info = response.json()
        return token_info["access_token"], token_info["refresh_token"]
    else:
        return None, None
    
def refresh_access_token():
    token_url = "https://api.etsy.com/v3/public/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": etsy_client_id,
        "client_secret": etsy_client_secret,
    }

    response = requests.post(token_url, data=data)
    print("Token Refresh Response:", response.status_code, response.text)
    if response.status_code == 200:
        token_info = response.json()
        return token_info["access_token"]
    else:
        return None

def get_outfit_suggestions(outfit_style):
    """Function to get outfit suggestions from Etsy based on the analyzed song."""
    global access_token
    if not access_token:
        access_token = refresh_access_token()  # Refresh the token if not set

    url = "https://openapi.etsy.com/v3/application/listings/active"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-api-key": etsy_client_id,
    }
    params = {
        "keywords": f"{outfit_style} adult clothing",  # Use the style from OpenAI and focus on adult clothing
        "limit": 2,
        "sort_on": "score",
        "currency": "GBP",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json().get("results", [])
        outfits = []
        for item in results:
            outfits.append({
                "title": item.get("title"),
                "price": item.get("price"),
                "url": item.get("url"),
                "image_url": item.get("images", [])[0].get("url_fullxfull") if item.get("images") else None
            })
        return outfits
    else:
        return {"error": "Failed to fetch outfits based on song style."}

