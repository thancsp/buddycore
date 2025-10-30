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
    === Methods Summary ===
    __init__(resolution="full"): Initialize camera, configure resolution, start capture.
    get_frame(): Capture a single frame and return as OpenCV-compatible BGR numpy array.

    === Variables ===
    picam2: Picamera2 instance (None if initialization fails)
    """

    def __init__(self, resolution="full"):
        """
        Initialize Picamera2 and configure the capture resolution.
        
        Arguments:
            resolution (str or tuple): 
                "full" uses sensor's max resolution,
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

            # Apply configuration to Picamera2
            self.picam2.configure(config)
            self.picam2.start()
            print(f"✅ Camera initialized with resolution {config['main']['size']}")

        except Exception as e:
            # Catch initialization errors and disable camera access
            print(f"❌ Failed to initialize camera: {e}")
            self.picam2 = None

    def get_frame(self):
        """
        Capture a single frame from the camera.

        Returns:
            frame_bgr (numpy array): OpenCV BGR image, or None if capture fails.
        """
        if self.picam2 is None:
            # Camera not initialized
            print("❌ Camera not available.")
            return None

        try:
            # Capture frame as RGB array from Picamera2
            frame_rgb = self.picam2.capture_array("main")

            # Convert RGB to BGR for OpenCV compatibility
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            return frame_bgr

        except Exception as e:
            # Capture failed
            print(f"❌ Failed to capture frame: {e}")
            return None
