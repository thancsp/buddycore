#!/bin/bash
set -e

echo "[BuddyCore Setup] Starting setup..."

# ---------------------------
# System update
# ---------------------------
echo "[BuddyCore Setup] Updating system..."
sudo apt update && sudo apt upgrade -y

# ---------------------------
# Install dependencies
# ---------------------------
echo "[BuddyCore Setup] Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv git wget \
    portaudio19-dev pulseaudio alsa-utils sox \
    piper docker.io

# ---------------------------
# Python virtual environment
# ---------------------------
echo "[BuddyCore Setup] Creating Python venv..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install opencv-python numpy tflite-runtime requests

# ---------------------------
# Piper TTS model
# ---------------------------
echo "[BuddyCore Setup] Setting up Piper TTS model..."
MODEL_DIR="models/piper_models"
MODEL_NAME="en_US-hfc_female-medium"
MODEL_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/hfc_female-medium"

mkdir -p $MODEL_DIR

if [ ! -f "$MODEL_DIR/$MODEL_NAME.onnx" ]; then
  echo "[BuddyCore Setup] Downloading Piper ONNX model..."
  wget -O "$MODEL_DIR/$MODEL_NAME.onnx" \
    "$MODEL_URL/$MODEL_NAME.onnx"
fi

if [ ! -f "$MODEL_DIR/$MODEL_NAME.onnx.json" ]; then
  echo "[BuddyCore Setup] Downloading Piper JSON metadata..."
  wget -O "$MODEL_DIR/$MODEL_NAME.onnx.json" \
    "$MODEL_URL/$MODEL_NAME.onnx.json"
fi

# ---------------------------
# Systemd service
# ---------------------------
echo "[BuddyCore Setup] Installing systemd service..."
SERVICE_FILE="/etc/systemd/system/buddy_core.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Buddy Core Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python3 main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

# ---------------------------
# Enable + start service
# ---------------------------
echo "[BuddyCore Setup] Enabling Buddy Core service..."
sudo systemctl daemon-reload
sudo systemctl enable buddy_core.service
sudo systemctl start buddy_core.service

# ---------------------------
# Voice confirmation
# ---------------------------
echo "[BuddyCore Setup] Speaking startup confirmation..."
echo "Buddy Core started" | piper --model "$MODEL_DIR/$MODEL_NAME.onnx" --output-raw | aplay -r 22050 -f S16_LE -t raw -

echo "[BuddyCore Setup] Finished!"
echo "[BuddyCore Setup] Buddy Core should now auto-start on boot."
