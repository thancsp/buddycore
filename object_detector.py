# object_detector.py
# ==================
# Buddy Core Object Detector using YOLOv11 ONNX
# -------------------------------------------------
# Provides object detection on frames captured from CameraManager
# and optional TTS announcements using AudioController.
#
# === Methods Summary ===
# - __init__(): Initializes YOLO model, camera, and output file path.
# - detect_frame(): Captures a frame, runs YOLO detection, annotates, and saves image.
# - speak_detections(detected_labels): Announces detected objects via TTS.
# - run_detection_test(): Full detection test that captures frame, detects, displays, and speaks results.
#
# === Instance Variables ===
# - self.model: YOLOv11 ONNX detection model.
# - self.cam: CameraManager instance for capturing frames.
# - self.output_file: Filename for saving annotated detection image.

import os
import cv2
import time
import threading
import subprocess
from ultralytics import YOLO  # YOLOv11 ONNX detection

from config import CAMERA_RESOLUTION, DETECTOR_TEST_FILENAME, YOLO_MODEL_PATH
from audio_controller import AudioController
from camera_manager import CameraManager


class ObjectDetector:
    """
    Handles YOLOv11 object detection for Buddy Core.
    """

    def __init__(self):
        # 🔹 Load YOLOv11 ONNX model from the path specified in config
        print(f"🔄 Loading YOLOv11 ONNX model from {YOLO_MODEL_PATH}...")
        self.model = YOLO(YOLO_MODEL_PATH, task="detect")  # task="detect" ensures detection mode
        print("✅ YOLOv11 model loaded successfully")

        # 🔹 Initialize CameraManager with resolution from config
        try:
            self.cam = CameraManager(resolution=CAMERA_RESOLUTION)
        except Exception as e:
            print(f"❌ Failed to initialize camera: {e}")
            self.cam = None  # Mark camera as unavailable if init fails

        # 🔹 Set output file for annotated detection image
        self.output_file = DETECTOR_TEST_FILENAME

    def detect_frame(self):
        """
        Capture a frame, run YOLOv11 detection, annotate it, and save.
        
        Returns:
            annotated_frame (numpy array): Frame with bounding boxes drawn
            detected_labels (list of str): Names of detected objects
        """
        # 🔹 Ensure camera is available
        if not self.cam:
            print("❌ Camera not available.")
            return None, []

        # 🔹 Capture a frame from the camera
        frame = self.cam.get_frame()
        if frame is None:
            print("❌ Failed to capture frame")
            return None, []

        # 🔹 Run YOLOv11 detection on the captured frame
        results = self.model.predict(source=frame, save=False, show=False)
        annotated_frame = results[0].plot()  # Draw bounding boxes
        cv2.imwrite(self.output_file, annotated_frame)  # Save annotated frame to file

        # 🔹 Extract detected object names from the YOLO result
        names = results[0].names
        detected_labels = [names[int(cls)] for cls in results[0].boxes.cls] if len(results[0].boxes) > 0 else []

        print(f"✅ Detection complete. Saved as {self.output_file}")
        return annotated_frame, detected_labels

    def speak_detections(self, detected_labels):
        """
        Announce detected objects via AudioController (Piper TTS).
        
        Args:
            detected_labels (list of str): List of detected object names
        """
        # 🔹 Prepare TTS message based on detection results
        if detected_labels:
            detected_str = ", ".join(set(detected_labels))  # List unique objects
            tts_text = f"Buddy Core has detected the following objects: {detected_str}."
        else:
            tts_text = "Buddy Core has finished object detection. No recognizable objects were found."

        # 🔹 Run TTS in background thread to avoid blocking main program
        def tts_thread():
            AudioController().speak(tts_text)

        threading.Thread(target=tts_thread, daemon=True).start()

    def run_detection_test(self):
        """
        Full detection test:
        1. Capture a frame
        2. Run YOLO detection
        3. Annotate and save image
        4. Display image
        5. Announce detections via TTS
        """
        # 🔹 Detect objects in a frame
        annotated_frame, detected = self.detect_frame()
        if annotated_frame is None:
            return  # Stop if capture failed

        # 🔹 Display image (desktop environment or headless fallback)
        def show_image():
            image_path = os.path.abspath(self.output_file)
            print(f"🖼️ Attempting to display image: {image_path}")
            try:
                # If desktop DISPLAY available, use OpenCV
                if os.environ.get("DISPLAY"):
                    cv2.imshow("Buddy Core Object Detection", annotated_frame)
                    cv2.waitKey(15000)  # Display for 15 seconds
                    cv2.destroyAllWindows()
                # Headless: try 'feh' image viewer if installed
                elif subprocess.run(["which", "feh"], capture_output=True).returncode == 0:
                    subprocess.run(["feh", "-F", "-t", "-Y", image_path])
                    time.sleep(15)
                    subprocess.run(["pkill", "-f", self.output_file])
                else:
                    print("⚠️ No DISPLAY or feh available. Skipping image display.")
            except Exception as e:
                print(f"⚠️ Failed to display image: {e}")

        # 🔹 Run TTS and image display concurrently
        t1 = threading.Thread(target=self.speak_detections, args=(detected,))
        t2 = threading.Thread(target=show_image)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        print("✅ Object detection test completed successfully")


# 🔹 Example usage
if __name__ == "__main__":
    detector = ObjectDetector()
    detector.run_detection_test()
