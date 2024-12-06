from flask import Flask, request, jsonify, render_template
from fasionfox import get_top_songs, analyze_song, generate_outfit_image

app = Flask(__name__)

@app.route('/')
def home():
    """Home endpoint to serve the HTML page with the Fox scene."""
    return render_template('index.html')

@app.route('/top-songs', methods=['GET'])
def top_songs():
    """Endpoint to get user's top songs."""
    try:
        songs = get_top_songs()
        return jsonify(songs)
    except Exception as e:
        print(f"Error fetching top songs: {str(e)}")
        return jsonify({"error": "Failed to fetch top songs"}), 500

@app.route('/song-analysis', methods=['GET'])
def song_analysis():
    """Endpoint to analyze the user's favorite track and generate outfit suggestions based on season and gender."""
    try:
        song_index = request.args.get('songIndex', default=0, type=int)
        season = request.args.get('season', default='Summer', type=str)
        gender = request.args.get('gender', default='Female', type=str)
        description = analyze_song(song_index, season, gender)
        return jsonify({"description": description})
    except Exception as e:
        print(f"Error analyzing song: {str(e)}")
        return jsonify({"error": "Failed to analyze song"}), 500

@app.route('/generate-outfit-image', methods=['GET'])
def generate_outfit_image_endpoint():
    """Generate a single outfit image based on the analyzed song description."""
    try:
        description = request.args.get('description')
        if not description:
            return jsonify({"error": "No description provided"}), 400

        # Generate the outfit image based on the description
        image_url = generate_outfit_image(description)
        if not image_url:
            return jsonify({"error": "Failed to generate outfit image"}), 500

        return jsonify({"image_url": image_url})
    except Exception as e:
        print(f"Error generating outfit image: {str(e)}")
        return jsonify({"error": "Failed to generate outfit image"}), 500

@app.route('/generate-outfit-images', methods=['POST'])
def generate_outfit_images():
    """Generate and retrieve multiple outfit images based on the analyzed songs provided."""
    try:
        data = request.get_json()
        if not data or 'analyzedSongs' not in data:
            return jsonify({"error": "No analyzed songs provided"}), 400

        analyzed_songs = data['analyzedSongs']
        if not isinstance(analyzed_songs, list):
            return jsonify({"error": "Invalid data format for analyzed songs"}), 400

        images = []
        for song in analyzed_songs:
            description = song.get('description')
            if description:
                image_path = generate_outfit_image(description)
                if image_path:
                    images.append(image_path)
                else:
                    print(f"Error generating image for description: {description}")

        if not images:
            return jsonify({"error": "Failed to generate any outfits"}), 500

        return jsonify({"images": images})

    except Exception as e:
        # Logging the exception for debugging
        print(f"Error generating images: {str(e)}")
        return jsonify({"error": "Failed to generate images"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
