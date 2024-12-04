from flask import Flask, request, jsonify, render_template
from fasionfox import get_top_songs, analyze_song, get_outfit_suggestions

app = Flask(__name__)

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
    outfit_description = analyze_song(song_index)
    return jsonify({"outfit_description": outfit_description})

@app.route('/fasion-hotspot', methods=['GET'])
def fashion_hotspot():
    """Endpoint to get outfit suggestions from Etsy based on the analyzed song."""
    song_index = request.args.get('songIndex', default=0, type=int)
    outfit_style = analyze_song(song_index)  # This function now returns a style string
    outfits = get_outfit_suggestions(outfit_style)
    return jsonify(outfits)


if __name__ == '__main__':
    app.run(debug=True, port=5000)