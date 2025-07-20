from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from googletrans import Translator
import os
from pydub import AudioSegment
from datetime import datetime

app = Flask(__name__)
recognizer = sr.Recognizer()
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    audio_file = request.files['audio']
    
    # Save the incoming audio file (WebM blob)
    webm_path = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.webm"
    wav_path = webm_path.replace('.webm', '.wav')
    audio_file.save(webm_path)

    try:
        # Convert WebM to WAV using pydub
        sound = AudioSegment.from_file(webm_path, format="webm")
        sound.export(wav_path, format="wav")

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        target_lang = request.form.get('language')
        result = translator.translate(text, dest=target_lang)

        return jsonify({
            'original': text,
            'translated': result.text
        })
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        if os.path.exists(webm_path):
            os.remove(webm_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

if __name__ == '__main__':
    app.run(debug=True)
