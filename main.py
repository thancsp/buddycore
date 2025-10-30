# ============================================================
# main.py — Buddy Core Main Runtime Controller
# ============================================================

# ---- Standard Library Imports ----
import time                     # Used for timing intervals and delays
import threading                # Enables concurrent execution of background threads
import queue                    # Provides a thread-safe command queue for inter-thread communication

# ---- Custom Configuration and Modules ----
from config import (             # Imports key configuration constants
    WAKEWORD_TRIGGER,            # The word that activates Buddy Core (e.g., "Hey Buddy")
    EXIT_PHRASES,                # List of phrases that trigger system shutdown
    DETECTION_INTERVAL,          # Delay between object detection cycles
    HARZARDOUS_OBJECTS           # List of objects considered hazardous
)
from audio_controller import AudioController     # Handles TTS, STT, and audio playback
from wake_word_listener import WakeWordListener  # Detects wake word activation
from object_detector import ObjectDetector        # Performs visual object detection
# CameraManager is now replaced by ObjectDetector, which includes image capture

# ============================================================
# Function: play_intro
# ============================================================
def play_intro(audio: AudioController, listener: WakeWordListener):
    """
    Plays Buddy Core startup message and listens for wake word within 3 seconds.
    Returns True if user says the wake word during the intro.
    """

    # Speak introductory message and instructions
    audio.speak(
        "Buddy Core started. "
        "If you want to hear full instructions, please say 'hey buddy'. "
        "If you already know how to use Buddy Core, please wait 3 seconds after the beep."
    )

    # Play a beep sound to signal listening phase
    audio.play_beep()
    print("🔊 Waiting 3 seconds for wake word...")

    # Track whether wake word is detected
    detected_flag = {"heard": False}

    # Nested function to listen for wake word for up to 3 seconds
    def check_wakeword():
        start_time = time.time()
        while time.time() - start_time < 3 and not detected_flag["heard"]:
            if listener.detected_nonblocking(timeout=0.1):  # Non-blocking check
                print("🟡 Wake word detected during intro!")
                detected_flag["heard"] = True
                break
            time.sleep(0.05)  # Small delay to avoid busy waiting

    # Run wake word detection in a background thread
    thread = threading.Thread(target=check_wakeword, daemon=True)
    thread.start()

    # Main thread waits up to 3 seconds for detection
    start_time = time.time()
    while time.time() - start_time < 3:
        if detected_flag["heard"]:
            return True
        time.sleep(0.05)

    print("⏱️ No wake word detected after 3 seconds.")
    return False


# ============================================================
# Function: play_full_instructions
# ============================================================
def play_full_instructions(audio: AudioController):
    """
    Reads out the complete user guide until user says "skip it" or reaches the end.
    """

    # Predefined lines to read sequentially
    instructions = [
        "Buddy Core is a wearable pendant-like device that helps you detect hazards in front of you and provide audio feedback.",
        "It uses a camera module for object detection, a microphone for offline wake word detection 'Hey Buddy' and a command, and a speaker for spoken alerts.",
        "You can end this instructions by saying 'hey buddy' followed by 'skip it'.",
        "To use it, simply wear Buddy Core around your neck and it will say objects detected in front of you automatically.",
        "By default, Buddy Core will say everything it detects via a speaker. This is the normal mode.",
        "You can change to the other mode by saying 'hey buddy' followed by 'change mode'.",
        "In hazard mode, Buddy Core will only speak when it detects hazards, or when you say 'hey buddy' followed by 'what is it?'.",
        "That's all. If you want to quit, simply say 'hey buddy' followed by 'system shutdown'."
    ]

    # Track whether user wants to skip
    stop_flag = {"skip": False}

    # Background thread to listen for skip command
    def skip_listener():
        listener = WakeWordListener(audio_controller=audio)
        while not stop_flag["skip"]:
            if listener.detected():                    # Wait for wake word
                audio.stop_speech()                    # Stop current TTS
                command = audio.speak_text_and_transcribe().lower()  # Get user’s command
                if "skip it" in command:
                    print("⏭️ Skip command detected. Stopping instructions.")
                    stop_flag["skip"] = True
            time.sleep(0.1)

    threading.Thread(target=skip_listener, daemon=True).start()

    # Sequentially read all instructions
    for line in instructions:
        if stop_flag["skip"]:
            break
        audio.speak(line)
        print(f"📘 {line}")

    # End message depending on skip state
    if stop_flag["skip"]:
        audio.speak("Skipping instructions.")
    else:
        audio.speak("End of instructions.")


# ============================================================
# Function: announce_mode
# ============================================================
def announce_mode(audio: AudioController, mode_name: str):
    """
    Announces the current operation mode and how to change it.
    """
    message = f"Buddy Core is in {mode_name} mode. Change mode by saying 'hey buddy' followed by 'change mode'."
    print(f"🔔 {message}")
    audio.speak(message)


# ============================================================
# Function: wake_word_thread
# ============================================================
def wake_word_thread(listener: WakeWordListener, audio: AudioController, cmd_queue: queue.Queue, running_flag: dict):
    """
    Background thread: continuously listens for wake word and enqueues user commands.
    """
    while running_flag["ok"]:
        if listener.detected():
            print("🟡 Wake word detected! Listening for command...")
            audio.stop_speech()
            cmd = audio.speak_text_and_transcribe().lower()
            cmd_queue.put(cmd)  # Push command to queue for main thread


# ============================================================
# Function: main
# ============================================================
def main():
    """
    Main entry point for Buddy Core runtime.
    Initializes all components, runs intro, handles modes, and controls loop.
    """

    print("🚀 Starting Buddy Core main program...")

    # Initialize core components
    audio = AudioController()
    detector = ObjectDetector()                      # Object + camera handler
    listener = WakeWordListener(audio_controller=audio)
    cmd_queue = queue.Queue()                        # Shared command queue
    running_flag = {"ok": True}                      # System running indicator

    # Step 1: Play intro and possibly full instructions
    if play_intro(audio, listener):
        play_full_instructions(audio)
    else:
        print("➡️ Proceeding to normal mode.")

    # Step 2: Start background wake word listener thread
    threading.Thread(
        target=wake_word_thread,
        args=(listener, audio, cmd_queue, running_flag),
        daemon=True
    ).start()

    # Step 3: Default mode
    current_mode = "Normal"
    announce_mode(audio, current_mode)

    # Step 4: Continuous detection loop
    while running_flag["ok"]:

        # ---- Handle queued voice commands ----
        while not cmd_queue.empty():
            command = cmd_queue.get()

            # Exit commands
            if any(phrase in command for phrase in EXIT_PHRASES):
                audio.speak("Buddy Core is shutting down.")
                print("🛑 System shutdown command received.")
                running_flag["ok"] = False
                break

            # Mode switching
            elif "change mode" in command:
                current_mode = "Hazard" if current_mode == "Normal" else "Normal"
                announce_mode(audio, current_mode)

            # On-demand detection in hazard mode
            elif "what is it" in command and current_mode == "Hazard":
                annotated_frame, detected = detector.detect_frame()
                if annotated_frame is None:
                    print("⚠️ Buddy Core couldn't detect anything right now.")
                    audio.speak("Buddy Core couldn't detect anything")
                else:
                    audio.speak(f"The following objects are detected in front of you: {detected}")

        # ---- Periodic automatic detection ----
        annotated_frame, detected = detector.detect_frame()

        if current_mode == "Normal":
            if annotated_frame is not None:
                print(f"👁️ Detected: {', '.join(detected)}")
                audio.speak(f"{detected} detected.")
            else:
                print("🔍 No objects detected.")
        elif current_mode == "Hazard":
            harzardous = [obj for obj in detected if obj in HARZARDOUS_OBJECTS]
            if harzardous:
                print(f"⚠️ Hazard detected: {', '.join(harzardous)}")
                audio.speak(f"Warning! {harzardous} detected ahead.")

        # Wait between detections
        time.sleep(DETECTION_INTERVAL)

    print("✅ Buddy Core terminated cleanly.")


# ============================================================
# Entrypoint Guard
# ============================================================
if __name__ == "__main__":
    main()
