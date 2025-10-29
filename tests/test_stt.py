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
from config import STT_DURATION

ac = AudioController()
# This method will handle TTS intro, beep, recording, transcription, and speaking result
ac.speak(f"This is the Speech to text test from the file test_STT.py. This will listen to you for {STT_DURATION} seconds then transform what you say into text and then say it out. Please speak after the beep.")

text = ac.speak_text_and_transcribe()
