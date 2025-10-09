# test_stt.py
# =================
# This script tests speech-to-text (STT) functionality.
# It records a few seconds of microphone audio, transcribes it using Whisper,
# and then speaks the result using Piper TTS.

import os
import sys
import tempfile
import time
import wave
import numpy as np
import sounddevice as sd
import whisper
# 🔧 Add Buddy Core root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audio_controller import AudioController
import subprocess



# === Configuration ===
SAMPLE_RATE = 16000      # 16 kHz sampling rate
CHANNELS = 1             # Mono audio input
DURATION = 7             # Seconds to record for STT test
MODEL_NAME = "base"      # Whisper model size; can use "tiny", "small", "base", "medium", "large"

# === Helper: Generate and play beep using system audio ===
def play_beep(frequency=1000, duration=0.2):
    """
    Generate a short sine wave beep and play it using 'aplay'.
    Works reliably on Raspberry Pi without interfering with mic stream.
    """
    print(f"🔔 Playing beep ({frequency} Hz, {duration:.2f}s)")
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    tone = np.sin(2 * np.pi * frequency * t) * 0.5  # sine wave, volume 50%

    # Convert to 16-bit PCM and save to a temp WAV file
    beep_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with wave.open(beep_file.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((tone * 32767).astype(np.int16).tobytes())

    # Play the beep using aplay (blocking)
    subprocess.run(["aplay", "-q", beep_file.name])
    os.unlink(beep_file.name)  # cleanup

# === Audio Recording Function ===
def record_audio(filename, duration):
    """Record audio from microphone and save it as a WAV file."""
    print(f"🎙️ Recording {duration} seconds of speech...")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32"
    )
    sd.wait()

    wav_data = (audio * 32767).astype(np.int16)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(wav_data.tobytes())

    print(f"💾 Audio saved to {filename}")

# === Whisper STT Function ===
def transcribe_audio(filename):
    """Transcribe speech from a WAV file using Whisper."""
    print("🧠 Loading Whisper model...")
    model = whisper.load_model(MODEL_NAME)
    print("✅ Model loaded. Transcribing...")
    result = model.transcribe(filename)
    text = result.get("text", "").strip()
    return text

# === Piper TTS Function ===
def speak_result(text):
    """Speak the transcribed result using Piper TTS."""
    if text:
        message = f"You said: {text}"
        print(f"🔊 Speaking: {message}")
        try:
            AudioController().speak(message)
        except Exception as e:
            print(f"⚠️ TTS error: {e}")
    else:
        print("❌ No speech detected.")
        AudioController().speak("I could not hear anything.")

# === Main Function ===
def main():
    """
    Main STT test sequence:
      1. Announce test start via TTS
      2. Beep to start recording
      3. Record audio
      4. Beep to end recording
      5. Transcribe and speak result
    """
    AudioController().speak("Starting speech to text test. Please say something after the first beep.")
    time.sleep(1)

    # 🔔 Start beep
    play_beep(1000, 0.25)
    time.sleep(0.1)

    # 🎙️ Record speech
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        record_audio(tmpfile.name, DURATION)

        # 🛑 End beep
        play_beep(800, 0.3)

        # 🧠 Transcribe and 🔊 Speak
        text = transcribe_audio(tmpfile.name)
        print(f"📝 Transcribed text: {text}")
        speak_result(text)

    print("✅ STT test completed.")

# === Entry Point ===
if __name__ == "__main__":
    main()
