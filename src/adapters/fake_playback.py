from __future__ import annotations
import os
from typing import Optional

from ..ports.playback import Playback
from ..utils.result import DomainError, Result


class FakePlayback(Playback):
    """Reproductor de estado para pruebas headless (TEST006).

    Simula un reloj de reproducción determinista: `play` avanza la posición
    con `advance(ms)`; no requiere QtMultimedia ni dispositivo de audio.
    """

    def __init__(self) -> None:
        self._path: Optional[str] = None
        self._duration_ms = 0
        self._position_ms = 0
        self._playing = False
        self._volume = 0.8

    # --- ciclo de vida ---

    def load(self, path: str) -> Result:
        if not path or not os.path.isfile(path):
            return Result.err(DomainError("preview.source_missing"))
        self._path = path
        self._duration_ms = self._probe_duration_ms(path)
        self._position_ms = 0
        self._playing = False
        return Result.ok(path)

    def has_source(self) -> bool:
        return self._path is not None and os.path.isfile(self._path)

    def unload(self) -> None:
        self._path = None
        self._duration_ms = 0
        self._position_ms = 0
        self._playing = False

    # --- transporte ---

    def play(self) -> Result:
        if not self.has_source():
            return Result.err(DomainError("preview.pending_mix"))
        self._playing = True
        return Result.ok()

    def pause(self) -> Result:
        if not self.has_source():
            return Result.err(DomainError("preview.pending_mix"))
        self._playing = False
        return Result.ok()

    def stop(self) -> Result:
        if not self.has_source():
            return Result.err(DomainError("preview.pending_mix"))
        self._playing = False
        self._position_ms = 0
        return Result.ok()

    def seek(self, position_ms: int) -> Result:
        if not self.has_source():
            return Result.err(DomainError("preview.pending_mix"))
        if position_ms < 0:
            return Result.err(DomainError("preview.seek_out_of_range"))
        self._position_ms = min(position_ms, self._duration_ms)
        return Result.ok()

    def set_volume(self, volume: float) -> Result:
        if not 0.0 <= volume <= 1.0:
            return Result.err(DomainError("preview.volume_out_of_range"))
        self._volume = volume
        return Result.ok()

    # --- estado ---

    def position_ms(self) -> int:
        return self._position_ms

    def duration_ms(self) -> int:
        return self._duration_ms

    def is_playing(self) -> bool:
        return self._playing

    @property
    def volume(self) -> float:
        return self._volume

    # --- utilidades de prueba ---

    def advance(self, ms: int) -> None:
        """Hace avanzar el reloj simulado (solo pruebas)."""
        if not self._playing:
            return
        self._position_ms = min(self._position_ms + ms, self._duration_ms)
        if self._position_ms >= self._duration_ms:
            self._playing = False

    def set_duration(self, ms: int) -> None:
        """Fija la duración simulada del temporal (solo pruebas)."""
        self._duration_ms = max(0, ms)

    def _probe_duration_ms(self, path: str) -> int:
        """Duración real del WAV: parser RIFF que busca el chunk ``data``."""
        try:
            with open(path, "rb") as fh:
                head = fh.read(12)
                if len(head) < 12 or head[:4] != b"RIFF" or head[8:12] != b"WAVE":
                    return 0
                channels = rate = bits = 0
                data_size = 0
                while True:
                    chunk = fh.read(8)
                    if len(chunk) < 8:
                        break
                    tag = chunk[:4]
                    size = int.from_bytes(chunk[4:8], "little")
                    if tag == b"fmt ":
                        body = fh.read(min(size, 40))
                        if len(body) >= 16:
                            channels = int.from_bytes(body[2:4], "little")
                            rate = int.from_bytes(body[4:8], "little")
                            bits = int.from_bytes(body[14:16], "little")
                        else:
                            fh.seek(size - len(body), 1)
                        if size % 2:
                            fh.seek(1, 1)
                    elif tag == b"data":
                        data_size = size
                        break
                    else:
                        fh.seek(size + (size % 2), 1)
                block = rate * channels * (bits // 8)
                if block <= 0:
                    return 0
                return int(data_size / block * 1000)
        except OSError:
            return 0
