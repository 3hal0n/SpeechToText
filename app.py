from flask import Flask, request, render_template, jsonify
import os
import torch
import numpy as np
from transformers import pipeline
import tempfile
import logging
import soundfile as sf
import io
import subprocess

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for the pipelines
asr_pipeline_whisper = None
asr_pipeline_wav2vec = None

def load_models():
    global asr_pipeline_whisper, asr_pipeline_wav2vec
    try:
        if torch.cuda.is_available():
            device_str = f"cuda ({torch.cuda.get_device_name(0)})"
            device_id = 0
        else:
            device_str = "cpu"
            device_id = -1
        logger.info(f"Loading Whisper small model for Sinhala on {device_str}...")
        asr_pipeline_whisper = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-small",
            device=device_id,
            generate_kwargs={"language": "si"}
        )
        logger.info("Whisper model loaded successfully!")
        logger.info(f"Loading wav2vec2 model for English on {device_str}...")
        asr_pipeline_wav2vec = pipeline(
            "automatic-speech-recognition",
            model="facebook/wav2vec2-base-960h",
            device=device_id
        )
        logger.info("wav2vec2 model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading ASR models: {e}")
        raise

def transcribe_audio(audio_path, lang="si"):
    try:
        audio, sampling_rate = sf.read(audio_path)
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        if sampling_rate != 16000:
            import scipy.signal
            number_of_samples = round(len(audio) * float(16000) / sampling_rate)
            audio = scipy.signal.resample(audio, number_of_samples)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            sf.write(tmp_wav.name, audio, 16000)
            if lang == "en":
                result = asr_pipeline_wav2vec(tmp_wav.name)
            else:
                result = asr_pipeline_whisper(tmp_wav.name, generate_kwargs={"language": "si"})
        os.unlink(tmp_wav.name)
        return result["text"]
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return f"Error: {str(e)}"

def convert_webm_to_wav(webm_path):
    wav_path = webm_path.rsplit('.', 1)[0] + '.wav'
    try:
        subprocess.run(['ffmpeg', '-y', '-i', webm_path, wav_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return wav_path
    except Exception as e:
        raise RuntimeError(f"ffmpeg conversion failed: {e}")

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
    allowed_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.webm'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'}), 400
    lang = request.form.get('lang', 'si')
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        if file_ext == '.webm':
            try:
                wav_path = convert_webm_to_wav(tmp_path)
                transcription = transcribe_audio(wav_path, lang=lang)
                os.unlink(wav_path)
            except Exception as e:
                logger.error(f"Error converting webm to wav: {e}")
                os.unlink(tmp_path)
                return jsonify({'error': f'Could not process .webm file: {e}'}), 400
        else:
            transcription = transcribe_audio(tmp_path, lang=lang)
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
    return jsonify({'status': 'healthy', 'model_loaded': asr_pipeline_whisper is not None and asr_pipeline_wav2vec is not None})

if __name__ == '__main__':
    # Load models on startup
    load_models()
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)