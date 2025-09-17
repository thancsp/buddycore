"""
Wake Word Listener: listens for 'Hey Buddy' from Rhasspy.
"""

import requests

class WakeWordListener:
    def __init__(self, audio_controller, url="http://localhost:12101/api/events/wake"):
        self.url = url
        self.audio = audio_controller

    def detected(self):
        try:
            resp = requests.get(self.url, timeout=0.5)
            if resp.status_code == 200:
                return True
        except:
            return False
        return False
