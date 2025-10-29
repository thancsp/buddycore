"""
audio_controller.py
===================
Buddy Core AudioController

Provides interruptible text-to-speech (TTS) via Piper TTS
and speech-to-text (STT) via Whisper. Configurable
using parameters from config.py.
"""

import os
import subprocess
import tempfile
import time
import numpy as np
import sounddevice as sd
import wave
import whisper

# Load configuration variables
from config import (
    PIPER_MODEL,         # Piper TTS model ONNX file
    STT_MODEL_NAME,      # Whisper model name
    STT_SAMPLE_RATE,     # Microphone sample rate for STT
    STT_CHANNELS,        # Microphone channels for STT
    STT_DURATION         # Default recording duration for STT
)


class AudioController:
    """
    === Methods Summary ===
    speak(text): Convert text to speech using Piper TTS (interruptible).
    stop_speech(): Immediately stops any ongoing TTS playback.
    play_beep(frequency, duration): Play a sine-wave beep.
    record_audio(filename, duration): Record microphone audio to WAV.
    transcribe_audio(filename): Convert recorded audio to text using Whisper.
    speak_text_and_transcribe(): Convenience method for full STT test.

    === Variables ===
    model_path: absolute path to Piper TTS model
    stt_model: cached Whisper model
    sample_rate: audio input sampling rate for STT
    channels: audio input channels for STT
    duration: recording duration for STT
    current_process: reference to current Piper TTS process (for stopping)
    """

    def __init__(self, model_path=PIPER_MODEL):
        """Initialize AudioController and validate Piper TTS model path"""
        self.model_path = os.path.abspath(model_path)
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Piper model not found at {self.model_path}")

        # Whisper model cache (lazy loading)
        self.stt_model = None

        # Audio configuration for STT
        self.sample_rate = STT_SAMPLE_RATE
        self.channels = STT_CHANNELS
        self.duration = STT_DURATION

        # Reference to currently playing TTS process
        self.current_process = None

    # === Text-to-Speech (TTS) ===
    def speak(self, text: str):
        """Speak text aloud using Piper TTS (interruptible)"""
        try:
            # Start Piper subprocess
            self.current_process = subprocess.Popen(
                ["piper", "--model", self.model_path, "--output-raw"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            # Pipe Piper output to aplay
            play = subprocess.Popen(
                ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"],
                stdin=self.current_process.stdout
            )
            # Send text to Piper
            self.current_process.stdin.write(text.encode("utf-8"))
            self.current_process.stdin.close()
            self.current_process.wait()
            play.wait()
            self.current_process = None
        except Exception as e:
            print(f"[AudioController] Piper TTS error: {e}")
            self.current_process = None

    def stop_speech(self):
        """Immediately stop ongoing TTS playback"""
        try:
            if self.current_process and self.current_process.poll() is None:
                print("🛑 Stopping current speech...")
                self.current_process.terminate()  # gentler than kill()
                time.sleep(0.05)  # give the OS a moment
                self.current_process.kill()  # force stop if still alive
            self.current_process = None
        except Exception as e:
            print(f"[AudioController] stop_speech() error: {e}")
            self.current_process = None


    # === Beep Generator ===
    def play_beep(self, frequency=1000, duration=0.25):
        """Play a sine-wave beep using sounddevice"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = np.sin(2 * np.pi * frequency * t) * 0.5
        beep_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        # Save to temporary WAV file
        with wave.open(beep_file.name, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes((tone * 32767).astype(np.int16).tobytes())
        subprocess.run(["aplay", "-q", beep_file.name])
        os.unlink(beep_file.name)

    # === Audio Recording ===
    def record_audio(self, filename, duration=None):
        """Record microphone audio and save to WAV file"""
        if duration is None:
            duration = self.duration
        print(f"🎙️ Recording {duration}s of audio...")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32"
        )
        sd.wait()
        wav_data = (audio * 32767).astype(np.int16)
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(wav_data.tobytes())
        print(f"💾 Audio saved to {filename}")

    # === Speech-to-Text (STT) ===
    def transcribe_audio(self, filename, model_name=STT_MODEL_NAME):
        """Transcribe speech from WAV file using Whisper"""
        if self.stt_model is None:
            print("🧠 Loading Whisper model...")
            self.stt_model = whisper.load_model(model_name)
            print("✅ Whisper model loaded")
        print("📝 Transcribing audio...")
        result = self.stt_model.transcribe(filename)
        text = result.get("text", "").strip()
        return text

    # === Convenience STT Flow ===
    def speak_text_and_transcribe(self):
        """Full STT test: beep -> record -> beep -> transcribe -> speak"""
        time.sleep(0.3)
        self.play_beep(1000, 0.25)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            self.record_audio(tmpfile.name)
            self.play_beep(800, 0.3)
            text = self.transcribe_audio(tmpfile.name)
            print(f"📝 Transcribed text: {text}")
            if text:
                self.speak(f"You said: {text}")
            else:
                self.speak("I could not hear anything.")
        return text


# === Entry Point Main ===
def main():
    """Run a full STT test with introduction and exit messages"""
    ac = AudioController()
    ac.speak("Hello! This is Buddy Core audio test. We will record your voice and convert it to text.")
    time.sleep(0.5)
    ac.speak_text_and_transcribe()
    ac.speak("Buddy Core audio test completed. Goodbye!")


# === Script Execution ===
if __name__ == "__main__":
    main()
