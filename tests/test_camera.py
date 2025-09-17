"""
Test camera capture via CameraManager.
Displays a live preview for 5 seconds.
"""

import cv2
import time
from camera_manager import CameraManager

if __name__ == "__main__":
    cam = CameraManager()
    print("[TEST] Showing camera frames for 5 seconds...")
    start = time.time()
    while time.time() - start < 5:
        frame = cam.get_frame()
        if frame is not None:
            cv2.imshow("Camera Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cam.release()
    cv2.destroyAllWindows()
    print("[TEST] Camera test complete.")
