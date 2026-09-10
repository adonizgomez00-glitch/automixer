# TEST005 — Renderizado de mezcla temporal (SPEC005). Motor FFmpeg real.
import os
import subprocess
import tempfile
import unittest

import paths  # noqa: F401

from src.adapters.ffmpeg_engine import FFmpegEngine
from src.adapters.fake_playback import FakePlayback
from src.adapters.temp_artifact_store import TempArtifactStore
from src.models.project import Genre, StemType
from src.ports.audio import RenderStem
from src.repositories.json_project_repository import JsonProjectRepository
from src.repositories.settings_repository import FileSettingsRepository
from src.services.mix_service import MixService
from src.services.profile_service import ProfileService
from src.services.project_service import ProjectService


def _ffprobe(path, entries):
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


class RenderBase(unittest.TestCase):
    """Proyecto real con stems WAV sintéticos generados con FFmpeg."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.engine = FFmpegEngine()
        self.artifacts = TempArtifactStore()
        self.playback = FakePlayback()
        self.profile = ProfileService()
        self.repo = JsonProjectRepository()
        self.settings = FileSettingsRepository(
            os.path.join(self.tmp.name, "cfg", "s.json")
        )
        self.svc = ProjectService(
            self.repo, self.settings, profile=self.profile, engine=self.engine
        )
        self.svc.create("cancion", self.tmp.name)
        self.mix = MixService(self.profile, self.engine, self.artifacts, self.playback)
        self._synth = 0

    def tearDown(self):
        self.mix.close()
        self.tmp.cleanup()

    def synth(self, seconds=2.0, freq=440):
        """Crea un stem WAV sintético y lo importa clasificado."""
        self._synth += 1
        path = os.path.join(self.tmp.name, f"stem{self._synth}.wav")
        subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
             f"sine=frequency={freq}:duration={seconds}",
             "-c:a", "pcm_s16le", "-ar", "44100", path],
            check=True, timeout=120,
        )
        return path

    def add(self, stype, seconds=2.0, freq=440):
        path = self.synth(seconds, freq)
        res = self.svc.add_stem(path, stype)
        assert res.is_ok
        return res.value


class Test005RenderTemporal(RenderBase):
    def test_test005_ac01_render_starts_with_valid_stem(self):
        self.add(StemType.VOZ)
        res = self.mix.render_preview(self.svc.active_project)
        self.assertTrue(res.is_ok)
        self.assertTrue(os.path.isfile(res.value))
        self.assertTrue(res.value.endswith(".wav"))

    def test_test005_ac02_no_valid_stems_blocks_render(self):
        res = self.mix.render_preview(self.svc.active_project)
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "project.no_valid_stems")
        self.assertFalse(self.svc.mix_enabled)


class Test005RenderOutput(RenderBase):
    def test_test005_ac03_output_is_stereo_playable_wav(self):
        self.add(StemType.VOZ)
        res = self.mix.render_preview(self.svc.active_project)
        self.assertTrue(res.is_ok)
        codec = _ffprobe(res.value, "stream=codec_name")
        channels = _ffprobe(res.value, "stream=channels")
        self.assertEqual(codec, ["pcm_s16le"])
        self.assertEqual(channels, ["2"])

    def test_test005_ac04_mix_last_until_longest_stem(self):
        self.add(StemType.VOZ, seconds=2.0)
        self.add(StemType.BAJO, seconds=3.0)
        res = self.mix.render_preview(self.svc.active_project)
        self.assertTrue(res.is_ok)
        duration = int(self.engine.duration_ms(res.value))
        self.assertGreaterEqual(duration, 2900)
        self.assertLessEqual(duration, 3400)

    def test_test005_ac05_render_applies_active_settings(self):
        # Consolidación de ajustes: perfil + manual + correcciones (offset manual con prioridad).
        stem = self.add(StemType.GUITARRA, seconds=2.0)
        self.svc.set_gain(stem.id, -6.0)
        stem.corrections.tempo_ratio = 1.0  # sin cambio de tempo
        stem.corrections.manual_offset_ms = 1000  # prioridad sobre auto (SPEC004)
        built = self.mix.build_render_stems(self.svc.active_project)
        self.assertEqual(len(built), 1)
        rs = built[0]
        self.assertEqual(rs.gain_db, -6.0)
        self.assertNotEqual(rs.pan, 0.0)  # guitarra en pop tiene paneo ±0.15
        self.assertEqual(rs.offset_ms, 1000)
        # El render aplica el desfase: 2 s de stem + 1 s de retardo.
        res = self.mix.render_preview(self.svc.active_project)
        self.assertTrue(res.is_ok)
        duration = int(self.engine.duration_ms(res.value))
        self.assertGreaterEqual(duration, 2900)
        self.assertLessEqual(duration, 3400)


class Test005RenderFailures(RenderBase):
    def test_test005_ac06_failure_keeps_previous_preview(self):
        self.add(StemType.VOZ)
        first = self.mix.render_preview(self.svc.active_project)
        self.assertTrue(first.is_ok)
        prev_path = first.value
        before = os.path.getsize(prev_path)
        # El stem se corrompe: el siguiente render falla.
        with open(self.svc.active_project.stems[0].path, "wb") as fh:
            fh.write(b"not audio")
        second = self.mix.render_preview(self.svc.active_project)
        self.assertTrue(second.is_err)
        # La preview válida anterior se conserva (SPEC005 AC-06).
        self.assertEqual(self.mix.preview_path, prev_path)
        self.assertTrue(os.path.isfile(prev_path))
        self.assertEqual(os.path.getsize(prev_path), before)

    def test_test005_ac07_cancel_cleans_partial(self):
        self.add(StemType.VOZ, seconds=2.0)
        res = self.mix.render_preview(
            self.svc.active_project, cancel=lambda: True
        )
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "job.cancelled")
        self.assertIsNone(self.mix.preview_path)
        # No quedan temporales propios del trabajo cancelado.
        leftovers = os.listdir(self.artifacts.base_dir)
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()

