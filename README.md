## Speech to Text App

[![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern web application for transcribing speech from audio files or live voice recordings using OpenAI's Whisper large-v3 model (via Hugging Face Transformers). Features a beautiful dark purple UI, drag-and-drop upload, browser-based recording, and Sinhala speech recognition support.

## Features
- 🎤 Record voice directly in your browser (with waveform visualization)
- 📁 Upload audio files (WAV, MP3, M4A, FLAC, OGG, WebM)
- 📝 Instant speech-to-text transcription using Whisper large-v3 (multilingual, including Sinhala)
- 📋 Copy transcription to clipboard
- 🎧 Playback your audio
- Responsive, modern dark purple design

## Sinhala Support

This app now supports Sinhala (සිංහල) speech recognition using OpenAI's Whisper large-v3 model. Just upload or record Sinhala audio and receive Sinhala text transcription. Whisper also supports many other languages—see [Whisper documentation](https://github.com/openai/whisper) for details.

**Note:** Whisper large-v3 is a very large model. For best performance, use a machine with a modern GPU. CPU inference is possible but much slower.

## Model

This app uses the [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) model from Hugging Face for multilingual (including Sinhala) speech recognition.

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/speech-to-text-app.git
cd speech-to-text-app
```

### 2. Install Python dependencies
It is recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install ffmpeg (required for .webm audio)
- Download from [ffmpeg.org](https://ffmpeg.org/download.html) or [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
- Add the `bin` folder to your system PATH
- Verify installation:
  ```bash
  ffmpeg -version
  ```

### 4. Run the app
```bash
python app.py
```
Visit [http://localhost:5000](http://localhost:5000) in your browser.

## Usage
- **Upload**: Drag and drop or select an audio file.
- **Record**: Use the "Record Voice" tab to record directly in your browser.
- **Supported formats**: `.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.webm`
- **Copy**: Click "Copy Text" to copy the transcription.

## Project Structure
```
speechToText/
├── app.py                # Flask backend
├── requirements.txt      # Python dependencies
├── static/
│   └── styles.css        # Main stylesheet (dark purple theme)
├── templates/
│   └── index.html        # Main frontend template
```

## Dependencies
- Flask
- torch
- transformers
- soundfile
- numpy
- scipy
- Werkzeug
- ffmpeg (system dependency)

## Troubleshooting
- **ffmpeg not found**: Make sure ffmpeg is installed and in your system PATH. Restart your terminal after installation.
- **Model loading issues**: Ensure you have a stable internet connection for the first run (downloads model weights).
- **Audio not transcribing**: Check browser permissions for microphone and supported formats.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE) 