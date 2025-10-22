# wake_word_listener.py
# ====================
# Buddy Core - Single Detection Wake Word Listener using Porcupine
# -------------------------------------------------
# Listens once for the configured wake word and announces detection via Piper TTS.

import queue
import numpy as np
import sounddevice as sd
import pvporcupine

from audio_controller import AudioController
from config import (
    WAKEWORD_TRIGGER,
    PORCUPINE_ACCESS_KEY,
    PORCUPINE_KEYWORD_PATH,
    WAKEWORD_SAMPLE_RATE,
    WAKEWORD_CHANNELS,
)


class WakeWordListener:
    """
    Listens for a single occurrence of the wake word using Porcupine.
    
    Methods
    -------
    speak_alert():
        Announces wake word detection via TTS.
    audio_callback(indata, frames, time_info, status):
        Collects audio samples from microphone and queues them.
    run_once():
        Listens until wake word is detected once, announces it, and quits.
    detected():
        Returns True if the wake word is detected once (used for external scripts).

    Variables
    ---------
    audio : AudioController
        Handles text-to-speech output.
    audio_queue : queue.Queue
        Thread-safe queue to store incoming microphone audio frames.
    porcupine : pvporcupine.Porcupine
        Porcupine engine instance for wake word detection.
    """

    def __init__(self, audio_controller=None):
        """Initialize listener and audio queue."""
        print("🔹 Initializing WakeWordListener")
        self.audio = audio_controller if audio_controller else AudioController()
        self.audio_queue = queue.Queue()
        self.porcupine = None

    def speak_alert(self):
        """Announce wake word detection via TTS."""
        message = f"Wake word '{WAKEWORD_TRIGGER}' detected."
        print(f"🔊 Speaking alert: {message}")
        try:
            self.audio.speak(message)
        except Exception as e:
            print(f"⚠️ TTS error: {e}")

    def audio_callback(self, indata, frames, time_info, status):
        """Microphone callback that queues captured audio."""
        if status:
            print(f"⚠️ Audio stream status: {status}")
        self.audio_queue.put(indata.copy())

    def run_once(self):
        """
        Start Porcupine engine and listen for wake word once.
        Prints progress at each step and announces detection via TTS.
        Exits after a single detection.
        """
        print(f"🎧 Setting up Porcupine for wake word '{WAKEWORD_TRIGGER}'...")
        self.porcupine = pvporcupine.create(
            access_key=PORCUPINE_ACCESS_KEY,
            keyword_paths=[PORCUPINE_KEYWORD_PATH]
        )
        frame_length = self.porcupine.frame_length
        print("✅ Porcupine initialized successfully")
        print("🎤 Opening microphone stream...")

        with sd.InputStream(
            samplerate=WAKEWORD_SAMPLE_RATE,
            blocksize=512,
            dtype='float32',
            channels=WAKEWORD_CHANNELS,
            callback=self.audio_callback
        ):
            print("🎙️ Listening for wake word... (will exit after detection)")
            buffer = np.zeros((0,), dtype=np.int16)
            detected = False

            while not detected:
                try:
                    data = self.audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                audio_data = (data.flatten() * 32768).astype(np.int16)
                buffer = np.concatenate((buffer, audio_data))

                while len(buffer) >= frame_length:
                    frame = buffer[:frame_length]
                    buffer = buffer[frame_length:]
                    if self.porcupine.process(frame) >= 0:
                        print("✅ Wake word detected!")
                        detected = True
                        self.speak_alert()
                        break

        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
        print("🛑 Wake word listener exited after single detection.")

    def detected(self):
        """
        Runs a single-pass detection cycle and returns True if the wake word is detected.
        Designed for use by external scripts (e.g., test_full_wakeword.py).
        """
        print("👂 Waiting for wake word detection (detected() mode)...")
        try:
            self.run_once()  # internally announces detection
            return True
        except Exception as e:
            print(f"❌ Detection error: {e}")
            return False


# === Main function for standalone test ===
def main():
    """Speak introduction, listen once for wake word, announce detection, then quit."""
    tts = AudioController()
    print("💬 TTS: Buddy Core wake word test starting...")
    tts.speak(
        "Buddy Core wake word test starting. "
        "Say 'Hey Buddy' once to trigger detection."
    )

    listener = WakeWordListener(audio_controller=tts)
    listener.run_once()

    print("💬 TTS: Wake word test completed. Goodbye.")
    tts.speak("Wake word test completed. Goodbye.")


# === Script entry point ===
if __name__ == "__main__":
    main()
