# tests/test_detector.py
# ======================
# Buddy Core - YOLOv11 Object Detection Test
# -------------------------------------------------
# This script tests the object detection pipeline:
# 1. Captures a full-resolution frame using CameraManager
# 2. Runs YOLOv11 ONNX detection
# 3. Annotates and saves the detection image
# 4. Announces detected objects via Piper TTS


import os
import threading
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from object_detector import ObjectDetector  # Use the refactored class
from audio_controller import AudioController

# === Main Test Script ===
def main():
    # 🔹 Announce test start
    AudioController().speak(
        "Starting Buddy Core object detection test. "
        "Capturing a frame and detecting objects now."
    )

    # 🔹 Initialize the ObjectDetector
    detector = ObjectDetector()

    # 🔹 Run the full detection test (capture, detect, save, display, speak)
    detector.run_detection_test()

    print("✅ test_detector.py completed successfully")

# === Entry Point ===
if __name__ == "__main__":
    main()
