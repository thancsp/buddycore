"""
Camera Manager: captures frames from the Pi Camera Module 3.
"""

import cv2

class CameraManager:
    def __init__(self, camera_id=0):
        self.cap = cv2.VideoCapture(camera_id)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()
