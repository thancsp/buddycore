# test_wakeword.py
# =================
# This script tests the Porcupine wake-word detection engine ("Hey Buddy").
# When the wake word is detected, Buddy Core will announce it via TTS
# and terminate the program cleanly.

import os
import sys
import queue
import sounddevice as sd
import numpy as np
import pvporcupine

# 🔧 Add Buddy Core root directory to the Python import path
#    so that 'audio_controller' and other modules can be imported directly.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audio_controller import AudioController


# === Configuration ===
WAKE_WORD = "Hey Buddy"  # Name of the wake word
ACCESS_KEY = "8sBtDjXViIrp/HFRNv6YeXJrgn7vVfHwQeGB6L6MjPYaFrpRX0EJMg=="  # Picovoice access key (for Porcupine)
KEYWORD_PATH = "/home/ladmin/buddycore/models/porcupine/Hey-buddy_en_raspberry-pi_v3_0_0.ppn"  # Path to the wake word model
SAMPLE_RATE = 16000  # Audio sampling rate in Hz
CHANNELS = 1         # Number of audio channels (mono)

# === Global Queue ===
# A thread-safe queue used to pass audio chunks from the microphone callback
# to the Porcupine processing loop.
audio_queue = queue.Queue()


def speak_alert():
    """Announce that the wake word was detected, then exit the program."""
    message = f"Wake word detected! Buddy Core is ending test_wakeword.py."
    print(f"🔊 Speaking: {message}")
    try:
        AudioController().speak(message)
    except Exception as e:
        print(f"⚠️ TTS error: {e}")
    finally:
        print("🛑 Exiting test_wakeword.py")
        os._exit(0)


def speak_intro():
    """Introduce the test and explain what will happen."""
    intro_message = (
        "This is the Buddy Core wake word detection test. "
        "Please say 'Hey Buddy' when you are ready. "
        "Buddy Core will announce detection and end the test."
    )
    print(f"🔊 Introduction: {intro_message}")
    try:
        AudioController().speak(intro_message)
    except Exception as e:
        print(f"⚠️ TTS intro error: {e}")


def audio_callback(indata, frames, time_info, status):
    """Capture incoming microphone audio stream."""
    if status:
        print(status)
    audio_queue.put(indata.copy())


def wakeword_listener():
    """Continuously check microphone input for the wake word using Porcupine."""
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[KEYWORD_PATH]
    )
    frame_length = porcupine.frame_length
    print(f"🎧 Listening for wake word '{WAKE_WORD}'...")

    buffer = np.zeros((0,), dtype=np.int16)

    while True:
        data = audio_queue.get()
        audio_data = (data.flatten() * 32768).astype(np.int16)
        buffer = np.concatenate((buffer, audio_data))

        while len(buffer) >= frame_length:
            frame = buffer[:frame_length]
            buffer = buffer[frame_length:]
            keyword_index = porcupine.process(frame)
            if keyword_index >= 0:
                speak_alert()


if __name__ == "__main__":
    # 🎙️ Speak an introduction before starting the test
    speak_intro()

    # Open the microphone stream
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=512,
        dtype="float32",
        channels=CHANNELS,
        callback=audio_callback
    ):
        wakeword_listener()
