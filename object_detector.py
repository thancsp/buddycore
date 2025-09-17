"""
Object Detector: uses TensorFlow Lite SSD model for object detection.
"""

import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from config import MODEL_PATH, LABELS_PATH, CONFIDENCE_THRESHOLD

class ObjectDetector:
    def __init__(self):
        self.interpreter = tflite.Interpreter(model_path=MODEL_PATH)
        self.interpreter.allocate_tensors()

        with open(LABELS_PATH, "r") as f:
            self.labels = [line.strip() for line in f.readlines()]

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def detect(self, frame):
        h, w, _ = frame.shape
        input_shape = self.input_details[0]["shape"]
        resized = cv2.resize(frame, (input_shape[2], input_shape[1]))
        input_data = np.expand_dims(resized, axis=0)

        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
        self.interpreter.invoke()

        boxes = self.interpreter.get_tensor(self.output_details[0]["index"])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]["index"])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]["index"])[0]

        detections = []
        for i, score in enumerate(scores):
            if score >= CONFIDENCE_THRESHOLD:
                ymin, xmin, ymax, xmax = boxes[i]
                detections.append({
                    "label": self.labels[int(classes[i])],
                    "score": float(score),
                    "box": (xmin, ymin, xmax, ymax)
                })
        return detections
