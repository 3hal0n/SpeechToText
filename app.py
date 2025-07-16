from flask import Flask, request, render_template, jsonify
import os
import torch
import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import tempfile
import logging
import soundfile as sf
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model and processor
model = None
processor = None

def load_model():
    """Load the Wav2Vec2 model and processor"""
    global model, processor
    try:
        logger.info("Loading Wav2Vec2 model...")
        processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
        model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def transcribe_audio(audio_path):
    """Transcribe audio file to text"""
    try:
        # Load audio file using soundfile (compatible with Python 3.13)
        audio, sampling_rate = sf.read(audio_path)
        
        # Ensure audio is mono
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        
        # Resample to 16kHz if needed
        if sampling_rate != 16000:
            # Simple resampling (you might want to use scipy.signal.resample for better quality)
            ratio = 16000 / sampling_rate
            audio = np.interp(
                np.arange(0, len(audio), 1/ratio),
                np.arange(0, len(audio)),
                audio
            )
        
        # Process audio
        input_values = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
        
        # Get logits from model
        with torch.no_grad():
            logits = model(input_values.input_values).logits
        
        # Get predicted ids
        predicted_ids = torch.argmax(logits, dim=-1)
        
        # Decode to text
        transcription = processor.batch_decode(predicted_ids)[0]
        
        return transcription.lower()
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return f"Error: {str(e)}"

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Handle audio file upload and transcription"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    allowed_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'}), 400
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        # Transcribe audio
        transcription = transcribe_audio(tmp_path)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return jsonify({
            'transcription': transcription,
            'filename': file.filename
        })
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

if __name__ == '__main__':
    # Load model on startup
    load_model()
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)