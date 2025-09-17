"""
Risk Engine: checks if detected objects are in hazard list.
"""

from config import HAZARD_CLASSES

class RiskEngine:
    def __init__(self):
        pass

    def evaluate(self, detections):
        hazards = []
        for det in detections:
            if det["label"] in HAZARD_CLASSES:
                hazards.append(det["label"])
        return hazards
