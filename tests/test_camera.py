# tests/test_camera.py
# ====================
# Buddy Core Camera Test
# ----------------------
# This script tests the Raspberry Pi camera and Buddy Core TTS.
# It:
#   1. Initializes the camera safely.
#   2. Captures a single frame.
#   3. Adds a timestamp overlay.
#   4. Saves the frame as 'test_frame.jpg'.
#   5. Announces the result via AudioController's Piper TTS.
#   6. Displays the image for 15 seconds (if DISPLAY is available).

import sys
import os
import cv2
from datetime import datetime


# 🔧 Add Buddy Core root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audio_controller import AudioController
from camera_manager import CameraManager  # Import updated CameraManager

# === Main Camera Test Function ===
def main():
    # Initialize camera
    cam = CameraManager()
    if cam.picam2 is None:
        msg = "❌ Camera failed to initialize. Test cannot proceed."
        print(msg)
        AudioController().speak(msg)
        return

    # Capture one frame
    frame = cam.get_frame()
    if frame is None:
        msg = "❌ Failed to capture frame."
        print(msg)
        AudioController().speak(msg)
        return

    # Add timestamp overlay
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    labeled_frame = frame.copy()  # Preserve original
    label_text = f"Buddy Core Camera Test - {timestamp}"
    cv2.putText(labeled_frame, label_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Save image
    filename = "test_frame.jpg"
    cv2.imwrite(filename, labeled_frame)
    print(f"✅ Frame captured and saved as {filename}")

    # Announce success via TTS
    tts_msg = (
        "Buddy Core has finished testing the camera. "
        f"The captured image is saved as {filename}."
    )
    AudioController().speak(tts_msg)

    # Display image if DISPLAY is set
    if os.environ.get("DISPLAY"):
        cv2.imshow("Buddy Core Camera Test", labeled_frame)
        cv2.waitKey(15000)  # Show for 15 seconds
        cv2.destroyAllWindows()

# === Script Entry Point ===
if __name__ == "__main__":
    main()
