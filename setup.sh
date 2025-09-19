#!/bin/bash
# setup.sh - Setup environment for Buddy Core on Raspberry Pi

set -e

echo "=== Buddy Core Setup Starting ==="

# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Install essential packages
sudo apt install -y \
    python3-venv python3-pip \
    libatlas-base-dev libopenjp2-7-dev libjpeg-dev \
    libfreetype6-dev libpng-dev \
    bluez pulseaudio alsa-utils \
    libasound2-dev \
    cmake git wget unzip curl \
    rpi-eeprom-update \
    ffmpeg \
    libcap-dev

# 3. Install libcamera apps for Raspberry Pi Camera Module 3
sudo apt install -y libcamera-apps

# 4. Create Python virtual environment
python3 -m venv ~/buddycore/venv
source ~/buddycore/venv/bin/activate

# 5. Upgrade pip
pip install --upgrade pip

# 6. Install Python packages
pip install --upgrade numpy opencv-python tflite-runtime requests

# 7. Install Piper TTS
pip install piper-tts

# 8. Test Piper installation
echo "Testing Piper TTS..."
python3 -c "import piper_tts; print('Piper TTS installed successfully')"

# 9. Bluetooth & PulseAudio setup
echo "Configuring Bluetooth speaker and PulseAudio..."
# Make sure your speaker is paired manually before running Buddy Core

# 10. Create systemd service for Buddy Core
echo "Creating systemd service..."
sudo tee /etc/systemd/system/buddy_core.service > /dev/null <<EOF
[Unit]
Description=Buddy Core Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/buddycore
ExecStart=/home/pi/buddycore/venv/bin/python3 /home/pi/buddycore/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 11. Enable service
sudo systemctl daemon-reload
sudo systemctl enable buddy_core.service

echo "=== Buddy Core Setup Complete ==="
echo "You can start the service with: sudo systemctl start buddy_core"
