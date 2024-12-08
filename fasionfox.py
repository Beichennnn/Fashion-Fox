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

def get_top_songs():
    """Function to get user's top songs."""
    results = sp.current_user_top_tracks(limit=10)
    songs = []
    for track in results['items']:
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        songs.append({
            "track_name": track_name,
            "artist_name": artist_name
        })
    return songs

def analyze_song(song_index=0, season="Summer", gender="Female"):
    """Function to analyze the user's favorite tracks and generate outfit suggestions based on the song index, season, and gender."""
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

    # Use OpenAI to determine the mood of the song
    mood_prompt = [
        {"role": "system", "content": "You are a music analyst. Given a song title, artist, genre, and tempo, describe the overall mood of the song."},
        {"role": "user", "content": f"The song '{track_name}' by {artist_name} is in the {genre} genre. What is the overall mood of this song?"}
    ]

    try:
        mood_response = openai.ChatCompletion.create(
            engine="GPT-4",
            messages=mood_prompt
        )
        mood = mood_response.choices[0].message['content'].strip().capitalize()
    except openai.error.OpenAIError as e:
        print(f"Error determining song mood: {str(e)}")
        mood = "Happy"  # Fallback mood in case of an error

    # Generate a detailed analysis including song and outfit suggestion based on the mood, season, and gender
    messages = [
        {
            "role": "system",
            "content": "Provides song information simply, then after a hyphen, give short fashionable and popular outfit suggestions inspired by high fashion magazines like Vogue, Elle, or Harper's Bazaar. Use luxurious descriptors without mentioning specific brands and artist's name. And control the answer length, make answer short and make sure the answer as a prompt won't make task failed as a result of Dalle safety system."
        },
        {
            "role": "user",
            "content": f"Based on the song '{track_name}' by {artist_name}, which is a {mood} song in the {genre} genre, suggest an short outfit style for a {gender} during the {season} season that would look fashionable and runway-worthy, inspired by high fashion magazines. without mentioning specific brands and artist's name. And won't make task failed as a result of Dalle safety system."
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            engine="GPT-4",
            messages=messages
        )
        full_analysis = response.choices[0].message['content'].strip()

        # Extract only the outfit suggestion after the hyphen
        if "-" in full_analysis:
            _, outfit_recommendation = full_analysis.split("-", 1)
            return outfit_recommendation.strip()
        else:
            # If no hyphen is found, return the full analysis for safety
            return full_analysis

    except openai.error.OpenAIError as e:
        print(f"Error generating GPT response: {str(e)}")
        return None


def generate_outfit_image(description, retry_count=3):
    """Generate an outfit image using DALL-E based on the outfit description, with retry mechanism."""
    for attempt in range(retry_count):
        try:
            # Log the prompt for debugging
            print(f"Attempt {attempt + 1}: Generated prompt for DALL-E: {description}")

            # Generate the image using the OpenAI API
            response = openai.Image.create(
                model="Dalle3", 
                prompt=description,
                n=1,
                size="1024x1024"
            )

            # Extract the URL of the generated image
            image_url = response['data'][0]['url']

            # Save the image locally
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_filename = f'outfit_{timestamp}.png'
            image_path = os.path.join('static/images', image_filename)

            if not os.path.exists('static/images'):
                os.makedirs('static/images')

            image_data = requests.get(image_url).content
            with open(image_path, 'wb') as file:
                file.write(image_data)

            return f"/static/images/{image_filename}"

        except openai.error.InvalidRequestError as e:
            # Log the failure and retry if necessary
            print(f"Error generating image for description '{description}': {str(e)}")
            if attempt == retry_count - 1:
                return None  # If all attempts fail, return None

    return None
