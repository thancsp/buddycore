import subprocess
import tempfile
import wave
import numpy as np
import os

class RhasspySTT:
    """
    Simple offline Speech-to-Text using Rhasspy’s CLI (requires Rhasspy or Pocketsphinx).
    It expects a running Rhasspy instance or local CLI command like `rhasspy-client` or `pocketsphinx_continuous`.
    """

    def __init__(self, engine="pocketsphinx"):
        self.engine = engine

    def transcribe(self, pcm_data: np.ndarray) -> str:
        """Convert PCM16 audio to text using offline engine."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            with wave.open(tmpfile.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(pcm_data.tobytes())

            wav_path = tmpfile.name

        try:
            if self.engine == "pocketsphinx":
                # Use offline pocketsphinx command-line decoder
                result = subprocess.check_output(
                    ["pocketsphinx_continuous", "-infile", wav_path],
                    stderr=subprocess.DEVNULL
                )
                text = result.decode("utf-8").strip()
            elif self.engine == "rhasspy":
                # Example if you have rhasspy-client
                result = subprocess.check_output(
                    ["rhasspy-client", "stt", "--audio", wav_path],
                    stderr=subprocess.DEVNULL
                )
                text = result.decode("utf-8").strip()
            else:
                text = "[Unsupported engine]"

        except Exception as e:
            text = f"[STT error: {e}]"
        finally:
            os.remove(wav_path)

        return text
