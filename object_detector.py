# object_detector.py
# ==================
# Buddy Core Object Detector using YOLOv11 ONNX
# -------------------------------------------------
# Provides object detection on frames captured from CameraManager
# and optional TTS announcements using AudioController.

# ==================
# Imports Explanation
# ==================
import os                # For filesystem operations (folders, file paths, deletion)
import cv2               # OpenCV library for image processing, drawing, annotation
import time              # Timing functions, e.g., sleep or timestamps
import threading         # To run TTS in a non-blocking background thread
import subprocess        # For running external programs like Piper TTS or aplay
from datetime import datetime  # To generate timestamped filenames and annotations
from ultralytics import YOLO    # YOLOv11 ONNX detection library

from config import CAMERA_RESOLUTION, DETECTOR_TEST_FILENAME, YOLO_MODEL_PATH  # Configurable parameters
from audio_controller import AudioController   # TTS functionality for speaking detections
from camera_manager import CameraManager       # Camera capture interface


class ObjectDetector:
    """
    Handles YOLOv11 object detection for Buddy Core.

    === Methods Summary ===
    __init__(): Initializes YOLO model, camera, and output file path.
    detect_frame(): Captures a frame, runs YOLO detection, annotates, and saves image.
    speak_detections(detected_labels): Announces detected objects via TTS.
    run_detection_test(): Full detection test that captures frame, detects, displays, and speaks results.

    === Instance Variables ===
    self.model: YOLOv11 ONNX detection model.
    self.cam: CameraManager instance for capturing frames.
    self.output_file: Filename for saving annotated detection image.
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
        Capture a frame, run YOLOv11 detection, annotate it with bounding boxes
        and current date/time, and save to OUTPUT folder.
        
        If there are 100 files in the OUTPUT folder, the oldest one is deleted.
        
        Returns:
            annotated_frame (numpy array): Frame with bounding boxes and timestamp
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

        # 🔹 Annotate with current date and time at top-left
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (0, 255, 0)  # Green
        thickness = 2
        cv2.putText(
            annotated_frame,
            timestamp,
            (10, 30),
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )

        # 🔹 Ensure OUTPUT folder exists
        output_dir = "OUTPUT"
        os.makedirs(output_dir, exist_ok=True)

        # 🔹 Check number of files in OUTPUT and remove oldest if ≥100
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.lower().endswith(".jpg")]
        if len(files) >= 100:
            oldest_file = min(files, key=os.path.getctime)
            try:
                os.remove(oldest_file)
                print(f"🧹 Removed oldest file: {os.path.basename(oldest_file)}")
            except Exception as e:
                print(f"⚠️ Could not remove oldest file: {e}")

        # 🔹 Save annotated frame with timestamped filename
        filename = f"[DETECTED]{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.jpg"
        self.output_file = os.path.join(output_dir, filename)
        cv2.imwrite(self.output_file, annotated_frame)

        # 🔹 Extract detected object names from YOLO result
        names = results[0].names
        detected_labels = [names[int(cls)] for cls in results[0].boxes.cls] if len(results[0].boxes) > 0 else []

        print(f"✅ Detection complete. Saved as {filename}")
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
            tts_text = f"{detected_str} detected."
        else:
            tts_text = "Nothing is detected."

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
        
        self.speak_detections(detected)

        print("✅ Object detection test completed successfully")


# 🔹 Example usage
if __name__ == "__main__":
    detector = ObjectDetector()
    detector.run_detection_test()
