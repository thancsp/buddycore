"""
Test object detection module.
Runs one frame through the TFLite model and prints detections.
"""

from camera_manager import CameraManager
from object_detector import ObjectDetector

if __name__ == "__main__":
    cam = CameraManager()
    detector = ObjectDetector()

    print("[TEST] Capturing one frame...")
    frame = cam.get_frame()
    if frame is not None:
        detections = detector.detect(frame)
        print("[TEST] Detections:")
        for det in detections:
            print(f" - {det['label']} ({det['score']:.2f}) box: {det['box']}")
    else:
        print("[TEST] Failed to capture frame.")

    cam.release()
