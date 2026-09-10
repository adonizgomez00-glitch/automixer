
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


SCHEMA_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class Genre(str, Enum):
    POP = "pop"
    ROCK = "rock"
    HIP_HOP = "hip_hop"


class StemType(str, Enum):
    VOZ = "voz"
    BATERIA = "bateria"
    BAJO = "bajo"
    GUITARRA = "guitarra"
    TECLADOS = "teclados"
    SINTETIZADORES = "sintetizadores"
    DROPS = "drops"
    EFECTOS = "efectos"
    OTRO = "otro"


@dataclass
class StemCorrections:
    """Correcciones no destructivas de tempo/alineación y desfase manual (D4).
    Cada campo `None` significa 'sin corrección aplicada'."""

    tempo_ratio: Optional[float] = None
    start_offset_ms: Optional[int] = None
    confidence: Optional[float] = None
    manual_offset_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tempo_ratio": self.tempo_ratio,
            "start_offset_ms": self.start_offset_ms,
            "confidence": self.confidence,
            "manual_offset_ms": self.manual_offset_ms,
        }

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> "StemCorrections":
        d = d or {}
        return cls(
            tempo_ratio=d.get("tempo_ratio"),
            start_offset_ms=d.get("start_offset_ms"),
            confidence=d.get("confidence"),
            manual_offset_ms=d.get("manual_offset_ms"),
        )


@dataclass
class Stem:
    path: str
    type: StemType = StemType.OTRO
    gain_db: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    corrections: StemCorrections = field(default_factory=StemCorrections)
    # Transitorio: derivado en carga desde el sistema de ficheros, no se persiste.
    available: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "path": self.path,
            "type": self.type.value,
            "gain_db": self.gain_db,
            "corrections": self.corrections.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Stem":
        return cls(
            id=str(d.get("id") or uuid.uuid4()),
            path=str(d.get("path") or ""),
            type=_stem_type(str(d.get("type") or "otro")),
            gain_db=float(d.get("gain_db", 0.0)),
            corrections=StemCorrections.from_dict(d.get("corrections")),
        )

    @property
    def manual_offset_ms(self) -> Optional[int]:
        return self.corrections.manual_offset_ms

    @manual_offset_ms.setter
    def manual_offset_ms(self, value: Optional[int]) -> None:
        self.corrections.manual_offset_ms = value


def _stem_type(value: str) -> StemType:
    for member in StemType:
        if member.value == value:
            return member
    return StemType.OTRO


def _genre(value: str) -> Genre:
    for member in Genre:
        if member.value == value:
            return member
    return Genre.POP


@dataclass
class MixProject:
    """Proyecto de una sola canción (esquema `.automixer` v1)."""

    name: str
    genre: Genre = Genre.POP
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reference_stem_id: Optional[str] = None
    stems: list[Stem] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "id": self.id,
            "name": self.name,
            "genre": self.genre.value,
            "reference_stem_id": self.reference_stem_id,
            "stems": [s.to_dict() for s in self.stems],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MixProject":
        """Reconstruye un proyecto: schema_version 1 es la única soportada."""
        schema = d.get("schema_version")
        if schema != SCHEMA_VERSION:
            raise ValueError(f"unsupported schema_version: {schema}")
        return cls(
            id=str(d.get("id") or uuid.uuid4()),
            name=str(d.get("name") or ""),
            genre=_genre(str(d.get("genre") or "pop")),
            reference_stem_id=d.get("reference_stem_id"),
            stems=[Stem.from_dict(s) for s in d.get("stems", [])],
            created_at=str(d.get("created_at") or _now()),
            updated_at=str(d.get("updated_at") or _now()),
        )

    def add_stem(self, stem: Stem) -> None:
        self.stems.append(stem)

    def find_stem(self, stem_id: str) -> Optional[Stem]:
        for stem in self.stems:
            if stem.id == stem_id:
                return stem
        return None

    def mark_updated(self) -> None:
        self.updated_at = _now()
