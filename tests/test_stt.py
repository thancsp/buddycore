# test_stt.py
# =================
# This script tests speech-to-text (STT) functionality.
# It records a few seconds of microphone audio, transcribes it using Whisper,
# and then speaks the result using Piper TTS.

import os
import sys

# 🔧 Add Buddy Core root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audio_controller import AudioController

ac = AudioController()
# This method will handle TTS intro, beep, recording, transcription, and speaking result
text = ac.speak_text_and_transcribe()
