# wake_word_listener.py
# ====================
# Buddy Core - Single Detection Wake Word Listener using Porcupine
# -------------------------------------------------
# Listens for the configured wake word and provides detection feedback.

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
    Listens for wake word using Porcupine.

    Methods
    -------
    speak_alert()
        Announces wake word via TTS.
    audio_callback(indata, frames, time_info, status)
        Queues incoming audio frames.
    run_once()
        Blocks until wake word detected once.
    detected()
        Blocks until wake word is detected, returns True, no TTS.
    detected_nonblocking(timeout)
        Checks for wake word in non-blocking mode (returns True/False).
    """

    def __init__(self, audio_controller=None):
        """Initialize listener and audio queue."""
        print("🔹 Initializing WakeWordListener")
        self.audio = audio_controller if audio_controller else AudioController()
        self.audio_queue = queue.Queue()
        self.porcupine = None
        self.buffer = np.zeros((0,), dtype=np.int16)
        self.stream = None

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
        Blocking call: listens for wake word once, speaks alert, and returns.
        """
        print(f"🎧 Setting up Porcupine for wake word '{WAKEWORD_TRIGGER}'...")
        self.porcupine = pvporcupine.create(
            access_key=PORCUPINE_ACCESS_KEY,
            keyword_paths=[PORCUPINE_KEYWORD_PATH]
        )
        frame_length = self.porcupine.frame_length
        print("✅ Porcupine initialized successfully")

        with sd.InputStream(
            samplerate=WAKEWORD_SAMPLE_RATE,
            blocksize=512,
            dtype='float32',
            channels=WAKEWORD_CHANNELS,
            callback=self.audio_callback
        ):
            print("🎙️ Listening for wake word... (blocking)")
            detected = False

            while not detected:
                try:
                    data = self.audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                audio_data = (data.flatten() * 32768).astype(np.int16)
                self.buffer = np.concatenate((self.buffer, audio_data))

                while len(self.buffer) >= frame_length:
                    frame = self.buffer[:frame_length]
                    self.buffer = self.buffer[frame_length:]
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
        Blocking call for background thread:
        Waits until wake word detected, returns True.
        Suppresses TTS during detection.
        """
        try:
            if hasattr(self, "speak_alert"):
                original_speak_alert = self.speak_alert
                self.speak_alert = lambda *a, **kw: None

            self.run_once()

            if hasattr(self, "speak_alert"):
                self.speak_alert = original_speak_alert

            return True
        except Exception as e:
            print(f"❌ Detection error: {e}")
            return False

    def detected_nonblocking(self, timeout=0.1):
        """
        Non-blocking check for wake word.
        Returns True if detected, False otherwise.
        """
        if not self.porcupine:
            self.porcupine = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY,
                keyword_paths=[PORCUPINE_KEYWORD_PATH]
            )
            self.audio_queue = queue.Queue()
            self.stream = sd.InputStream(
                samplerate=WAKEWORD_SAMPLE_RATE,
                blocksize=512,
                dtype='float32',
                channels=WAKEWORD_CHANNELS,
                callback=self.audio_callback
            )
            self.stream.start()
            self.buffer = np.zeros((0,), dtype=np.int16)

        detected = False
        try:
            data = self.audio_queue.get(timeout=timeout)
            audio_data = (data.flatten() * 32768).astype(np.int16)
            self.buffer = np.concatenate((self.buffer, audio_data))
            while len(self.buffer) >= self.porcupine.frame_length:
                frame = self.buffer[:self.porcupine.frame_length]
                self.buffer = self.buffer[self.porcupine.frame_length:]
                if self.porcupine.process(frame) >= 0:
                    detected = True
                    break
        except queue.Empty:
            pass

        return detected
