import time
import threading
import queue

from config import WAKEWORD_TRIGGER, EXIT_PHRASES, DETECTION_INTERVAL, HARZARDOUS_OBJECTS
from audio_controller import AudioController
from wake_word_listener import WakeWordListener
from object_detector import ObjectDetector


# === Intro / Wake Word ===
def play_intro(audio: AudioController, listener: WakeWordListener):
    audio.speak(
        "Buddy Core started. "
        "If you want to hear full instructions, please say 'hey buddy'. "
        "If you already know how to use Buddy Core, please wait 3 seconds after the beep."
    )
    audio.play_beep()
    print("🔊 Waiting 3 seconds for wake word...")

    detected_flag = {"heard": False}

    def check_wakeword():
        start_time = time.time()
        while time.time() - start_time < 3 and not detected_flag["heard"]:
            if listener.detected_nonblocking(timeout=0.1):
                print("🟡 Wake word detected during intro!")
                detected_flag["heard"] = True
                break
            time.sleep(0.05)

    thread = threading.Thread(target=check_wakeword, daemon=True)
    thread.start()

    # Wait max 3 seconds
    start_time = time.time()
    while time.time() - start_time < 3:
        if detected_flag["heard"]:
            return True
        time.sleep(0.05)

    print("⏱️ No wake word detected after 3 seconds.")
    return False


# === Full Instructions ===
def play_full_instructions(audio: AudioController):
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

    stop_flag = {"skip": False}

    def skip_listener():
        listener = WakeWordListener(audio_controller=audio)
        while not stop_flag["skip"]:
            if listener.detected():
                audio.stop_speech()
                command = audio.speak_text_and_transcribe().lower()
                if "skip it" in command:
                    print("⏭️ Skip command detected. Stopping instructions.")
                    stop_flag["skip"] = True
            time.sleep(0.1)

    threading.Thread(target=skip_listener, daemon=True).start()

    for line in instructions:
        if stop_flag["skip"]:
            break
        audio.speak(line)
        print(f"📘 {line}")

    if stop_flag["skip"]:
        audio.speak("Skipping instructions.")
    else:
        audio.speak("End of instructions.")


# === Mode Announcement ===
def announce_mode(audio: AudioController, mode_name: str):
    message = f"Buddy Core is in {mode_name} mode. Change mode by saying 'hey buddy' followed by 'change mode'."
    print(f"🔔 {message}")
    audio.speak(message)


# === Background Wake Word Thread ===
def wake_word_thread(listener: WakeWordListener, audio: AudioController, cmd_queue: queue.Queue, running_flag: dict):
    while running_flag["ok"]:
        if listener.detected():
            print("🟡 Wake word detected! Listening for command...")
            audio.stop_speech()
            cmd = audio.speak_text_and_transcribe().lower()
            cmd_queue.put(cmd)


# === Main Loop ===
def main():
    print("🚀 Starting Buddy Core main program...")
    audio = AudioController()
    detector = ObjectDetector()  # replace CameraManager
    listener = WakeWordListener(audio_controller=audio)
    cmd_queue = queue.Queue()
    running_flag = {"ok": True}

    # Step 1: Intro
    if play_intro(audio, listener):
        play_full_instructions(audio)
    else:
        print("➡️ Proceeding to normal mode.")

    # Step 2: Start background wake word listener
    threading.Thread(target=wake_word_thread, args=(listener, audio, cmd_queue, running_flag), daemon=True).start()

    # Step 3: Default mode
    current_mode = "Normal"
    announce_mode(audio, current_mode)

    # Step 4: Core operation loop
    while running_flag["ok"]:
        # Handle queued commands
        while not cmd_queue.empty():
            command = cmd_queue.get()

            if any(phrase in command for phrase in EXIT_PHRASES):
                audio.speak("Buddy Core is shutting down.")
                print("🛑 System shutdown command received.")
                running_flag["ok"] = False
                break

            elif "change mode" in command:
                current_mode = "Hazard" if current_mode == "Normal" else "Normal"
                announce_mode(audio, current_mode)

            elif "what is it" in command and current_mode == "Hazard":
                annotated_frame, detected = detector.detect_frame()
                if annotated_frame is None:
                    print("⚠️ Buddy Core couldn't detect anything right now.")
                    audio.speak(f"Buddy Core couldn't detect anything")
                else:
                    audio.speak(f"{detected} in front of you.")

        # Detection logic every DETECTION_INTERVAL
        annotated_frame, detected = detector.detect_frame()
        if current_mode == "Normal":
            if annotated_frame is not None :
                print(f"👁️ Detected: {', '.join(detected)}")
                audio.speak(f"{detected} detected.")
            else:
                print("🔍 No objects detected.")
        elif current_mode == "Hazard":
            harzardous = [obj for obj in detected if obj in HARZARDOUS_OBJECTS]
            if harzardous:
                print(f"⚠️ Hazard detected: {', '.join(harzardous)}")
                audio.speak(f"Warning! {harzardous} detected ahead.")
        time.sleep(DETECTION_INTERVAL)

    print("✅ Buddy Core terminated cleanly.")


if __name__ == "__main__":
    main()
