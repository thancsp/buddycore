# test_wakeword.py
# ====================
# Buddy Core - Wake Word Test using WakeWordListener
# -------------------------------------------------
# Listens once for 'Hey Buddy' and announces detection via Piper TTS.

import sys
import os
import time

# 🔧 Add Buddy Core root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_controller import AudioController
from wake_word_listener import WakeWordListener

def main():
    """Full test sequence: intro TTS -> listen once -> announce -> exit."""
    tts = AudioController()
    print("💬 Introduction: Starting Buddy Core wake word test...")
    tts.speak(
        "Hello! This is Buddy Core wake word test. "
        "Say 'Hey Buddy' once to trigger detection."
    )

    # Initialize wake word listener
    listener = WakeWordListener(audio_controller=tts)

    print("🎧 Listening for wake word once...")

    # Wait until wake word is detected once
    while True:
        if listener.detected():
            print("✅ Wake word detected!")
            tts.speak("Wake word detected.")
            break
        time.sleep(0.1)

    print("💬 Exit: Wake word test completed. Goodbye.")
    tts.speak("Wake word test completed. Goodbye.")


if __name__ == "__main__":
    main()
