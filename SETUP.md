# 🧠 Buddy Core Set Up Manual

**Version:** 1.3  
**Last Updated:** October 31, 2025
**Note:** This version is subject to change. Please check for updates periodically.  
🔗 [View on GitHub](https://github.com/thancsp/buddycore/blob/main/SETUP.md)

---

## 🪜 Step 1: Download Raspberry Pi OS

1. Go to the [Raspberry Pi OS download page](https://www.raspberrypi.com/software/operating-systems/).  
2. Download **Raspberry Pi OS 64-bit (Bookworm)**.

---

## 💾 Step 2: Flash the SD Card

1. Go to the [Raspberry Pi Imager page](https://www.raspberrypi.com/software/).  
2. Download **Raspberry Pi Imager** for your OS (Windows, macOS, or Linux).  
3. Install Raspberry Pi Imager.  
4. Insert your **SD card (16GB or larger)**.  
5. In Raspberry Pi Imager:
   - **Choose Device →** your Raspberry Pi model  
   - **Choose OS →** “Raspberry Pi OS (other)” or “Custom (the downloaded OS image)” → **64-bit Bookworm**  
   - **Choose SD card →** your card  
   - Click **Write**  
6. Wait for completion, then **safely eject** the SD card.

---

## ⚙️ Step 3: First Boot & Basic Setup

1. Insert the SD card into your Raspberry Pi and **power on**.  
2. Connect to **Wi-Fi** and ensure **date/time** is correct.  
3. Connect to a **Bluetooth speaker** or audio device.  
4. Connect a **microphone** (if available).  
5. Run a full system update:
```bash
   sudo apt update && sudo apt full-upgrade -y
```
### Optional: Enable Raspberry Pi Connect 
Run:
```bash
rpi-connect on
```
or click the Raspberry Pi Connect in the desktop's status bar then: 
- Click the Connect icon in the status bar and sign in with your Raspberry Pi ID (create one if you don’t already have).
- Assign a unique device name and click Create device and sign in.
From now on, the Raspberry Pi will allow you to access remotely from another device with Screen Sharing and SSH
* * *
## 🧩 Step 4: Clone Buddy Core Repository

1.  Navigate to your home directory (Assuming you put Buddy Core in /home/ladmin/):
    
```bash
cd /home/ladmin/
```
2.  Clone the repository:
```bash
git clone https://github.com/thancsp/buddycore.git
```
* * *

## 📦 Step 5: Install Required Packages

First, install all system-level dependencies that Buddy Core needs for audio, Bluetooth, and media handling:

```bash
sudo apt install -y bluez pulseaudio pulseaudio-module-bluetooth alsa-utils libportaudio2 portaudio19-dev ffmpeg
```
Then, create the python virtual environment (venv), and install the Python dependencies from the repository’s `requirements.txt` file:
```bash
cd ~/buddycore
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
This installs all essential Python modules including:
- OpenCV + Picamera2 for camera handling
- Ultralytics YOLOv11 + ONNXRuntime for object detection
- Piper TTS for offline speech output
- Whisper (STT) for speech-to-text
- Porcupine for wake-word detection
- SoundDevice + NumPy for audio I/O
### 💡 After installation, you can verify everything works with:
```bash
python3 -c "import cv2, numpy, sounddevice, whisper, pvporcupine, ultralytics, piper_tts, picamera2, onnxruntime; print('✅ All dependencies OK')"
```
* * *

## 🛠️ Step 6: Reboot and Test

1. Reboot your Raspberry Pi:

```bash
sudo reboot
```
2. After boot, navigate to the Buddy Core directory
```bash
cd ~/buddycore
```
3. Activate the virtual environment:
```bash
source venv/bin/activate
```
💡 After activation, your prompt should show:
```bash
(venv) ladmin@rpi: ~/buddycore $
```
4. Run `tests/test_launcher.py` to validate each module:
```bash
python3 tests/test_launcher.py
```

* * *
## 🏃 Step 7: Run `main.py`

After setting up the virtual environment and installing dependencies, you can run the main Buddy Core program:

```bash
cd ~/buddycore
source venv/bin/activate
python3 main.py
```
This will start the full Buddy Core runtime:
💡 Tip: Keep a terminal open to monitor logs and output while testing.
* * * 
## ⚙️ Step 8: Make main.py Auto-Run on Boot

To have Buddy Core start automatically when the Raspberry Pi powers on, create a systemd service:

1. Create the service file:
```bash
sudo nano /etc/systemd/system/buddycore.service
```
2. Paste the following content (update the paths as necessary):
```ini
[Unit]
Description=Buddy Core Service
After=network.target

[Service]
Type=simple
User=ladmin
WorkingDirectory=/home/ladmin/buddycore
ExecStart=/home/ladmin/buddycore/venv/bin/python3 /home/ladmin/buddycore/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
3. Reload systemd to recognize the new service:
```bash
sudo systemctl daemon-reload
```
4. Enable the service to start on boot:
```bash
sudo systemctl enable buddycore.service
```
5. Start the service immediately (optional):
```bash
sudo systemctl start buddycore.service
```
6. Check the logs:
```bash
journalctl -u buddycore.service -f
```
💡 Tip: If you need to stop the service manually, run:
```bash
sudo systemctl stop buddycore.service
```
* * * 

