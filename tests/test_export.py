# TEST007 — Exportación de mezcla (SPEC007). Motor FFmpeg real.
import os
import subprocess
import tempfile
import unittest

import paths  # noqa: F401

from src.adapters.ffmpeg_engine import FFmpegEngine
from src.adapters.fake_playback import FakePlayback
from src.adapters.temp_artifact_store import TempArtifactStore
from src.models.project import StemType
from src.ports.audio import ExportFormat
from src.repositories.json_project_repository import JsonProjectRepository
from src.repositories.settings_repository import FileSettingsRepository
from src.services.mix_service import MixService
from src.services.profile_service import ProfileService
from src.services.project_service import ProjectService


def _probe(path, entries):
    out = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", entries,
            "-of", "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True, text=True, timeout=60,
    )
    return [l.strip() for l in out.stdout.strip().splitlines() if l.strip()]


class ExportBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.engine = FFmpegEngine()
        self.mix = MixService(
            ProfileService(), self.engine, TempArtifactStore(), FakePlayback()
        )
        self.repo = JsonProjectRepository()
        self.settings = FileSettingsRepository(
            os.path.join(self.tmp.name, "cfg", "s.json")
        )
        self.svc = ProjectService(
            self.repo, self.settings, profile=ProfileService(), engine=self.engine
        )
        self.svc.create("cancion", self.tmp.name)
        self._add_stem()

    def tearDown(self):
        self.tmp.cleanup()

    def _add_stem(self, seconds=2.0):
        path = os.path.join(self.tmp.name, "voz.wav")
        subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
             f"sine=frequency=440:duration={seconds}",
             "-c:a", "pcm_s16le", "-ar", "44100", path],
            check=True, timeout=120,
        )
        res = self.svc.add_stem(path, StemType.VOZ)
        assert res.is_ok
        return res.value

    def _export(self, fmt, name="mezcla", overwrite=False):
        dest = os.path.join(self.tmp.name, f"{name}.{fmt.value}")
        return self.mix.export(self.svc.active_project, dest, fmt, overwrite=overwrite), dest


class Test007Formats(ExportBase):
    def test_test007_ac01_export_wav_44100_24bit(self):
        res, dest = self._export(ExportFormat.WAV_44100_24)
        self.assertTrue(res.is_ok)
        self.assertTrue(os.path.isfile(dest))
        self.assertEqual(_probe(dest, "stream=codec_name"), ["pcm_s24le"])
        self.assertEqual(_probe(dest, "stream=sample_rate"), ["44100"])

    def test_test007_ac02_export_mp3_320kbps(self):
        res, dest = self._export(ExportFormat.MP3_320)
        self.assertTrue(res.is_ok)
        self.assertTrue(os.path.isfile(dest))
        self.assertEqual(_probe(dest, "stream=codec_name"), ["mp3"])
        bit_rate = int(_probe(dest, "format=bit_rate")[0])
        self.assertGreater(bit_rate, 300_000)
        self.assertLessEqual(bit_rate, 330_000)


class Test007Overwrite(ExportBase):
    def test_test007_ac03_no_overwrite_without_confirmation(self):
        res1, dest = self._export(ExportFormat.WAV_44100_24)
        self.assertTrue(res1.is_ok)
        with open(dest, "rb") as fh:
            before = fh.read()
        res2 = self.mix.export(
            self.svc.active_project, dest, ExportFormat.WAV_44100_24, overwrite=False
        )
        self.assertTrue(res2.is_err)
        self.assertEqual(res2.error.code, "export.overwrite_confirmation")
        with open(dest, "rb") as fh:
            self.assertEqual(fh.read(), before)

    def test_test007_ac04_overwrite_with_confirmation(self):
        res1, dest = self._export(ExportFormat.WAV_44100_24)
        self.assertTrue(res1.is_ok)
        res2 = self.mix.export(
            self.svc.active_project, dest, ExportFormat.MP3_320, overwrite=True
        )
        self.assertTrue(res2.is_ok)
        self.assertEqual(_probe(dest, "stream=codec_name"), ["mp3"])

    def test_test007_ac05_cancelled_dialog_creates_nothing(self):
        res = self.mix.export(
            self.svc.active_project, None, ExportFormat.WAV_44100_24
        )
        self.assertTrue(res.is_err)
        leftovers = [f for f in os.listdir(self.tmp.name) if f.startswith("mezcla")]
        self.assertEqual(leftovers, [])


class Test007FailuresAndPersistence(ExportBase):
    def test_test007_ac06_write_failure_keeps_project(self):
        ro = os.path.join(self.tmp.name, "ro")
        os.makedirs(ro)
        os.chmod(ro, 0o500)
        if os.access(ro, os.W_OK):
            self.skipTest("el usuario actual puede escribir en un dir 0500")
        dest = os.path.join(ro, "mezcla.wav")
        res = self.mix.export(
            self.svc.active_project, dest, ExportFormat.WAV_44100_24
        )
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "export.failed")
        # El proyecto sigue intacto y los stems no se modifican.
        self.assertEqual(len(self.svc.active_project.stems), 1)
        self.assertTrue(os.path.isfile(self.svc.active_project.stems[0].path))

    def test_test007_ac07_exported_file_survives_close(self):
        res, dest = self._export(ExportFormat.WAV_44100_24)
        self.assertTrue(res.is_ok)
        # Render de un temporal de preview y cierre de la mezcla.
        preview = self.mix.render_preview(self.svc.active_project)
        self.assertTrue(preview.is_ok)
        self.mix.close()
        # El archivo exportado NO se elimina; el temporal propio sí.
        self.assertTrue(os.path.isfile(dest))
        self.assertIsNone(self.mix.preview_path)


if __name__ == "__main__":
    unittest.main()

