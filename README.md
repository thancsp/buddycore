# 🤖 Buddy Core  
**Smart Vision and Voice Assistant for Raspberry Pi**  
*An offline AI companion combining object detection, wake-word interaction, and natural speech.*

---

## 🌟 Overview
**Buddy Core** is an intelligent embedded system that detects objects in real-time, listens for wake words, and interacts through speech — all running **offline on a Raspberry Pi**.  
It uses **YOLOv11** for computer vision, **Porcupine** for wake word detection, and **Piper TTS** for natural voice output.

---

## 🧠 Features
- 🎯 **Real-time Object Detection** with YOLOv11 (via camera)
- 🔈 **Offline Wake Word Detection** (“Hey Buddy”)
- 🗣 **Text-to-Speech (TTS)** using Piper (interruptible)
- ⚙️ **Two Operation Modes**
  - **Normal Mode** → reports all detected objects  
  - **Hazard Mode** → reports only hazardous items
- 💾 **Automatic Frame Logging** → annotated images saved with timestamp  
  (auto-manages last 100 detection images)
- 🔄 **Modular Design** for easy integration with new AI models or sensors

---

## 🧩 System Architecture
```sql
+---------------------------------------------------+
|                     main.py                       |
|---------------------------------------------------|
| • Coordinates all subsystems                      |
| • Manages Normal/Hazard modes                     |
| • Handles wake-word events and voice commands     |
+----------------------------+----------------------+
                             |
                             v
          +------------------+------------------+
          |          WakeWordListener           |
          |-------------------------------------|
          | • Uses Porcupine offline engine      |
          | • Detects “Hey Buddy” and commands   |
          +------------------+------------------+
                             |
                             v
          +------------------+------------------+
          |            ObjectDetector            |
          |-------------------------------------|
          | • YOLOv11 (ONNX) object detection    |
          | • Annotates and timestamps frames    |
          | • Saves last 100 detections          |
          +------------------+------------------+
                             |
                             v
          +------------------+------------------+
          |           AudioController            |
          |-------------------------------------|
          | • Uses Piper TTS for speech output   |
          | • Interruptible voice playback       |
          +------------------+------------------+
```
---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/thancsp/buddycore.git
cd buddycore
```
### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
### 3️⃣ Download Required Models
- YOLOv11 ONNX model → place in `models/yolo11`
- Porcupine wake word model → place in `models/porcupine/`
- Piper voice model → place in `models/piper_models`
(See comments in `config.py` for model paths and supported file names.)
## 🚀 Usage
Run Buddy Core directly:
```bash
cd buddycore/
source venv/bin/activate
python3 main.py
```
## 🗂 Folder Structure
```bash
buddycore/
├── main.py
├── audio_controller.py
├── wakeword_listener.py
├── object_detector.py
├── config.py
├── OUTPUT/                # Annotated frames
├── models/                # YOLO + Porcupine
├── voices/                # Piper TTS models
└── test/                  # Optional test scripts
```
## 📸 Output
Each detection is saved to the `OUTPUT/` folder as:
```bash
[DETECTED]YYYY-MM-DD-HH-MM-SS.jpg
```
- Timestamp overlay at top-left
- Bounding boxes for detected objects
- Folder automatically pruned to keep the latest 100 images
## 🧪 Testing
To run the test sequence:
```bash
python3 test/test_launcher.py
```
Follow the on screen instructions
## 🔐 License
MIT License © 2025 Than Chaiboriphan (on behalf of Saint Paul Convent School, Thailand)
## 🙌 Acknowledgments
- [Ultralytics YOLOv11](https://github.com/ultralytics/ultralytics)
- [Picovoice Porcupine](https://github.com/Picovoice/porcupine)
- [Piper TTS](https://github.com/OHF-Voice/piper1-gpl)
- [Raspberry Pi Foundation](https://www.raspberrypi.org)
---
