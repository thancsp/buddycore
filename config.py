"""
Configuration constants for Buddy Core.
"""

MODEL_PATH = "models/ssd_mobilenet_v2.tflite"
LABELS_PATH = "models/coco_labels.txt"

CONFIDENCE_THRESHOLD = 0.5

# Hazard words to announce if detected
HAZARD_CLASSES = ["person", "car", "bicycle", "motorcycle", "bus", "truck"]
