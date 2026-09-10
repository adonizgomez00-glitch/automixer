from __future__ import annotations

"""Empaquetado de AutoMixer (SPEC010, decisión D5).

Genera un bundle `--onedir` con PyInstaller y lo deja listo para distribución:

1. Ejecuta PyInstaller `--onedir --name automixer` sobre `src.app`.
2. Copia `ffmpeg`/`ffmpeg.exe` (y `ffprobe`/`ffprobe.exe`) a `<bundle>/resources/`.
   Fuente: primero el binario del PATH; alternativas en `--ffmpeg-dir`.
3. Copia `LICENSES.md` a la raíz del bundle.
4. Ejecuta el gate de release (`release_check`): si falla, aborta con código 1.

Uso:
    python scripts/build.py                # usa el ffmpeg del PATH
    python scripts/build.py --ffmpeg-dir DIR
    python scripts/build.py --skip-pyinstaller --bundle-dir dist/automixer   # solo empaqueta deps
"""

import argparse
import os
import shutil
import subprocess
import sys

from release_check import validate_bundle

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_BUNDLE_NAME = "automixer"
LICENSES_SOURCE = os.path.join(PROJECT_ROOT, "LICENSES.md")


def _tool(tool: str) -> str:
    exe = tool + (".exe" if os.name == "nt" else "")
    found = shutil.which(exe)
    if found:
        return found
    raise SystemExit(f"[build] No se encontró {exe} en el PATH.")


def _find_ffmpeg(ffmpeg_dir: os.PathLike | str | None) -> tuple[str, str]:
    """Devuelve (ffmpeg, ffprobe); prioriza `ffmpeg_dir`, luego el PATH."""
    exes = ("ffmpeg", "ffprobe")
    if ffmpeg_dir:
        ffmpeg_dir = os.fspath(ffmpeg_dir)
        paths = {}
        for exe in exes:
            cand = os.path.join(ffmpeg_dir, exe + (".exe" if os.name == "nt" else ""))
            if not os.path.isfile(cand):
                raise SystemExit(f"[build] Falta {exe} en --ffmpeg-dir {ffmpeg_dir}")
            paths[exe] = cand
        return paths["ffmpeg"], paths["ffprobe"]
    return _tool("ffmpeg"), _tool("ffprobe")


def _copy_ffmpeg(bundle_dir: str, ffmpeg_dir: os.PathLike | str | None) -> None:
    resources = os.path.join(bundle_dir, "resources")
    os.makedirs(resources, exist_ok=True)
    ffmpeg, ffprobe = _find_ffmpeg(ffmpeg_dir)
    names = ("ffmpeg", "ffprobe")
    for src, base in ((ffmpeg, "ffmpeg"), (ffprobe, "ffprobe")):
        dest = os.path.join(
            resources, base + (".exe" if os.name == "nt" else "")
        )
        shutil.copy2(src, dest)


def _add_data_spec() -> str:
    """`--add-data` para `profiles.json` (separador `;` en Windows, `:` en …)."""
    sep = ";" if os.name == "nt" else ":"
    return (
        os.path.join(PROJECT_ROOT, "src", "resources", "profiles.json")
        + sep
        + "src/resources"
    )


def _run_pyinstaller(bundle_name: str) -> str:
    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:  # noqa: BLE001
        raise SystemExit(
            "[build] PyInstaller no está instalado. Ejecuta: pip install pyinstaller"
        ) from exc
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onedir",
        "--name", bundle_name,
        "--log-level", "WARN",
        "--add-data", _add_data_spec(),
        os.path.join(PROJECT_ROOT, "entrypoint.py"),
    ]
    subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)
    return os.path.join("dist", bundle_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Empaqueta AutoMixer (D5)")
    parser.add_argument("--bundle-name", default=DEFAULT_BUNDLE_NAME)
    parser.add_argument("--ffmpeg-dir", default=None, help="Carpeta con ffmpeg/ffprobe")
    parser.add_argument("--skip-pyinstaller", action="store_true")
    parser.add_argument("--bundle-dir", default=None)
    args = parser.parse_args(argv)

    if args.skip_pyinstaller:
        if not args.bundle_dir:
            parser.error("--bundle-dir es obligatorio con --skip-pyinstaller")
        bundle_dir = args.bundle_dir
    else:
        bundle_dir = _run_pyinstaller(args.bundle_name)

    bundle_abs = (
        bundle_dir
        if os.path.isabs(bundle_dir)
        else os.path.join(PROJECT_ROOT, bundle_dir)
    )

    _copy_ffmpeg(bundle_abs, args.ffmpeg_dir)

    if os.path.isfile(LICENSES_SOURCE):
        shutil.copy2(LICENSES_SOURCE, os.path.join(bundle_abs, "LICENSES.md"))
    else:
        print("[build] Aviso: no existe LICENSES.md en la raíz; el gate lo rechazará.")

    errors = validate_bundle(bundle_abs)
    if errors:
        print("[build] Gate de release fallido:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"[build] OK. Bundle listo: {bundle_abs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())