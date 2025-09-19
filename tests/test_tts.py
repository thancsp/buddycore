"""
Test Text-to-Speech output via AudioController.
"""

import sys, os
# Add parent directory (project root) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_controller import AudioController

tts = AudioController()
tts.speak("This is a test of Buddy Core audio system. Hearing this voice means that Buddy Core is using text-to-speech from Piper TTS")
