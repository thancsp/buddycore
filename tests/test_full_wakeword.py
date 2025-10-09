"""
test_full_wakeword.py

This test script performs a full integration test of Buddy Core’s voice pipeline:
1. Listens for the wake word (“Hey Buddy”) using Porcupine
2. Pauses wake word detection and records 7 seconds of speech
3. Transcribes the speech with Whisper STT
4. Responds using Piper TTS
5. Terminates when user says “shut down” or “abort testing”
"""

import os
import sys
import queue
import time
import threading
import tempfile
import sounddevice as sd
import numpy as np
import pvporcupine
import whisper
import soundfile as sf

# 🔧 Add Buddy Core root to Python path so that local modules (like audio_controller.py) can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audio_controller import AudioController

# === Configuration ===
WAKE_WORD = "Hey Buddy"     # Wake word to trigger recording
EXIT_PHRASES = ["shut down", "abort testing"]  # Commands that end the test
ACCESS_KEY = "8sBtDjXViIrp/HFRNv6YeXJrgn7vVfHwQeGB6L6MjPYaFrpRX0EJMg=="  # Picovoice API access key
KEYWORD_PATH = "/home/ladmin/buddycore/models/porcupine/Hey-buddy_en_raspberry-pi_v3_0_0.ppn"  # Path to .ppn model
SAMPLE_RATE = 16000         # Sample rate in Hz (required by Porcupine and Whisper)
CHANNELS = 1                # Mono microphone input
RECORD_SECONDS = 7          # Duration of user speech capture
MODEL_NAME = "tiny"         # Whisper model size ("tiny", "base", "small", etc.)

# === Global State Flags and Shared Objects ===
audio_queue = queue.Queue()           # Buffer for audio stream samples
detected_event = threading.Event()    # Trigger when wake word is detected
terminate_event = threading.Event()   # Global stop flag for the main loop
pause_detection = threading.Event()   # Pauses wake word detection during TTS or recording
whisper_model = None                  # Cache Whisper model so it loads only once
porcupine = None                      # Handle for Porcupine wake word engine


# === Text-to-Speech Wrapper ===
def speak(text):
    """Speak text aloud using Piper TTS (via AudioController)."""
    pause_detection.set()   # Temporarily stop wake word detection
    print(f"🔊 Speaking: {text}")
    try:
        AudioController().speak(text)  # Call Buddy Core’s audio controller
    except Exception as e:
        print(f"⚠️ TTS error: {e}")
    time.sleep(0.2)         # Short delay to ensure mic settles
    pause_detection.clear() # Resume detection after TTS completes


# === Beep Generator ===
def play_beep():
    """Generate and play a short beep tone."""
    duration = 0.25          # Beep duration (seconds)
    frequency = 880          # Frequency (Hz)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)  # Time axis
    beep = np.sin(2 * np.pi * frequency * t) * 0.3                   # Sine wave at given frequency
    sd.play(beep, SAMPLE_RATE)   # Play via sounddevice
    sd.wait()                    # Wait until playback completes


# === Audio Callback ===
def audio_callback(indata, frames, time_info, status):
    """Triggered continuously by sounddevice.InputStream."""
    if status:
        print(status)  # Print audio warnings (e.g., buffer underrun)
    # Only collect audio for detection when not paused
    if not pause_detection.is_set():
        audio_queue.put(indata.copy())


# === Wake Word Listener Thread ===
def wakeword_listener():
    """Continuously checks microphone stream for the Porcupine wake word."""
    global porcupine
    porcupine = pvporcupine.create(access_key=ACCESS_KEY, keyword_paths=[KEYWORD_PATH])
    frame_length = porcupine.frame_length  # Expected frame length (512 samples for 16 kHz)
    buffer = np.zeros((0,), dtype=np.int16)  # Empty buffer to hold incoming samples
    print(f"🎧 Listening for wake word '{WAKE_WORD}'... (say 'shut down' to quit)")

    while not terminate_event.is_set():  # Run until main thread signals stop
        if pause_detection.is_set():     # Pause if TTS or recording active
            time.sleep(0.1)
            continue

        try:
            data = audio_queue.get(timeout=0.5)  # Get audio samples from queue
        except queue.Empty:
            continue

        # Convert float32 (-1.0 to 1.0) → int16 (Porcupine format)
        audio_data = (data.flatten() * 32768).astype(np.int16)
        buffer = np.concatenate((buffer, audio_data))

        # Process in chunks of `frame_length`
        while len(buffer) >= frame_length:
            frame = buffer[:frame_length]
            buffer = buffer[frame_length:]
            keyword_index = porcupine.process(frame)
            if keyword_index >= 0:   # Keyword detected!
                print("✅ Wake word detected!")
                detected_event.set() # Signal to main thread
                break

    porcupine.delete()  # Clean up Porcupine instance on exit


# === Audio Recording ===
def record_speech(duration=RECORD_SECONDS):
    """Record a fixed-duration audio clip."""
    pause_detection.set()  # Disable wake word while recording
    play_beep()            # Pre-record beep
    print(f"🎙️ Recording {duration} seconds of speech...")
    recording = sd.rec(    # Capture from default mic
        int(SAMPLE_RATE * duration),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='float32'
    )
    sd.wait()              # Wait for recording to finish
    play_beep()            # Post-record beep

    # Save to a temporary WAV file for Whisper
    wav_path = tempfile.mktemp(suffix=".wav")
    sf.write(wav_path, recording, SAMPLE_RATE)
    print(f"💾 Audio saved to {wav_path}")

    pause_detection.clear()  # Re-enable detection
    return wav_path


# === Whisper Speech Recognition ===
def transcribe_audio(wav_path):
    """Transcribe audio to text using OpenAI Whisper."""
    global whisper_model
    if whisper_model is None:               # Load model only once
        print("🧠 Loading Whisper model...")
        whisper_model = whisper.load_model(MODEL_NAME)
        print("✅ Whisper model loaded.")
    print("📝 Transcribing audio...")
    result = whisper_model.transcribe(wav_path)  # Run STT
    text = result["text"].strip().lower()        # Clean result
    print(f"🧾 Transcribed text: {text}")
    return text


# === Main Control Loop ===
def main():
    """Orchestrates the test — wake word, recording, STT, and TTS."""
    # Speak initial instructions
    speak("Hello. This is Buddy Core full test. Say 'Hey Buddy' to start, and I’ll listen for seven seconds. Say 'shut down' to end testing.")
    time.sleep(0.5)

    # Open microphone input stream
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=512,
        dtype="float32",
        channels=CHANNELS,
        callback=audio_callback,
    ):
        # Run wake word listener in background
        listener_thread = threading.Thread(target=wakeword_listener, daemon=True)
        listener_thread.start()

        # Loop until user says shutdown or abort
        while not terminate_event.is_set():
            detected_event.wait()   # Wait for “Hey Buddy”
            if terminate_event.is_set():
                break

            speak("Hey, I’m listening.")    # Acknowledge wake word

            # Step 1 — Record voice input
            wav_file = record_speech(RECORD_SECONDS)

            # Step 2 — Convert to text
            spoken_text = transcribe_audio(wav_file)

            # Step 3 — Check if user wants to end test
            if any(phrase in spoken_text for phrase in EXIT_PHRASES):
                speak("Abort testing confirmed. Buddy Core is shutting down now.")
                terminate_event.set()
                break

            # Step 4 — Repeat the recognized text back
            speak(f"You said: {spoken_text}. Ready for the next command.")
            detected_event.clear()   # Reset detection flag for next cycle

        print("🛑 Test ended. Goodbye!")


# === Entry Point ===
if __name__ == "__main__":
    try:
        main()  # Run the full wake word + STT loop
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")  # Handle Ctrl+C gracefully
    finally:
        if porcupine:
            porcupine.delete()  # Ensure Porcupine engine is properly released
