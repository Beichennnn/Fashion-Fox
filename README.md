# 🦊 Outfit Explorer

**Outfit Explorer** is a magical 🪄 web application where your favorite Spotify 🎵 tracks meet creative fashion ideas! Led by your guide, a curious **Fox 🦊**, explore a 3D world 🌍 where music inspires your wardrobe. Analyze your top songs, generate unique outfits, and jam out to your personal playlist — all in one interactive experience. 🎧✨

------

## ✨ Features

- 🎶 **Spotify Integration**: Fetch your top tracks directly from Spotify and build a custom playlist!
- 🌌 **3D Exploration**: Immerse yourself in an interactive scene with hotspots for music and fashion discovery.
- 👗 **Song-Based Outfit Generation**: Transform the vibes of your favorite songs into stunning outfit ideas.
- 🎧 **Custom Playlist Sidebar**: Play your top Spotify tracks while exploring the app.
- 🖼️ **Gallery of Generated Outfits**: Save and view your personalized fashion creations.
- 🦊 **Fox-Themed Adventure**: Your companion, the **Fox**, adds a playful charm to every interaction.
- 🖥️ **Responsive UI**: Designed for a seamless experience across devices. 

------

## 🛠️ Technologies Used

### Frontend

- **HTML5, CSS3, JavaScript**: Core web technologies for building the UI.
- **SweetAlert2**: For sleek and modern pop-ups. 
- **Spotify Web API**: To fetch and manage music data. 
- **3D Rendering**: Powered by a **Spline**-based runtime for interactive experiences.

### Backend

- **Python (Flask)**: A lightweight framework for serving APIs and rendering templates. 
- **Spotipy**: Python client library for the Spotify Web API.
- **AWS S3**: ☁️ For storing and accessing generated outfit images securely. 

------

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher 
- Spotify Developer Account 

### Installation

1.  Clone the repository:

   ```bash
   git clone https://github.com/yourusername/outfit-explorer.git
   cd outfit-explorer
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3.  Set up Spotify credentials:

   - Create a 

     ```
     spotify_keys.json
     ```

      file in the root directory and add:

     ```
     {
         "username": "your_user_name",
         "client_id": "your_client_id",
         "client_secret": "your_client_secret",
         "redirect": "your_redirect_web" in my case is: "https://google.com"
     }
     ```

4. ☁️ Configure AWS (optional for storing images):

   - Add AWS keys to 

     ```
     .env
     ```

     :

     ```
     AWS_ACCESS_KEY_ID=your_aws_access_key
     AWS_SECRET_ACCESS_KEY=your_aws_secret_key
     AWS_S3_BUCKET_NAME=your_bucket_name
     ```

5. 🖥️ Set up Azure OpenAI client with keys from environment variables

   ```
   set AZURE_KEY="your_key"
   set AZURE_ENDPOINT="your_endpoint"
   ```

6. 🌐 Enable virtual environment and Start the Flask server:

   ```
   flask run
   ```

------

## 🦊 How to Use

1. **🎵 Login with Spotify**: Authenticate and fetch your top tracks.
2. **🌌 Explore the 3D Scene**: Click on hotspots to interact with options for music and fashion.
3. **👗 Generate Outfits**: Select a song, analyze its mood, and watch the **Fox** work its magic.
4. **📂 Save Your Favorites**: Keep your best outfits in the gallery for later inspiration.
5. **🎧 Play Your Playlist**: Use the custom sidebar to jam out while exploring.

------

## 📂 File Structure

```
outfit-explorer/
│
├── static/                     # Static assets (CSS, JavaScript, images)
│   ├── css/
│   │   └── styles.css          # Custom styles
│   ├── js/
│   │   └── runtime.js          # Spline runtime
│   ├── images/
│   └── scenes/
│       └── scene.splinecode    # 3D scene file
│
├── templates/
│   └── index.html              # Main HTML template
│
├── app.py                      # Main Flask app
├── fasionfox.py                # Spotify and outfit generation logic
├── spotify_keys.json           # Place to store your Spotify credentials
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

------

## 🌟 Future Enhancements

- **🧠 AI Outfit Suggestions**: Incorporate advanced AI for more personalized styles.
- **🎮 Multiplayer Interaction**: Allow users to explore the 3D scene together.
- **📱 Social Sharing**: Share your outfit creations on social media with one click.
