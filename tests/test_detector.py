# tests/test_object_detector.py
import sys
import os
import subprocess
import cv2
from datetime import datetime
from threading import Thread
import time

# Ensure Buddy Core modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from camera_manager import CameraManager
# from object_detector import ObjectDetector  # Uncomment when you have a model

# Set display for desktop if running via Pi Connect
if not os.environ.get("DISPLAY"):
    os.environ["DISPLAY"] = ":0"  # Adjust if your desktop uses a different display

def speak(text):
    """
    Use Piper TTS to speak a given text via aplay concurrently.
    Ensures the first word is not cut off.
    """
    def run_piper(tts_text):
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  "models/piper_models/en_US-hfc_female-medium.onnx")
        try:
            piper = subprocess.Popen(
                ["piper", "--model", model_path, "--output-raw"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            aplay = subprocess.Popen(
                ["aplay", "-f", "S16_LE", "-r", "22050", "-c", "1"],
                stdin=piper.stdout
            )
            time.sleep(0.1)  # Give Piper a moment to initialize
            piper.stdin.write((" " + tts_text).encode())
            piper.stdin.flush()
            piper.stdin.close()
            aplay.wait()
        except Exception as e:
            print(f"❌ Piper TTS error: {e}")

    Thread(target=run_piper, args=(text,), daemon=True).start()

def main():
    cam = CameraManager()
    frame = cam.get_frame()

    if frame is not None:
        # Add timestamp overlay
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        labeled_frame = frame.copy()
        label_text = f"Buddy Core Object Detector Test - {timestamp}"
        cv2.putText(labeled_frame, label_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Save image with fixed filename
        filename = "test_detector.jpg"
        cv2.imwrite(filename, labeled_frame)
        print(f"✅ Frame captured and saved as {filename}")

        # TTS message
        tts_text = (
            "Buddy Core has finished testing object_detector.py. "
            "No model is currently loaded, so no objects were detected. "
            "A test image has been created in the Buddy Core root directory. "
            "It will be closed automatically."
        )
        speak(tts_text)

        # Show image on desktop if available
        if os.environ.get("DISPLAY"):
            cv2.imshow("Buddy Core Object Detector Test", labeled_frame)
            cv2.waitKey(15000)
            cv2.destroyAllWindows()
    else:
        print("❌ Failed to capture frame")
        speak("Buddy Core failed to capture a frame during test_object_detector.py.")

if __name__ == "__main__":
    main()
