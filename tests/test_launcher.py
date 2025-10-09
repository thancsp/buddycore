# tests/test_launcher.py
"""
Interactive Buddy Core Test Launcher
Allows the user to select and run each test script one by one.
"""

import os
import subprocess  # Used to run other Python scripts as separate processes

# === Define available tests ===
# Each test has a number key, a display name, the script path, and a description
TESTS = {
    "1": {
        "name": "TTS Only",
        "script": "tests/test_tts.py",
        "desc": "Plays a test phrase via Piper TTS."
    },
    "2": {
        "name": "Camera Test",
        "script": "tests/test_camera.py",
        "desc": "Capture full-frame image → timestamp → save → show → TTS."
    },
    "3": {
        "name": "Object Detection (YOLO)",
        "script": "tests/test_detector.py",
        "desc": "Capture image → YOLO detection → annotated image → TTS → show."
    },
    "4": {
        "name": "Wake Word Detection",
        "script": "tests/test_wakeword.py",
        "desc": "Listen for 'Hey Buddy' and announce detection."
    },
    "5": {
        "name": "Speech-to-Text Only",
        "script": "tests/test_stt.py",
        "desc": "Record 7s speech → Whisper transcribe → TTS."
    },
    "6": {
        "name": "Full Wake Word + STT",
        "script": "tests/test_full_wakeword.py",
        "desc": "Wake word → beep → 7s speech → Whisper STT → TTS result."
    }
}

# === Utility function: clear the terminal screen ===
def clear_screen():
    # On Unix use 'clear', on Windows use 'cls'
    os.system("clear" if os.name != "nt" else "cls")

# === Display the menu to the user ===
def show_menu():
    clear_screen()
    print("=== Buddy Core Test Launcher ===\n")
    # Print each test option with number, name, and description
    for key, info in TESTS.items():
        print(f"{key}. {info['name']}: {info['desc']}")
    print("0. Exit")
    print("\nSelect a test to run:")

# === Run the selected test script ===
def run_test(choice):
    script = TESTS[choice]["script"]  # Get the script path from TESTS dictionary
    print(f"\n➡ Running {TESTS[choice]['name']}...\n")
    try:
        # Run the script in a separate Python process
        subprocess.run(["python3", script])
    except KeyboardInterrupt:
        # Handle Ctrl+C while the script is running
        print("\n🛑 Test interrupted by user.")
    # Wait for user input before returning to the menu
    input("\nPress Enter to return to the menu...")

# === Main program loop ===
def main():
    while True:
        show_menu()  # Show menu each time
        choice = input("> ").strip()  # Get user input and remove spaces
        if choice == "0":
            print("Exiting launcher. Goodbye!")
            break  # Exit the loop and quit
        elif choice in TESTS:
            run_test(choice)  # Run the chosen test
        else:
            print("❌ Invalid choice. Try again.")  # Handle wrong input

# === Run main loop if this script is executed directly ===
if __name__ == "__main__":
    main()
