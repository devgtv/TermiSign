import speech_recognition as sr
from audio.capture import SAMPLE_RATE


class GoogleSTT:
    def __init__(self, language="pt-BR"):
        self.language = language
        self._recognizer = sr.Recognizer()

    def transcribe(self, audio_chunk: bytes) -> str | None:
        try:
            audio_data = sr.AudioData(audio_chunk, SAMPLE_RATE, 2)
            text = self._recognizer.recognize_google(
                audio_data, language=self.language
            )
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None
