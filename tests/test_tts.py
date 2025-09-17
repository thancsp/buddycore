"""
Test Text-to-Speech output via AudioController.
"""

from audio_controller import AudioController

if __name__ == "__main__":
    audio = AudioController()
    print("[TEST] Speaking test message...")
    audio.speak("Hello, this is a Buddy Core TTS test")
