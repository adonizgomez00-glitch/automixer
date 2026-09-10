from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from .project import StemType


@dataclass
class EqBand:
    gain_db: float
    freq_hz: float


@dataclass
class Compressor:
    threshold_db: float
    ratio: float
    attack_ms: float
    release_ms: float


@dataclass
class StemProfile:
    """Parámetros fijos de mezcla para un género/tipo (decisión D1)."""

    gain_base_db: float = 0.0
    pan_magnitude: float = 0.0          # 0 = centro; si >0 el signo alterna por stem del mismo tipo
    hpf_hz: Optional[float] = None
    eq: List[EqBand] = field(default_factory=list)
    compressor: Optional[Compressor] = None
    makeup_gain_db: float = 0.0

    @classmethod
    def from_dict(cls, d: dict) -> "StemProfile":
        eq = [EqBand(gain_db=b["gain"], freq_hz=b["freq"]) for b in d.get("eq", [])]
        comp = d.get("compressor")
        compressor = (
            Compressor(
                threshold_db=comp["threshold"],
                ratio=comp["ratio"],
                attack_ms=comp["attack_ms"],
                release_ms=comp["release_ms"],
            )
            if comp
            else None
        )
        return cls(
            gain_base_db=d.get("gain_base", 0.0),
            pan_magnitude=d.get("pan", 0.0),
            hpf_hz=d.get("hpf"),
            eq=eq,
            compressor=compressor,
            makeup_gain_db=d.get("makeup_gain", 0.0),
        )


@dataclass
class MixNormalization:
    lufs: float
    true_peak_db: float


@dataclass
class GenreProfile:
    stems: dict[StemType, StemProfile] = field(default_factory=dict)
    normalization: Optional[MixNormalization] = None
    neutral: StemProfile = field(default_factory=StemProfile)

    def profile_for(self, stem_type: StemType) -> StemProfile:
        if stem_type == StemType.OTRO:
            return self.neutral
        return self.stems.get(stem_type, self.neutral)
