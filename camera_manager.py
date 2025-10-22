# camera_manager.py
# =================
# Buddy Core Camera Manager
# -------------------------
# Handles Raspberry Pi Camera Module 3 via Picamera2.
# Provides frames as OpenCV-compatible BGR numpy arrays.
# Includes line-by-line explanations.

import cv2
from picamera2 import Picamera2

class CameraManager:
    """
    CameraManager handles camera initialization, configuration, and frame capture.
    Provides safe access to frames for downstream modules.
    """

    def __init__(self, resolution="full"):
        """
        Initialize Picamera2 and configure the capture resolution.
        Arguments:
            resolution (str or tuple): "full" uses sensor's max resolution,
                                       otherwise provide (width, height) tuple.
        """
        try:
            # Initialize Picamera2 instance
            self.picam2 = Picamera2()

            # Configure resolution
            if resolution == "full":
                # Use full sensor resolution
                config = self.picam2.create_preview_configuration(
                    main={"size": self.picam2.sensor_resolution}
                )
            elif isinstance(resolution, tuple) and len(resolution) == 2:
                # Use custom resolution (width, height)
                config = self.picam2.create_preview_configuration(
                    main={"size": resolution}
                )
            else:
                # Default fallback resolution 640x480
                config = self.picam2.create_preview_configuration(
                    main={"size": (640, 480)}
                )

            # Apply configuration
            self.picam2.configure(config)
            self.picam2.start()
            print(f"✅ Camera initialized with resolution {config['main']['size']}")

        except Exception as e:
            # Catch initialization errors
            print(f"❌ Failed to initialize camera: {e}")
            self.picam2 = None

    def get_frame(self):
        """
        Capture a single frame from the camera.
        Returns:
            frame_bgr (numpy array): OpenCV BGR image, or None if capture fails.
        """
        if self.picam2 is None:
            print("❌ Camera not available.")
            return None

        try:
            # Capture frame as RGB array
            frame_rgb = self.picam2.capture_array("main")
            # Convert to BGR for OpenCV compatibility
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            return frame_bgr
        except Exception as e:
            print(f"❌ Failed to capture frame: {e}")
            return None
