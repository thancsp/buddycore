"""
Test Text-to-Speech output via AudioController.
"""

import sys, os
# 🔧 Add the project root (parent directory) to Python path
# This allows importing the local module `audio_controller` even if running from tests/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the custom AudioController class
from audio_controller import AudioController

# Create an instance of AudioController
tts = AudioController()

# Use Piper TTS to speak a test message
tts.speak(
    "This is a test of Buddy Core audio system. "
    "Hearing this voice means that Buddy Core is using text-to-speech from Piper TTS"
)
