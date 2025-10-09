"""
Buddy Core - Test Detector Module
Captures a full-resolution frame, runs YOLOv11 ONNX detection, announces detected objects via Piper TTS,
and displays the annotated image for 15 seconds.
"""

import os
import sys
import time
import threading
import subprocess  # For running external commands like xdg-open or feh
import cv2         # OpenCV for image saving and manipulation
from picamera2 import Picamera2  # Picamera2 for Raspberry Pi camera control
from ultralytics import YOLO      # YOLOv11 ONNX detection

# 🔧 Add Buddy Core root to Python path
# Allows importing local modules like AudioController
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audio_controller import AudioController  # TTS handler

# === Output file and YOLO model path ===
OUTPUT_FILE = "test_detector.jpg"
MODEL_PATH = "models/yolo11/yolo11n.onnx"

# Load YOLOv11 ONNX model for object detection
print("🔄 Loading YOLOv11 ONNX model...")
model = YOLO(MODEL_PATH, task="detect")  # task="detect" ensures detection mode
print("✅ Model loaded successfully")

# === Initialize camera for full wide-screen capture ===
picam2 = Picamera2()
# Full-resolution wide-frame (example: 4603x2592)
picam2.configure(picam2.create_still_configuration(main={"size": (4603, 2592)}))
picam2.start()
time.sleep(1)  # Allow sensor to warm up
frame = picam2.capture_array()  # Capture image as numpy array
picam2.close()
print("✅ Captured full-frame wide image using Picamera2")

# === Run YOLO detection on captured frame ===
results = model.predict(source=frame, save=False, show=False)  # Run detection
annotated_frame = results[0].plot()  # Draw bounding boxes on image
cv2.imwrite(OUTPUT_FILE, annotated_frame)  # Save annotated image
print(f"✅ Detection complete. Saved as {OUTPUT_FILE}")

# === Extract detected object names ===
names = results[0].names  # Class names dictionary
detected = [names[int(cls)] for cls in results[0].boxes.cls] if len(results[0].boxes) > 0 else []

# Prepare TTS message based on detection
if detected:
    detected_str = ", ".join(set(detected))  # Unique detected objects
    tts_text = (f"Buddy Core has detected the following objects: {detected_str}. ")
else:
    tts_text = ("Buddy Core has finished testing object detection. "
                "No recognizable objects were found.")

# === Display the image for 15 seconds ===
def show_image():
    """Open captured image automatically depending on environment"""
    image_path = os.path.abspath(OUTPUT_FILE)
    print(f"🖼️ Attempting to display image: {image_path}")

    if os.environ.get("DISPLAY"):
        # Desktop environment available, use default image viewer
        try:
            subprocess.run(["xdg-open", image_path])
        except Exception as e:
            print(f"⚠️ Could not open image with xdg-open: {e}")
    else:
        # Headless: try feh if installed
        if subprocess.run(["which", "feh"], capture_output=True).returncode == 0:
            try:
                subprocess.run(["feh", "-F", "-t", "-Y", image_path])
            except Exception as e:
                print(f"⚠️ Could not open image with feh: {e}")
        else:
            print("⚠️ No DISPLAY or feh available. Skipping image display.")
            return

    # Keep displayed for 15 seconds
    time.sleep(15)
    # Close the image automatically after 15 seconds
    subprocess.run(["pkill", "-f", OUTPUT_FILE])

# === Speak detection results using Piper TTS concurrently ===
def speak_message():
    """Announce detected objects via TTS"""
    time.sleep(0.1)  # Small delay to avoid cutting off first word
    print(f"🔊 Speaking: {tts_text}")
    AudioController().speak(tts_text)

# === Run TTS and image display concurrently ===
t1 = threading.Thread(target=speak_message)
t2 = threading.Thread(target=show_image)
t1.start()
t2.start()
t1.join()
t2.join()

print("✅ test_detector.py completed successfully")
