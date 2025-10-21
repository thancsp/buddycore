# Buddy Core Set Up Manual

Version: 1.2  
Last Updated: September 23, 2025  
Note: This version is subject to change. Please check for updates periodically. [https://github.com/thancsp/buddycore/blob/main/SETUP.md](https://github.com/thancsp/buddycore/blob/main/SETUP.md) 

* * *

## Step 1: Download Raspberry Pi OS

*   Go to the [Raspberry Pi OS download page](https://www.raspberrypi.com/software/operating-systems/).
    
*   Download Raspberry Pi OS 64-bit (Bookworm):
    

*   Lite: headless, minimal, recommended for Buddy Core.
    
*   Desktop: includes GUI, useful for camera testing.
    

* * *

## Step 2: Flash the SD Card

1.  Go to the [Raspberry Pi software Page](https://www.raspberrypi.com/software/)
    
2.  Download Raspberry Pi Imager for your computer's operating system.
    
3.  Install Raspberry Pi Imager on your computer.
    
4.  Insert SD card (16GB+ recommended).
    
5.  In Raspberry Pi Imager:
    

*   Choose OS → “Raspberry Pi OS (other)” → 64-bit Bookworm
    
*   Choose SD card → your SD card
    
*   Click Write
    

7.  Wait for completion and safely eject the SD card.
    

* * *

## Step 3: First Boot & Basic Setup

1.  Insert SD card into the Raspberry Pi Imager and power on.
    
2.  Connect to Wi-Fi and ensure date/time is correct.
    
3.  Connect to a BlueTooth speaker
    
4.  Update the system:
    

sudo apt update && sudo apt full-upgrade -y

Optional:

5.  Enable Raspberry Pi Connect Run:
    

rpi-connect on

6.  After starting the service, click the Connect icon in the status bar and select Sign in.
    
7.  If you don’t already have Raspberry Pi ID, create one
    
8.  After authenticating, assign a name to your device. Choose a name that uniquely identifies the device. Click the Create device and sign in button to continue.
    
9.  From now on, the Raspberry Pi will allow you to access remotely from another device with Screen Sharing and SSH
    

* * *

## Step 4: Install Required Packages

1.  Install all system dependencies Buddy Core needs:
    

sudo apt update && sudo apt full-upgrade -y

sudo apt install -y \\

    git \\

    python3-venv python3-pip \\

    docker.io \\

    bluez pulseaudio pulseaudio-module-bluetooth \\

    alsa-utils libatlas-base-dev libportaudio2 portaudio19-dev \\

    ffmpeg

2.  Enable and start Docker:
    

sudo systemctl enable docker

sudo systemctl start docker

* * *

## Step 5: Clone Buddy Core Repository

1.  Navigate to your home directory (Assuming you put Buddy Core in /home/ladmin/):
    

cd /home/ladmin/

3.  Clone the repository:
    

git clone https://github.com/thancsp/buddycore.git

* * *

## Step 6: Run setup.sh

1.  Navigate into Buddy Corefolder:
    

cd ~/buddycore

2.  Make script executable:
    

chmod +x setup.sh

3.  Run the setup script:
    

./setup.sh

What this does:

*   Creates a Python virtual environment.
    
*   Installs required Python dependencies (OpenCV, TFLite runtime, Piper TTS, etc.).
    
*   Configures Bluetooth and audio support.
    
*   Installs and runs Rhasspy in Docker for offline wake word detection.
    
*   Creates and enables the Buddy Core systemd service.
    

* * *

## Step 7: Reboot and Test

1.  Reboot the Pi
    

sudo reboot

2.  On boot, Buddy Core should announce via Bluetooth speaker:
    

“Buddy Core started”

3.  To monitor log
    

journalctl -u buddycore.service -f

* * *

## Step 8: Optional Validation

Run individual test scripts to validate each module:

source venv/bin/activate

python3 tests/test\_tts.py

python3 tests/test\_camera.py

python3 tests/test\_detector.py

python3 tests/test\_wake\_word.py

Purpose of each test script:

*   test\_tts.py → Check Piper TTS.
    
*   test\_camera.py → Capture frame from Pi Camera.
    
*   test\_detector.py → Run object detection (TFLite SSD).
    
*   test\_wake\_word.py → Simulate wake word detection.
    

* * *

## Notes & Tips

### Pi Connect / Remote Access

*   If the Pi doesn’t appear in Pi Connect, check firewall and\*\* Wi-Fi\*\* connectivity.
    
*   Ensure your Raspberry Pi ID is correctly signed in.
    

### Camera Issues

*   Raspberry Pi Camera Module 3 requires libcamera-apps installed.
    
*   Test via CLI:
    

libcamera-still -o test.jpg

*   If you get command not found, reinstall libcamera-apps.
    
*   Ensure camera ribbon is properly seated and enabled via raspi-config.
    

### Piper TTS Issues

*   Piper requires libcap-dev and alsa-utils.
    
*   If first word is cut off, use a short prepended space in text input.
    
*   Quick test:
    

python3 -c "import piper\_tts; print('Piper works')"

### Bluetooth Speaker

*   Make sure the speaker is paired manually before running Buddy Core.
    
*   PulseAudio and ALSA should be configured for output.
    

### General Troubleshooting

*   Check logs:
    

journalctl -u buddy\_core.service -f

*   Activate venv before running test scripts:
    

source venv/bin/activate

*   If Raspberry Pi Imager has been activated, you should see:
    

(venv) username@hostname: ~/directory $

  

OR

  

(venv) ladmin@rpi: ~/buddycore $

At this point, Buddy Core is fully deployed on a fresh Raspberry Pi OS, ready for use by visually impaired users.
