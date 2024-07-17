# Fuse: Video Slideshow Creator 🎬

## Introduction ✨

Fuse is a web application that empowers users to create captivating video slideshows from their photos and audio. Developed by team Code Fusion for the Introduction to Software Systems (ISS) course at IIIT Hyderabad, Spring 2024, Fuse offers a user-friendly platform with custom audio and transition libraries.

## Features 🚀

- Create stunning video slideshows from photos and audio
- User account creation and management
- Secure authentication using JWT tokens for persistent login
- Cloud storage for user images, allowing reuse across multiple projects
- Custom audio library with a wide range of music and sound effects
- Extensive transition effects library for professional-looking videos
- Support for all image formats (JPEG, PNG, GIF, TIFF, WebP, SVG, etc.)
- Support for all audio formats (MP3, WAV, AAC, FLAC, OGG, etc.)
- Video download functionality in various formats and qualities
- Export options including:
  - Common formats: MP4, AVI, MOV, WMV
  - High-quality options: 4K, 1080p, 720p all the way down to 144p!
  - Custom quality settings for advanced users
- User-friendly interface designed for both beginners and advanced users
- Real-time preview of slideshow during creation
- Ability to adjust timing, duration, and order of slides
- Text overlay feature for adding captions or titles to slides
- Filters and basic image editing tools

## Tech Stack 💻

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript, jQuery
- Styling: Bootstrap
- Database: MySQL
- Media Processing: FFmpeg
- Authentication: JWT (JSON Web Tokens)
- Cloud Storage: AWS S3 (for storing user images)

## Installation 🛠️

1. Clone the repository:
   ```
   git clone https://github.com/your-username/fuse.git
   cd fuse
   ```

2. Set up a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Install FFmpeg:
   - On macOS (using Homebrew):
     ```
     brew install ffmpeg
     ```
   - On Ubuntu/Debian:
     ```
     sudo apt-get update
     sudo apt-get install ffmpeg
     ```
   - On Windows:
     Download from [FFmpeg official website](https://ffmpeg.org/download.html) and add to PATH

## Usage 🖥️

1. Start the Flask development server:
   ```
   flask run
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Create an account or log in to an existing one.

4. Upload your images and audio files, or choose from the provided libraries.

5. Arrange your slides, add transitions, and adjust timings as desired.

6. Preview your slideshow in real-time.

7. When satisfied, export your video in your preferred format and quality.

8. Download your created video slideshow and enjoy!

## Acknowledgments 👏

- IIIT Hyderabad for providing the opportunity to work on this project
- The open-source community for the wonderful tools and libraries used in this project
