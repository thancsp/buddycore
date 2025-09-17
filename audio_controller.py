"""
Audio Controller: speaks alerts via Bluetooth speaker.
"""

import subprocess

class AudioController:
    def __init__(self, voice="en+f1"):
        self.voice = voice

    def speak(self, text):
        subprocess.run(["espeak", "-v", self.voice, text])
