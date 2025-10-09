# camera_manager.py
from picamera2 import Picamera2
import cv2

class CameraManager:
    """
    Handles Raspberry Pi Camera Module 3 via Picamera2.
    Provides frames as OpenCV-compatible BGR numpy arrays.
    """

    def __init__(self, resolution="full"):
        from picamera2 import Picamera2
        self.picam2 = Picamera2()

        if resolution == "full":
            config = self.picam2.create_preview_configuration(main={"size": self.picam2.sensor_resolution})
        else:
            # default to 640x480
            config = self.picam2.create_preview_configuration(main={"size": (640, 480)})

        self.picam2.configure(config)
        self.picam2.start()


    def get_frame(self):
        """
        Capture a single frame and return as BGR numpy array.
        Returns None if capture fails.
        """
        try:
            frame = self.picam2.capture_array("main")         # RGB array
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Convert to BGR for OpenCV
            return frame_bgr
        except Exception as e:
            print(f"Camera error: {e}")
            return None
