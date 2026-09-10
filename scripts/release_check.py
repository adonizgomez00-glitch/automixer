from __future__ import annotations

"""Gate de release (SPEC010 AC-06/AC-07).

Valida una distribución empaquetada devolviendo la lista de incumplimientos:

- Existencia y contenido de `LICENSES.md` (avisos de FFmpeg/códecs/PySide6/Python).
  Un paquete sin `LICENSES.md` se rechaza (AC-07).
- Presencia de `ffmpeg`/`ffmpeg.exe` en `resources/` (AC-06).

Uso:
    python scripts/release_check.py dist/automixer
exit code 0 = válido; 1 = se rechaza el release.
"""

import argparse
import os
import sys
from typing import List


# Marcadores obligatorios en LICENSES.md (comparación case-insensitive).
REQUIRED_MARKERS = ("ffmpeg", "lame", "pyside", "python")


def _ffmpeg_name() -> str:
    return "ffmpeg.exe" if os.name == "nt" else "ffmpeg"


def _probe_license_markers(path: os.PathLike | str) -> List[str]:
    """Devuelve los marcadores ausentes en el fichero de avisos."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read().lower()
    except OSError:
        return list(REQUIRED_MARKERS)
    return [m for m in REQUIRED_MARKERS if m not in text]


def validate_bundle(bundle_dir: os.PathLike | str) -> List[str]:
    """Valida un bundle y devuelve la lista de incumplimientos (vacía = OK)."""
    bundle_dir = os.fspath(bundle_dir)
    errors: List[str] = []

    licenses_path = os.path.join(bundle_dir, "LICENSES.md")
    if not os.path.isfile(licenses_path):
        errors.append("LICENSES.md ausente: se rechaza el release (SPEC010 AC-07).")
    else:
        missing = _probe_license_markers(licenses_path)
        if missing:
            errors.append(
                "LICENSES.md no incluye los avisos requeridos: "
                + ", ".join(missing)
                + "."
            )

    ffmpeg_path = os.path.join(bundle_dir, "resources", _ffmpeg_name())
    if not os.path.isfile(ffmpeg_path):
        errors.append(
            f"FFmpeg ({_ffmpeg_name()}) ausente en resources/ (SPEC010 AC-06)."
        )

    return errors


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate de release de AutoMixer")
    parser.add_argument("bundle_dir", help="Directorio del bundle (p. ej. dist/automixer)")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.bundle_dir):
        print(f"[release] No existe el bundle: {args.bundle_dir}", file=sys.stderr)
        return 1

    errors = validate_bundle(args.bundle_dir)
    if errors:
        print("[release] REJECTED: el paquete no supera el gate de release.")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("[release] OK: el paquete incluye FFmpeg y los avisos de licencia requeridos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())