"""
Test Rhasspy wake word detection.
Waits for 'Hey Buddy' for 10 seconds.
"""

from wake_word_listener import WakeWordListener
from audio_controller import AudioController
import time

if __name__ == "__main__":
    audio = AudioController()
    wake_word = WakeWordListener(audio)

    print("[TEST] Waiting for wake word (say 'Hey Buddy') for 10 seconds...")
    start = time.time()
    detected = False
    while time.time() - start < 10:
        if wake_word.detected():
            print("[TEST] Wake word detected!")
            audio.speak("Wake word detected")
            detected = True
            break
    if not detected:
        print("[TEST] Wake word not detected during test period.")
