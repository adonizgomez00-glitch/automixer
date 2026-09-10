# TEST010 — Empaquetado y gate de release (SPEC010 AC-06/AC-07).
import os
import tempfile
import unittest

import paths  # noqa: F401

import sys

sys.path.insert(0, os.path.join(paths.WORKSPACE, "scripts"))
from release_check import validate_bundle  # noqa: E402

LICENSES_OK = """# Avisos
## FFmpeg (LGPLv2.1+)
## LAME (LGPL)
## PySide6 (LGPLv3)
## Python (PSF)
"""


def _make_bundle(root, *, with_licenses=True, licenses_text=LICENSES_OK):
    bundle = os.path.join(root, "automixer")
    os.makedirs(os.path.join(bundle, "resources"), exist_ok=True)
    ffmpeg = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    with open(os.path.join(bundle, "resources", ffmpeg), "w", encoding="utf-8") as fh:
        fh.write("bin")
    if with_licenses:
        with open(os.path.join(bundle, "LICENSES.md"), "w", encoding="utf-8") as fh:
            fh.write(licenses_text)
    return bundle


class Test010ReleaseGate(unittest.TestCase):
    def test_ac06_bundle_includes_ffmpeg_and_notices(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = _make_bundle(td)
            self.assertEqual(validate_bundle(bundle), [])

    def test_ac07_package_without_licenses_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = _make_bundle(td, with_licenses=False)
            errors = validate_bundle(bundle)
            self.assertTrue(any("LICENSES.md" in e for e in errors))

    def test_ac07_licenses_missing_markers_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = _make_bundle(
                td, licenses_text="# Solo FFmpeg, sin códecs ni Python.\n"
            )
            errors = validate_bundle(bundle)
            # Deben faltar lame, pyside y/o python.
            self.assertTrue(any("avisos requeridos" in e for e in errors))

    def test_ac06_missing_ffmpeg_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = _make_bundle(td)
            ffmpeg = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
            os.remove(os.path.join(bundle, "resources", ffmpeg))
            errors = validate_bundle(bundle)
            self.assertTrue(any("FFmpeg" in e and "resources" in e for e in errors))


if __name__ == "__main__":
    unittest.main()