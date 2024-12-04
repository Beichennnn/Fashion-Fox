from flask import Flask, request, jsonify, render_template
from fasionfox import get_top_songs, analyze_song, generate_outfit_image
import os
import hashlib

app = Flask(__name__)

# Simple cache to store generated image paths based on the song description hash
cache = {}

@app.route('/')
def home():
    """Home endpoint to serve the HTML page with the Fox scene."""
    return render_template('index.html')

@app.route('/top-songs', methods=['GET'])
def top_songs():
    """Endpoint to get user's top songs."""
    songs = get_top_songs()
    return jsonify(songs)

@app.route('/song-analysis', methods=['GET'])
def song_analysis():
    """Endpoint to analyze the user's favorite track and generate outfit suggestions."""
    song_index = request.args.get('songIndex', default=0, type=int)
    description = analyze_song(song_index)
    return jsonify({"description": description})

def get_cache_key(description):
    """Generate a unique cache key for each description."""
    return hashlib.md5(description.encode('utf-8')).hexdigest()

@app.route('/generate-outfit-image', methods=['GET'])
def generate_image():
    """Generate and retrieve an outfit image based on the description provided."""
    description = request.args.get('description')
    if not description:
        return jsonify({"error": "No description provided"}), 400

    # Check if the image is already cached
    cache_key = get_cache_key(description)
    if cache_key in cache:
        print(f"Cache hit for description: {description}")
        return jsonify({"image_url": cache[cache_key]})

    # If not cached, generate the image and add it to the cache
    try:
        image_path = generate_outfit_image(description)
        cache[cache_key] = image_path
        return jsonify({"image_url": image_path})
    except Exception as e:
        # Logging the exception can help in debugging
        print(f"Error generating image: {str(e)}")
        return jsonify({"error": "Failed to generate image"}), 500

@app.route('/generate-outfit-images', methods=['POST'])
def generate_multiple_images():
    """Generate and retrieve outfit images based on multiple song descriptions."""
    descriptions = request.json.get('descriptions', [])
    if not descriptions:
        return jsonify({"error": "No descriptions provided"}), 400

    image_urls = []
    for description in descriptions:
        cache_key = get_cache_key(description)
        if cache_key in cache:
            print(f"Cache hit for description: {description}")
            image_urls.append({"description": description, "image_url": cache[cache_key]})
        else:
            try:
                image_path = generate_outfit_image(description)
                if image_path:
                    cache[cache_key] = image_path
                    image_urls.append({"description": description, "image_url": image_path})
                else:
                    image_urls.append({"description": description, "error": "Failed to generate image after retries"})
            except Exception as e:
                # Logging the exception can help in debugging
                print(f"Error generating image for description '{description}': {str(e)}")
                image_urls.append({"description": description, "error": "Failed to generate image"})

    return jsonify(image_urls)



if __name__ == '__main__':
    app.run(debug=True, port=5000)
