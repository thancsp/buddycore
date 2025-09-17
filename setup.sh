#!/bin/bash
# Setup script for Buddy Core

echo "[INFO] Installing system packages..."
sudo apt update
sudo apt install -y python3-venv python3-pip docker.io espeak

echo "[INFO] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install opencv-python numpy tflite-runtime requests

echo "[INFO] Pulling Rhasspy Docker image..."
sudo docker pull rhasspy/rhasspy:latest
sudo docker run -d \
    --name rhasspy \
    --restart unless-stopped \
    -p 12101:12101 \
    rhasspy/rhasspy \
    --user-profiles /profiles \
    --profile en

echo "[INFO] Installing systemd service..."
sudo tee /etc/systemd/system/buddy_core.service > /dev/null <<EOL
[Unit]
Description=Buddy Core Service
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=/home/pi/buddy_core
ExecStart=/home/pi/buddy_core/venv/bin/python /home/pi/buddy_core/main.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable buddy_core.service

echo "[INFO] Setup complete. Reboot and Buddy Core will auto-start."
