"""
audio_controller.py
Handles text-to-speech output for Buddy Core using Piper TTS.
"""

import os
import subprocess


class AudioController:
    def __init__(self, model_path="models/piper_models/en_US-hfc_female-medium.onnx"):
        # Store the model path (relative to project root)
        self.model_path = os.path.abspath(model_path)

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Piper model not found at {self.model_path}")

    def speak(self, text: str):
        """
        Generate speech using Piper TTS and play through default audio output.
        Piper outputs raw WAV which we stream directly to 'aplay'.
        """
        try:
            process = subprocess.Popen(
                ["piper", "--model", self.model_path, "--output-raw"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            play = subprocess.Popen(
                ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"],
                stdin=process.stdout
            )
            process.stdin.write(text.encode("utf-8"))
            process.stdin.close()
            process.wait()
            play.wait()

        except Exception as e:
            print(f"[AudioController] Piper TTS error: {e}")
