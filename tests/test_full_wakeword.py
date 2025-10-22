"""
Buddy Core - Continuous Wake Word → STT → Exit Test
===================================================
Continuously listens for the configured wake word using Porcupine.
When triggered, it runs a full speech-to-text (STT) session using Whisper,
announces the transcribed result using Piper TTS,
and terminates gracefully when the user says any EXIT_PHRASE.
"""
import sys
import os
# 🔧 Add Buddy Core root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from audio_controller import AudioController
from wake_word_listener import WakeWordListener
from config import (
    WAKEWORD_TRIGGER,
    EXIT_PHRASES,
)


def main():
    """
    Main loop:
      1. Speak introduction.
      2. Continuously wait for wake word.
      3. After wake word, record speech (STT).
      4. Announce recognized text.
      5. Stop if exit phrase is detected.
    """
    tts = AudioController()

    # === Step 1: Speak introduction ===
    intro_text = (
        f"Starting Buddy Core full wake word test. "
        f"Say '{WAKEWORD_TRIGGER}' to begin speaking. "
    )
    print(f"💬 {intro_text}")
    tts.speak(intro_text)
    time.sleep(1)

    # === Step 2: Initialize wake word listener ===
    wake_listener = WakeWordListener(audio_controller=tts)

    # === Continuous loop ===
    while True:
        print(f"\n🎧 Listening for wake word: ['{WAKEWORD_TRIGGER}']...")
        if wake_listener.detected():  # Blocking call until detected
            print("✅ Wake word detected.")
            time.sleep(0.5)

            # === Step 3: Speech-to-Text ===
            print("🧠 Listening for your speech...")
            recognized_text = tts.speak_text_and_transcribe()

            # === Step 4: Exit check ===
            if any(
                phrase.lower() in recognized_text.lower()
                for phrase in EXIT_PHRASES
            ):
                print("👋 Exit phrase detected. Ending test.")
                tts.speak("Exit phrase detected. Shutting down. Goodbye.")
                break  # Exit loop

            print("🔁 Waiting for next wake word...")
            tts.speak("You can say Hey Buddy again to continue.")

        else:
            print("❌ Wake word not detected.")
            tts.speak("I did not detect any wake word. Please try again.")
            time.sleep(1)

    print("✅ Full wake word loop test completed.")


# === Entry point ===
if __name__ == "__main__":
    main()
