"""
Test: Non-blocking Wake Word Detection
--------------------------------------
This test continuously checks if the wake word can be detected
using the `WakeWordListener.detected_nonblocking()` method.

Expected behavior:
- Program announces readiness.
- You say your wake word (e.g., "Hey Buddy").
- It should immediately print detection feedback.
- It keeps running until you say 'exit' or press Ctrl+C.
"""

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === Import project modules ===
from audio_controller import AudioController
from wake_word_listener import WakeWordListener
from config import WAKEWORD_TRIGGER


def main():
    print("🎧 Starting non-blocking wake word detection test...")
    print(f"🔹 Wake word trigger: {WAKEWORD_TRIGGER}")
    print("Say your wake word to test. Say 'exit' to stop.\n")

    # Initialize audio and wake word listener
    audio = AudioController()
    listener = WakeWordListener(audio_controller=audio)

    try:
        while True:
            detected = listener.detected_nonblocking(timeout=0.1)
            if detected:
                print("✅ Wake word detected!")
                audio.speak("Wake word detected.")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔚 Test completed cleanly.")


if __name__ == "__main__":
    main()
