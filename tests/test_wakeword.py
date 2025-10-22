# test_wakeword.py
# ====================
# Buddy Core - Wake Word Test using WakeWordListener
# -------------------------------------------------
# Listens once for 'Hey Buddy' and announces detection via Piper TTS.

import sys
import os
# 🔧 Add Buddy Core root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_controller import AudioController
from wake_word_listener import WakeWordListener

def main():
    """Full test sequence: intro TTS -> listen -> announce -> exit."""
    tts = AudioController()
    print("💬 Introduction: Starting Buddy Core wake word test...")
    tts.speak(
        "Hello! This is Buddy Core wake word test. "
        "Please say 'Hey Buddy' once to trigger detection."
    )

    # Initialize wake word listener
    listener = WakeWordListener(audio_controller=tts)
    # Listen once for wake word and announce via TTS
    listener.run_once()

    # Exit phrase
    print("💬 Exit: Wake word test completed. Goodbye.")
    tts.speak("Wake word test completed. Goodbye.")


if __name__ == "__main__":
    main()
