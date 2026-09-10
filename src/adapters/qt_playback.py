from __future__ import annotations
import os
from typing import Optional

from ..ports.playback import Playback
from ..utils.result import DomainError, Result

try:  # PySide6 es opcional en pruebas headless
    from PySide6.QtCore import QUrl
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

    _QT = True
except Exception:  # noqa: BLE001 - sin entorno gráfico/multimedia
    _QT = False


class QtPlayback(Playback):
    """Reproductor de preview con QtMultimedia sobre el WAV temporal (SPEC006).

    El volumen actúa solo sobre la salida de audio (QAudioOutput), nunca sobre
    los ajustes de mezcla (SPEC006 AC-06). Requiere PySide6 instalado.
    """

    def __init__(self) -> None:
        if not _QT:
            raise RuntimeError(
                "PySide6/QtMultimedia no está disponible en este entorno."
            )
        self._player = QMediaPlayer()
        self._audio = QAudioOutput()
        self._player.setAudioOutput(self._audio)
        self._audio.setVolume(0.8)
        self._path: Optional[str] = None

    def load(self, path: str) -> Result:
        if not path or not os.path.isfile(path):
            return Result.err(DomainError("preview.source_missing"))
        self._player.stop()
        self._player.setSource(QUrl.fromLocalFile(path))
        self._path = path
        return Result.ok(path)

    def has_source(self) -> bool:
        return self._path is not None and os.path.isfile(self._path)

    def unload(self) -> None:
        self._player.stop()
        self._player.setSource(QUrl())
        self._path = None

    def play(self) -> Result:
        if not self.has_source():
            return Result.err(DomainError("preview.pending_mix"))
        self._player.play()
        return Result.ok()

    def pause(self) -> Result:
        if not self.has_source():
            return Result.err(DomainError("preview.pending_mix"))
        self._player.pause()
        return Result.ok()

    def stop(self) -> Result:
        if not self.has_source():
            return Result.err(DomainError("preview.pending_mix"))
        self._player.stop()
        return Result.ok()

    def seek(self, position_ms: int) -> Result:
        if not self.has_source():
            return Result.err(DomainError("preview.pending_mix"))
        if position_ms < 0:
            return Result.err(DomainError("preview.seek_out_of_range"))
        self._player.setPosition(int(position_ms))
        return Result.ok()

    def set_volume(self, volume: float) -> Result:
        if not 0.0 <= volume <= 1.0:
            return Result.err(DomainError("preview.volume_out_of_range"))
        self._audio.setVolume(float(volume))
        return Result.ok()

    def position_ms(self) -> int:
        return int(self._player.position())

    def duration_ms(self) -> int:
        return int(self._player.duration())

    def is_playing(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
