"""
BuddyCore Configuration
-----------------------
Centralized configuration file for all BuddyCore modules:
TTS, Camera, Object Detection, Wake Word, Speech-to-Text (STT), Risk Engine.
"""

import os
import platform
from pathlib import Path # enables you to directly create Path objects and call their methods without needing to prefix them with pathlib.In this case is to use '/' to append paths.

# ------------------------------------------------------------
# BASE DIRECTORIES
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

# ------------------------------------------------------------
# PLATFORM DETECTION
# ------------------------------------------------------------
SYSTEM = platform.system()
IS_RPI = (
    Path("/proc/device-tree/model").exists()
    and "Raspberry Pi" in open("/proc/device-tree/model").read()
)

# ------------------------------------------------------------
# CAMERA SETTINGS
# ------------------------------------------------------------
CAMERA_INDEX = 0  # default for OpenCV; ignored if using Picamera2
CAMERA_RESOLUTION = (4603, 2592)  # full-resolution for camera & detector tests
CAMERA_FPS = 20

# Camera test settings
CAMERA_TEST_FILENAME = BASE_DIR / "test_frame.jpg"
CAMERA_TEST_LABEL = "Buddy Core Camera Test"
CAMERA_DISPLAY_MS = 15000  # milliseconds
CAMERA_WARMUP_SEC = 1       # seconds to allow sensor to warm up

# ------------------------------------------------------------
# AUDIO / TTS SETTINGS
# ------------------------------------------------------------
# Using Python-based Piper TTS (installed via pip install piper-tts)
TTS_ENGINE = "piper_tts"
PIPER_MODEL = MODELS_DIR / "piper_models" / "en_US-hfc_female-medium.onnx"
PIPER_VOICE = "en_US-hfc_female-medium"
AUDIO_DEVICE_INDEX = None  # default device for playback

# ------------------------------------------------------------
# DETECTION SETTINGS
# ------------------------------------------------------------
YOLO_MODEL_PATH = MODELS_DIR / "yolo11" / "yolo11n.onnx"
DETECTION_CONFIDENCE = 0.5
HARZARDOUS_OBJECTS = ["person", "bicycle", "car", "bus", "truck"]
DETECTION_INTERVAL = 10# seconds interval of how often the main program's detector function will detect with the camera
# Detector test settings
DETECTOR_TEST_FILENAME = BASE_DIR / "test_detector.jpg"
DETECTOR_DISPLAY_SEC = 15  # seconds to show annotated image


# ------------------------------------------------------------
# WAKE WORD SETTINGS
# ------------------------------------------------------------
WAKEWORD_ENGINE = "porcupine"
PORCUPINE_MODEL_PATH = MODELS_DIR / "porcupine"
WAKEWORD_TRIGGER = ["hey buddy"]
PORCUPINE_ACCESS_KEY = "8sBtDjXViIrp/HFRNv6YeXJrgn7vVfHwQeGB6L6MjPYaFrpRX0EJMg=="
PORCUPINE_KEYWORD_PATH = PORCUPINE_MODEL_PATH / "Hey-buddy_en_raspberry-pi_v3_0_0.ppn"
WAKEWORD_SAMPLE_RATE = 16000  # Hz
WAKEWORD_CHANNELS = 1         # Mono

EXIT_PHRASES = ["shut down", "system shutdown", "system shut down"]

# ------------------------------------------------------------
# SPEECH-TO-TEXT (STT) SETTINGS
# ------------------------------------------------------------
STT_SAMPLE_RATE = 16000   # Hz
STT_CHANNELS = 1          # Mono audio input
STT_DURATION = 3          # Seconds to record for STT test
STT_MODEL_NAME = "base"   # Whisper model size ("tiny", "small", "base", "medium", "large")

# Beep signals for start/end of recording
STT_BEEP_START_FREQ = 1000  # Hz
STT_BEEP_START_DUR = 0.25   # seconds
STT_BEEP_END_FREQ = 800     # Hz
STT_BEEP_END_DUR = 0.3      # seconds

STT_TTS_START_MESSAGE = (
    "Starting speech to text test. Please say something after the first beep."
)

# ------------------------------------------------------------
# FULL WAKEWORD + STT TEST MESSAGES
# ------------------------------------------------------------
FULL_WAKEWORD_INTRO = (
    "Hello. This is Buddy Core full test. Say 'Hey Buddy' to start, "
    "and I’ll listen for seven seconds. Say 'shut down' to end testing."
)
FULL_WAKEWORD_ACK = "Hey, I’m listening."
FULL_WAKEWORD_ABORT = "Abort testing confirmed. Buddy Core is shutting down now."

# ------------------------------------------------------------
# LOGGING & DEBUG
# ------------------------------------------------------------
DEBUG = True
VERBOSE = True


def debug_log(message: str):
    """Utility function for consistent debug printing."""
    if DEBUG:
        print(f"[DEBUG] {message}")


# ------------------------------------------------------------
# SYSTEM PATH CHECKS
# ------------------------------------------------------------
def validate_paths():
    """Ensure required model paths exist."""
    missing = []
    if not PIPER_MODEL.exists():
        missing.append(str(PIPER_MODEL))
    if not YOLO_MODEL_PATH.exists():
        missing.append(str(YOLO_MODEL_PATH))
    if not PORCUPINE_KEYWORD_PATH.exists():
        missing.append(str(PORCUPINE_KEYWORD_PATH))
    if missing:
        print("⚠️ Missing required model files:")
        for m in missing:
            print("   -", m)
    else:
        print("✅ All model paths verified.")


# ------------------------------------------------------------
# TEST HOOK
# ------------------------------------------------------------
if __name__ == "__main__":
    summary_lines = [
        "BuddyCore Configuration Summary:",
        f"Base Dir: {BASE_DIR}",
        f"Is Raspberry Pi: {IS_RPI}",
        f"TTS Engine: {TTS_ENGINE}",
        f"TTS Model: {PIPER_MODEL.name}",
        f"Camera: {CAMERA_INDEX}, {CAMERA_RESOLUTION}",
        f"Camera test file: {CAMERA_TEST_FILENAME}",
        f"Detector test file: {DETECTOR_TEST_FILENAME}",
        f"Wake-word keywords: {WAKEWORD_TRIGGER}",
        f"STT model: {STT_MODEL_NAME}, Duration: {STT_DURATION} seconds"
    ]

    # Print summary
    for line in summary_lines:
        print(line)

    # Validate model paths
    validate_paths()

    # 🔊 Speak summary via Piper TTS
    try:
        from audio_controller import AudioController
        tts = AudioController()
        tts.speak("Buddy Core Configuration Summary. " + " ".join(summary_lines))
    except Exception as e:
        print(f"⚠️ TTS error while announcing configuration: {e}")
