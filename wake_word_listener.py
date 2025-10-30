# wake_word_listener.py
# ====================
# Buddy Core - Single Detection Wake Word Listener using Porcupine
# -------------------------------------------------
# Listens for the configured wake word and provides detection feedback.

# ==================
# Imports
# ==================
import queue           # Thread-safe FIFO queue, used to store captured audio frames for processing
import numpy as np     # For numerical operations and array manipulations (audio buffers)
import sounddevice as sd  # Library for capturing microphone audio in real-time
import pvporcupine     # Porcupine wake word engine by Picovoice

# Internal imports
from audio_controller import AudioController  # TTS module for announcing detected wake word
from config import (                           # Import configuration constants
    WAKEWORD_TRIGGER,       # The word that triggers wake word detection (string)
    PORCUPINE_ACCESS_KEY,   # API key for Porcupine service
    PORCUPINE_KEYWORD_PATH, # Path to the Porcupine keyword file (.ppn)
    WAKEWORD_SAMPLE_RATE,   # Microphone sample rate in Hz
    WAKEWORD_CHANNELS,      # Number of microphone channels
)

# ==================
# Class Definition
# ==================
class WakeWordListener:
    """
    Listens for a wake word using Porcupine.
    
    === Methods Summary ===
    speak_alert(): Announces wake word via TTS.
    audio_callback(indata, frames, time_info, status): Queues captured audio.
    run_once(): Blocking call, listens for wake word once, speaks alert.
    detected(): Blocking wait, returns True when wake word detected, no TTS.
    detected_nonblocking(timeout): Non-blocking check for wake word detection.

    === Instance Variables ===
    self.audio: AudioController instance for TTS.
    self.audio_queue: Queue for storing audio frames.
    self.porcupine: Porcupine engine instance.
    self.buffer: Concatenated audio buffer for fixed-length frame processing.
    self.stream: sounddevice InputStream instance.
    """

    # ==================
    # Initialization
    # ==================
    def __init__(self, audio_controller=None):
        """Initialize WakeWordListener."""
        print("🔹 Initializing WakeWordListener")
        # Use provided AudioController or create a default one
        self.audio = audio_controller if audio_controller else AudioController()
        # Queue for storing microphone audio frames
        self.audio_queue = queue.Queue()
        # Placeholder for Porcupine engine instance (will initialize later)
        self.porcupine = None
        # Buffer for accumulating audio until a full frame is ready
        self.buffer = np.zeros((0,), dtype=np.int16)
        # Placeholder for sounddevice microphone stream
        self.stream = None

    # ==================
    # TTS Alert
    # ==================
    def speak_alert(self):
        """Speak TTS message indicating wake word detected."""
        # Build message string using configured wake word
        message = f"Wake word '{WAKEWORD_TRIGGER}' detected."
        print(f"🔊 Speaking alert: {message}")
        try:
            # Speak message using AudioController
            self.audio.speak(message)
        except Exception as e:
            print(f"⚠️ TTS error: {e}")

    # ==================
    # Audio Callback
    # ==================
    def audio_callback(self, indata, frames, time_info, status):
        """
        Callback for sounddevice InputStream.
        Arguments:
            indata: numpy array of captured audio frames
            frames: number of frames captured
            time_info: dictionary with timing info from stream
            status: Stream status flag (warnings/errors)
        """
        if status:  # If sounddevice reports an issue, log it
            print(f"⚠️ Audio stream status: {status}")
        # Add a copy of the audio data to the queue for main processing
        self.audio_queue.put(indata.copy())

    # ==================
    # Blocking Detection
    # ==================
    def run_once(self):
        """
        Blocking call: listens for wake word once, speaks alert, and exits.

        Steps:
        1. Initialize Porcupine engine.
        2. Open microphone stream.
        3. Collect audio frames in a buffer.
        4. Process buffer in fixed-length frames.
        5. Trigger TTS alert on detection.
        """
        print(f"🎧 Setting up Porcupine for wake word '{WAKEWORD_TRIGGER}'...")
        # Initialize Porcupine engine with API key and keyword file
        self.porcupine = pvporcupine.create(
            access_key=PORCUPINE_ACCESS_KEY,
            keyword_paths=[PORCUPINE_KEYWORD_PATH]
        )
        frame_length = self.porcupine.frame_length  # Number of samples per Porcupine frame
        print("✅ Porcupine initialized successfully")

        # Open microphone stream using sounddevice
        with sd.InputStream(
            samplerate=WAKEWORD_SAMPLE_RATE,  # Set sample rate
            blocksize=512,                    # Chunk size for callback
            dtype='float32',                  # Microphone audio format
            channels=WAKEWORD_CHANNELS,       # Number of channels
            callback=self.audio_callback      # Provide callback to enqueue frames
        ):
            print("🎙️ Listening for wake word... (blocking)")
            detected = False  # Flag to indicate detection

            while not detected:  # Keep listening until detection
                try:
                    # Wait for next audio chunk (0.5s timeout)
                    data = self.audio_queue.get(timeout=0.5)
                except queue.Empty:  # No data in queue
                    continue

                # Convert float32 [-1,1] audio to int16 [-32768,32767]
                audio_data = (data.flatten() * 32768).astype(np.int16)
                # Append audio data to buffer
                self.buffer = np.concatenate((self.buffer, audio_data))

                # Process fixed-length frames for Porcupine
                while len(self.buffer) >= frame_length:
                    frame = self.buffer[:frame_length]           # Take first frame
                    self.buffer = self.buffer[frame_length:]    # Remove processed frame
                    if self.porcupine.process(frame) >= 0:     # Detection occurs
                        print("✅ Wake word detected!")
                        detected = True
                        self.speak_alert()                      # Announce via TTS
                        break

        # Cleanup Porcupine engine after use
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
        print("🛑 Wake word listener exited after single detection.")

    # ==================
    # Blocking Detection Without TTS
    # ==================
    def detected(self):
        """
        Blocking call for background threads.
        Waits until wake word detected, returns True.
        TTS is suppressed during detection.
        """
        try:
            # Temporarily replace TTS method with no-op
            if hasattr(self, "speak_alert"):
                original_speak_alert = self.speak_alert
                self.speak_alert = lambda *a, **kw: None

            # Run detection once (blocking)
            self.run_once()

            # Restore original TTS method
            if hasattr(self, "speak_alert"):
                self.speak_alert = original_speak_alert

            return True
        except Exception as e:
            print(f"❌ Detection error: {e}")
            return False

    # ==================
    # Non-Blocking Detection
    # ==================
    def detected_nonblocking(self, timeout=0.1):
        """
        Non-blocking check for wake word.
        Returns True if detected, False otherwise.
        """
        # Initialize Porcupine engine and stream if not already
        if not self.porcupine:
            self.porcupine = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY,
                keyword_paths=[PORCUPINE_KEYWORD_PATH]
            )
            self.audio_queue = queue.Queue()  # Reset queue
            self.stream = sd.InputStream(
                samplerate=WAKEWORD_SAMPLE_RATE,
                blocksize=512,
                dtype='float32',
                channels=WAKEWORD_CHANNELS,
                callback=self.audio_callback
            )
            self.stream.start()
            self.buffer = np.zeros((0,), dtype=np.int16)  # Reset buffer

        detected = False  # Flag for detection
        try:
            # Attempt to get audio chunk from queue within timeout
            data = self.audio_queue.get(timeout=timeout)
            audio_data = (data.flatten() * 32768).astype(np.int16)
            self.buffer = np.concatenate((self.buffer, audio_data))

            # Process buffer in frame-length slices
            while len(self.buffer) >= self.porcupine.frame_length:
                frame = self.buffer[:self.porcupine.frame_length]
                self.buffer = self.buffer[self.porcupine.frame_length:]
                if self.porcupine.process(frame) >= 0:  # Detection occurs
                    detected = True
                    break
        except queue.Empty:
            pass  # No new audio, return False

        return detected  # True if wake word detected, else False
