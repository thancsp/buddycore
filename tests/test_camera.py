# tests/test_camera.py
# ====================
# This script tests the camera and TTS.
# Captures a frame from the default camera, adds a timestamp,
# saves the image, speaks a notification via Piper TTS, and shows the image.

import sys
import os
import subprocess   # To run Piper TTS and aplay
import cv2           # OpenCV for image capture and display
from datetime import datetime
from threading import Thread
import time

# 🔧 Add Buddy Core root to Python path
# This allows imports like 'from camera_manager import CameraManager'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from camera_manager import CameraManager  # Custom camera handler

# Set DISPLAY for desktop if running headlessly (e.g., via SSH)
if not os.environ.get("DISPLAY"):
    os.environ["DISPLAY"] = ":0"  # Adjust if desktop uses a different display

# === Piper TTS Function ===
def speak(text):
    """
    Speak a given text via Piper TTS concurrently using a daemon thread.
    Prepends a space to prevent first word cutoff.
    """
    def run_piper(tts_text):
        # Path to pre-trained Piper TTS ONNX model
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  "models/piper_models/en_US-hfc_female-medium.onnx")
        try:
            # Start Piper process to generate raw PCM audio
            piper = subprocess.Popen(
                ["piper", "--model", model_path, "--output-raw"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            # Pipe Piper output to aplay to play sound
            aplay = subprocess.Popen(
                ["aplay", "-f", "S16_LE", "-r", "22050", "-c", "1"],
                stdin=piper.stdout
            )
            time.sleep(0.1)  # Give Piper a moment to initialize
            piper.stdin.write((" " + tts_text).encode())  # Prepend space
            piper.stdin.flush()
            piper.stdin.close()  # Signal Piper no more input
            aplay.wait()         # Wait for audio to finish
        except Exception as e:
            print(f"❌ Piper TTS error: {e}")

    # Run TTS in background thread so it doesn't block the main program
    Thread(target=run_piper, args=(text,), daemon=True).start()

# === Main Camera Test ===
def main():
    cam = CameraManager()      # Initialize camera
    frame = cam.get_frame()    # Capture one frame

    if frame is not None:
        # Add timestamp overlay to image
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        labeled_frame = frame.copy()  # Copy to preserve original frame
        label_text = f"Buddy Core Camera Test - {timestamp}"
        cv2.putText(labeled_frame, label_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Save image with fixed filename
        filename = "test_frame.jpg"
        cv2.imwrite(filename, labeled_frame)
        print(f"✅ Frame captured and saved as {filename}")

        # Prepare TTS message to notify user
        tts_text = (
            "Buddy Core has finished testing test_camera.py. "
            "A captured image file has been created in the Buddy Core root directory. "
            "The file is opened on the screen labeled Buddy Core Camera Test. "
            "It will be closed automatically."
        )
        speak(tts_text)  # Non-blocking, runs concurrently

        # Show the image if desktop DISPLAY is available
        if os.environ.get("DISPLAY"):
            cv2.imshow("Buddy Core Camera Test", labeled_frame)
            cv2.waitKey(15000)  # Display for 15 seconds
            cv2.destroyAllWindows()
    else:
        # Capture failed
        print("❌ Failed to capture frame")
        speak("Buddy Core failed to capture a frame during test_camera.py.")

# === Script Entry Point ===
if __name__ == "__main__":
    main()
