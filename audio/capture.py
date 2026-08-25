import queue
import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 8000
DTYPE = "int16"


class AudioCapture:
    def __init__(self):
        self._queue: queue.Queue[bytes] = queue.Queue()
        self._stream = None
        self._running = False

    def _callback(self, indata, frames, time, status):
        if status:
            pass
        self._queue.put(bytes(indata))

    def start(self):
        self._running = True
        self._stream = sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype=DTYPE,
            channels=CHANNELS,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self):
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def get_chunk(self, timeout=1.0) -> bytes | None:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    @property
    def is_running(self) -> bool:
        return self._running

    def list_devices(self) -> list[dict]:
        devices = sd.query_devices()
        return [
            {"index": i, "name": d["name"], "channels": d["max_input_channels"]}
            for i, d in enumerate(devices)
            if d["max_input_channels"] > 0
        ]
