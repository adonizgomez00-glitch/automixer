# TEST006 — Vista previa y reproducción (SPEC006). Puerto Playback con fake.
import os
import subprocess
import tempfile
import unittest

import paths  # noqa: F401

from src.adapters.fake_playback import FakePlayback
from src.services.mix_service import MixService


class PlaybackBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.playback = FakePlayback()
        # WAV real de 0.5 s (la duración se parsea de la cabecera RIFF).
        self.source = os.path.join(self.tmp.name, "preview.wav")
        subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
             "sine=frequency=440:duration=0.5",
             "-c:a", "pcm_s16le", "-ar", "44100", self.source],
            check=True, timeout=60,
        )
        self.source_ms = 500

    def tearDown(self):
        self.tmp.cleanup()


class Test006LoadAndTransport(PlaybackBase):
    def test_test006_ac01_load_enables_controls(self):
        res = self.playback.load(self.source)
        self.assertTrue(res.is_ok)
        self.assertTrue(self.playback.has_source())
        self.assertGreater(self.playback.duration_ms(), 0)
        self.assertLessEqual(self.playback.duration_ms(), self.source_ms + 100)

    def test_test006_ac02_play_starts_playback(self):
        self.playback.load(self.source)
        self.assertTrue(self.playback.play().is_ok)
        self.assertTrue(self.playback.is_playing())
        self.playback.advance(100)
        self.assertEqual(self.playback.position_ms(), 100)

    def test_test006_ac03_pause_keeps_position(self):
        self.playback.load(self.source)
        self.playback.play()
        self.playback.advance(200)
        self.assertTrue(self.playback.pause().is_ok)
        self.assertFalse(self.playback.is_playing())
        self.assertEqual(self.playback.position_ms(), 200)

    def test_test006_ac04_stop_returns_to_start(self):
        self.playback.load(self.source)
        self.playback.play()
        self.playback.advance(200)
        self.assertTrue(self.playback.stop().is_ok)
        self.assertFalse(self.playback.is_playing())
        self.assertEqual(self.playback.position_ms(), 0)

    def test_test006_ac05_seek_changes_position(self):
        self.playback.load(self.source)
        self.assertTrue(self.playback.seek(200).is_ok)
        self.assertEqual(self.playback.position_ms(), 200)
        self.assertTrue(self.playback.seek(-1).is_err)

    def test_test006_ac06_preview_volume_does_not_touch_mix(self):
        self.playback.load(self.source)
        self.assertTrue(self.playback.set_volume(0.3).is_ok)
        self.assertEqual(self.playback.volume, 0.3)
        self.assertTrue(self.playback.set_volume(1.5).is_err)


class Test006PendingMix(PlaybackBase):
    def _mix_service(self):
        return MixService(None, None, None, self.playback)  # type: ignore[arg-type]

    def test_test006_ac07_no_temp_file_no_playback(self):
        mix = self._mix_service()
        # Sin render previo: estado "mezcla pendiente de regenerar".
        res = mix.load_preview()
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "preview.pending_mix")
        self.assertFalse(self.playback.has_source())
        self.assertTrue(self.playback.play().is_err)
        self.assertFalse(self.playback.is_playing())

    def test_test006_ac07b_deleted_temp_reports_pending(self):
        mix = self._mix_service()
        mix._preview_path = self.source  # temporal "activo" ya eliminado del disco
        os.remove(self.source)
        res = mix.load_preview()
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "preview.pending_mix")

    def test_test006_ac01b_load_via_mix_service(self):
        mix = self._mix_service()
        mix._preview_path = self.source
        res = mix.load_preview()
        self.assertTrue(res.is_ok)
        self.assertTrue(self.playback.has_source())


if __name__ == "__main__":
    unittest.main()

