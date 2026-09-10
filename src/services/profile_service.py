from __future__ import annotations
import json
import os
import sys
from typing import Optional

from ..models.mix_profile import GenreProfile, MixNormalization, StemProfile
from ..models.project import Genre, MixProject, Stem, StemType


def _default_resources_path() -> str:
    """Ruta de `profiles.json`: bundle PyInstaller (`sys._MEIPASS`) o fuente."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, "src", "resources", "profiles.json")
    return os.path.join(os.path.dirname(__file__), "..", "resources", "profiles.json")


_RESOURCES = _default_resources_path()


class ProfileService:
    """Carga los perfiles fijos (JSON, decision D1) y calcula ajustes por stem."""

    _PROFILE_TYPE_KEYS = {
        StemType.VOZ: "voz",
        StemType.BATERIA: "bateria",
        StemType.BAJO: "bajo",
        StemType.GUITARRA: "guitarra",
        StemType.TECLADOS: "teclados",
        StemType.SINTETIZADORES: "sintetizadores",
        StemType.DROPS: "drops",
        StemType.EFECTOS: "efectos",
        StemType.OTRO: "otro",
    }

    def __init__(self, path: Optional[str] = None) -> None:
        self._path = path or _RESOURCES
        self._genres: dict[Genre, GenreProfile] = {}
        self._load()

    def _load(self) -> None:
        with open(self._path, encoding="utf-8") as fh:
            data = json.load(fh)
        norm = data["normalization"]
        profiles = data["profiles"]
        for genre in Genre:
            key = genre.value
            gdata = profiles.get(key, {})
            stem_map = {}
            for stype, skey in self._PROFILE_TYPE_KEYS.items():
                if stype == StemType.OTRO:
                    continue
                stem_map[stype] = StemProfile.from_dict(gdata.get(skey, {}))
            ns = norm.get(key)
            normalization = MixNormalization(
                lufs=float(ns["lufs"]), true_peak_db=float(ns["true_peak"])
            ) if ns else None
            neutral = StemProfile.from_dict(gdata.get("otro", {}))
            self._genres[genre] = GenreProfile(
                stems=stem_map, normalization=normalization, neutral=neutral
            )

    def genre_profile(self, genre: Genre) -> GenreProfile:
        return self._genres.get(genre, GenreProfile())

    def profile_for(self, genre: Genre, stem_type: StemType) -> StemProfile:
        return self.genre_profile(genre).profile_for(stem_type)

    def default_gain(self, genre: Genre, stem_type: StemType) -> float:
        return self.profile_for(genre, stem_type).gain_base_db

    def normalization(self, genre: Genre) -> Optional[MixNormalization]:
        return self.genre_profile(genre).normalization

    def apply_defaults(self, project: MixProject, stem: Stem) -> Stem:
        """Aplica la ganancia base del perfil activo al stem (al clasificar). SPEC003 AC-02."""
        stem.gain_db = self.default_gain(project.genre, stem.type)
        return stem

    def pan_for_stem(self, project: MixProject, stem: Stem) -> float:
        """Paneo alternado por tipo: -X con un solo stem, +-X por posicion."""
        profile = self.profile_for(project.genre, stem.type)
        mag = profile.pan_magnitude
        if mag == 0:
            return 0.0
        same_type = [s for s in project.stems if s.type == stem.type]
        if len(same_type) <= 1:
            return -mag
        index = same_type.index(stem)
        return mag if index % 2 == 1 else -mag

    def reset_gain(self, project: MixProject, stem: Stem) -> Stem:
        """Restablece solo la ganancia al perfil activo (cambio de genero)."""
        stem.gain_db = self.default_gain(project.genre, stem.type)
        return stem

    def reset_stem(self, project: MixProject, stem: Stem) -> Stem:
        """Restablecer: ganancia, correcciones y desfase al perfil activo. SPEC003 AC-07 / SPEC004 AC-08."""
        self.reset_gain(project, stem)
        stem.corrections.tempo_ratio = None
        stem.corrections.start_offset_ms = None
        stem.corrections.confidence = None
        stem.corrections.manual_offset_ms = None
        return stem
