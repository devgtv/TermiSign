import json
from vosk import Model, KaldiRecognizer, SetLogLevel
from audio.capture import SAMPLE_RATE

SetLogLevel(-1)


class VoskSTT:
    def __init__(self, model_path: str = "vosk-model-small-pt-0.3"):
        self._model = Model(model_path)
        self._rec = KaldiRecognizer(self._model, SAMPLE_RATE)
        self._buffer = b""

    def transcribe(self, audio_chunk: bytes) -> str | None:
        if self._rec.AcceptWaveform(audio_chunk):
            result = json.loads(self._rec.FinalResult())
            text = result.get("text", "").strip()
            return text if text else None
        else:
            partial = json.loads(self._rec.PartialResult())
            text = partial.get("partial", "").strip()
            return text if text else None

    def reset(self):
        self._rec = KaldiRecognizer(self._model, SAMPLE_RATE)
