# TEST003 — Perfiles de mezcla y controles por stem (SPEC003, decisión D1).
import os
import tempfile
import unittest

import paths  # noqa: F401

from src.models.project import Genre, StemType
from src.repositories.json_project_repository import JsonProjectRepository
from src.repositories.settings_repository import FileSettingsRepository
from src.services.profile_service import ProfileService
from src.services.project_service import ProjectService


def _touch(tmp, rel):
    p = os.path.join(tmp, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(b"audio")
    return p


def _svc(tmp):
    repo = JsonProjectRepository()
    settings = FileSettingsRepository(os.path.join(tmp, "cfg", "settings.json"))
    profile = ProfileService()
    return ProjectService(repo, settings, profile=profile), profile


class Test003GenreDefault(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_test003_ac01_initial_genre_is_pop(self):
        svc, _ = _svc(self.tmp.name)
        svc.create("cancion", self.tmp.name)
        self.assertEqual(svc.active_project.genre, Genre.POP)


class Test003ProfileApplication(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.svc, self.profile = _svc(self.tmp.name)
        self.svc.create("cancion", self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_test003_ac02_applies_profile_by_genre_and_type(self):
        stem = self.svc.add_stem(_touch(self.tmp.name, "voz.wav"), StemType.VOZ).value
        self.assertEqual(stem.gain_db, 0.0)
        prof = self.profile.profile_for(Genre.POP, StemType.VOZ)
        self.assertEqual(len(prof.eq), 2)
        self.assertEqual(prof.eq[0].freq_hz, 400)
        self.assertEqual(self.profile.normalization(Genre.POP).lufs, -14.0)

    def test_test003_ac03_neutral_profile_for_otro(self):
        stem = self.svc.add_stem(_touch(self.tmp.name, "x.wav"), StemType.OTRO).value
        prof = self.profile.profile_for(Genre.POP, StemType.OTRO)
        self.assertEqual(prof.eq, [])
        self.assertIsNone(prof.compressor)
        self.assertEqual(prof.gain_base_db, 0.0)
        self.assertEqual(stem.gain_db, 0.0)


class Test003GainRange(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.svc, _ = _svc(self.tmp.name)
        self.svc.create("cancion", self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_test003_ac04_accepts_gain_in_range(self):
        stem = self.svc.add_stem(_touch(self.tmp.name, "b.wav"), StemType.BATERIA).value
        self.assertTrue(self.svc.set_gain(stem.id, -60.0).is_ok)
        self.assertEqual(stem.gain_db, -60.0)
        self.assertTrue(self.svc.set_gain(stem.id, 12.0).is_ok)
        self.assertEqual(stem.gain_db, 12.0)

    def test_test003_ac05_rejects_gain_out_of_range(self):
        stem = self.svc.add_stem(_touch(self.tmp.name, "b.wav"), StemType.BATERIA).value
        for bad in (-60.1, 12.1, -100.0, 20.0):
            res = self.svc.set_gain(stem.id, bad)
            self.assertTrue(res.is_err)
            self.assertEqual(res.error.code, "stem.gain_out_of_range")


class Test003GenreChangeAndReset(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.svc, self.profile = _svc(self.tmp.name)
        self.svc.create("cancion", self.tmp.name)
        self.voz = self.svc.add_stem(
            _touch(self.tmp.name, "voz.wav"), StemType.VOZ
        ).value
        self.bajo = self.svc.add_stem(
            _touch(self.tmp.name, "bajo.wav"), StemType.BAJO
        ).value

    def tearDown(self):
        self.tmp.cleanup()

    def test_test003_ac06_genre_change_resets_gains(self):
        # El bajo en pop tiene gain 0; en hip_hop tiene gain 2.
        self.assertEqual(self.bajo.gain_db, 0.0)
        self.bajo.corrections.tempo_ratio = 1.05  # no depende del género
        self.svc.change_genre(Genre.HIP_HOP)
        self.assertEqual(self.svc.active_project.genre, Genre.HIP_HOP)
        self.assertEqual(self.bajo.gain_db, 2.0)
        self.assertEqual(self.voz.gain_db, 0.0)
        # Las correcciones se conservan al cambiar de género.
        self.assertEqual(self.bajo.corrections.tempo_ratio, 1.05)

    def test_test003_ac07_reset_stem_returns_to_profile(self):
        # Ganancia manual + correcciones + desfase manual.
        self.svc.set_gain(self.bajo.id, -15.0)
        self.bajo.corrections.tempo_ratio = 1.1
        self.bajo.corrections.start_offset_ms = 30
        self.bajo.corrections.confidence = 0.9
        self.bajo.corrections.manual_offset_ms = 40
        self.svc.reset_stem(self.bajo.id)
        self.assertEqual(self.bajo.gain_db, 0.0)  # pop/bajo
        self.assertIsNone(self.bajo.corrections.tempo_ratio)
        self.assertIsNone(self.bajo.corrections.start_offset_ms)
        self.assertIsNone(self.bajo.corrections.confidence)
        self.assertIsNone(self.bajo.corrections.manual_offset_ms)


if __name__ == "__main__":
    unittest.main()

