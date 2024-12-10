from flask import Flask, request, jsonify, render_template
from fasionfox import get_top_songs, analyze_song, generate_outfit_image, create_top_songs_playlist
import boto3
import os
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)


# Function to upload image to S3
def upload_image_to_s3(image_path, bucket_name, object_name=None):
    """Upload an image to an S3 bucket."""
    # If S3 object_name was not specified, use the image filename
    if object_name is None:
        object_name = os.path.basename(image_path)
    image_path = f"C:/Users/Beichen HU/CTA/FasionFox{image_path}"
    print("if exist: {0}".format(os.path.exists(image_path)))

    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # Check if the file exists before attempting upload
        if not os.path.exists(image_path):
            print("The file was not found.")
            return None

        # Upload the file
        s3.upload_file(image_path, bucket_name, object_name, ExtraArgs={'ACL': 'public-read'})
        # Construct the public URL of the uploaded image
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        return image_url
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except NoCredentialsError:
        print("Credentials not available.")
        return None

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
    
@app.route('/generate-top-songs-playlist', methods=['GET'])
def generate_top_songs_playlist():
    """Endpoint to generate a playlist from the user's top songs."""
    try:
        playlist_url = create_top_songs_playlist()
        if playlist_url:
            return jsonify({"playlist_url": playlist_url})
        else:
            return jsonify({"error": "Failed to create playlist"}), 500
    except Exception as e:
        print(f"Error generating playlist: {str(e)}")
        return jsonify({"error": "Failed to generate playlist"}), 500

@app.route('/song-analysis', methods=['GET'])
def song_analysis():
    """Endpoint to analyze the user's favorite track and generate outfit suggestions based on season and gender."""
    try:
        song_index = request.args.get('songIndex', default=0, type=int)
        song_name = get_top_songs()[song_index]["track_name"]
        season = request.args.get('season', default='Summer', type=str)
        gender = request.args.get('gender', default='Female', type=str)
        description = analyze_song(song_index, season, gender)
        return jsonify({"description": description, "songName": song_name})
    except Exception as e:
        print(f"Error analyzing song: {str(e)}")
        return jsonify({"error": "Failed to analyze song"}), 500

@app.route('/generate-outfit-image', methods=['GET'])
def generate_outfit_image_endpoint():
    """Generate a single outfit image based on the analyzed song description and upload to S3."""
    try:
        description = request.args.get('description')
        if not description:
            return jsonify({"error": "No description provided"}), 400

        # Generate the outfit image based on the description
        print("Generating image for description:", description)
        local_image_path = generate_outfit_image(description)  # Assuming this returns a local path to the generated image
        if not local_image_path:
            print("Image generation failed.")
            return jsonify({"error": "Failed to generate outfit image"}), 500
        print("Generated image saved at:", local_image_path)

        # Upload the generated image to S3
        bucket_name = 'outfitimagesfromdalle'
        object_key = os.path.basename(local_image_path)  # Use the filename from the local path
        s3_url = upload_image_to_s3(local_image_path, bucket_name, object_key)

        if not s3_url:
            print("S3 upload failed.")
            return jsonify({"error": "Failed to upload outfit image to S3"}), 500

        print("Image successfully uploaded to S3:", s3_url)
        # Return the S3 URL of the image
        return jsonify({"image_url": s3_url})
    except Exception as e:
        print(f"Error generating or uploading outfit image: {str(e)}")
        return jsonify({"error": "Failed to generate or upload outfit image"}), 500


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