import logging
from stt.google_stt import GoogleSTT
from stt.vosk_stt import VoskSTT

logger = logging.getLogger("termisign")


class SpeechRecognizer:
    def __init__(self, vosk_model_path: str = "vosk-model-small-pt-0.3"):
        self._google = GoogleSTT()
        self._vosk = None
        self._online = True

        try:
            self._vosk = VoskSTT(vosk_model_path)
            logger.info("Vosk offline carregado")
        except Exception as e:
            logger.warning(f"Vosk nao disponivel: {e}")

    def transcribe(self, audio_chunk: bytes) -> str | None:
        if self._online:
            text = self._google.transcribe(audio_chunk)
            if text:
                return text
            logger.debug("Google falhou, tentando Vosk...")
            self._online = False

        if self._vosk:
            return self._vosk.transcribe(audio_chunk)

        return None

    def force_offline(self):
        self._online = False

    def force_online(self):
        self._online = True

    @property
    def mode(self) -> str:
        if self._online:
            return "online (Google)"
        if self._vosk:
            return "offline (Vosk)"
        return "indisponivel"
