"""
Main program: integrates wake word, camera, detection, risk, and audio.
"""

import time
from camera_manager import CameraManager
from object_detector import ObjectDetector
from risk_engine import RiskEngine
from audio_controller import AudioController
from wake_word_listener import WakeWordListener

def main():
    audio = AudioController()
    cam = CameraManager()
    detector = ObjectDetector()
    risk_engine = RiskEngine()
    wake_word = WakeWordListener(audio)

    audio.speak("Buddy Core started")
    print("[INFO] Buddy Core started")

    try:
        while True:
            frame = cam.get_frame()
            if frame is None:
                continue

            # Wake word trigger
            if wake_word.detected():
                audio.speak("Scanning surroundings")
                detections = detector.detect(frame)
                hazards = risk_engine.evaluate(detections)
                if hazards:
                    audio.speak("Nearby: " + ", ".join(hazards))
                else:
                    audio.speak("No hazards detected")

            # Hazard auto-detection
            detections = detector.detect(frame)
            hazards = risk_engine.evaluate(detections)
            if hazards:
                audio.speak("Caution: " + ", ".join(hazards))

            time.sleep(0.5)
    except KeyboardInterrupt:
        audio.speak("Buddy Core shutting down")
        cam.release()
        print("[INFO] Buddy Core stopped")

if __name__ == "__main__":
    main()
