# TEST002 — Importación y clasificación manual de stems (SPEC002).
import os
import tempfile
import unittest

import paths  # noqa: F401

from src.adapters.fake_audio_engine import FakeAudioEngine
from src.models.project import StemType
from src.repositories.json_project_repository import JsonProjectRepository
from src.repositories.settings_repository import FileSettingsRepository
from src.services.profile_service import ProfileService
from src.services.project_service import ProjectService


class StemsTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = JsonProjectRepository()
        self.settings = FileSettingsRepository(
            os.path.join(self.tmp.name, "cfg", "settings.json")
        )
        self.engine = FakeAudioEngine()
        self.profile = ProfileService()
        self.service = ProjectService(
            self.repo, self.settings, profile=self.profile, engine=self.engine
        )
        self.service.create("cancion", self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def touch(self, rel):
        p = os.path.join(self.tmp.name, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(b"audio")
        return p

    def test_test002_ac01_imports_valid_stem(self):
        res = self.service.add_stem(self.touch("voz.wav"), StemType.VOZ)
        self.assertTrue(res.is_ok)
        stem = res.value
        self.assertTrue(stem.available)
        self.assertEqual(stem.type, StemType.VOZ)
        self.assertEqual(self.service.active_project.stems[0], stem)

    def test_test002_ac02_rejects_unsupported_extension(self):
        res = self.service.add_stem(self.touch("x.ogg"))
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "stem.format_unsupported")
        self.assertEqual(len(self.service.active_project.stems), 0)

    def test_test002_ac03_rejects_undecodable_file(self):
        path = self.touch("broken.wav")
        self.engine.set(path, decodable=False)
        res = self.service.add_stem(path)
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "stem.decode_failed")
        self.assertEqual(len(self.service.active_project.stems), 0)

    def test_test002_ac04_assigns_manual_type_and_allows_duplicates(self):
        voz = self.service.add_stem(self.touch("v1.wav")).value
        voz2 = self.service.add_stem(self.touch("v2.wav")).value
        res = self.service.set_stem_type(voz.id, StemType.VOZ)
        self.assertTrue(res.is_ok)
        self.assertEqual(res.value.type, StemType.VOZ)
        res2 = self.service.set_stem_type(voz2.id, StemType.VOZ)
        self.assertTrue(res2.is_ok)
        self.assertEqual(voz.gain_db, 0.0)

    def test_test002_ac05_mix_enabled_with_one_valid_stem(self):
        self.service.add_stem(self.touch("bateria.wav"), StemType.BATERIA)
        self.assertTrue(self.service.mix_enabled)

    def test_test002_ac06_mix_disabled_with_no_valid_stems(self):
        self.assertFalse(self.service.active_project.stems)
        self.assertFalse(self.service.mix_enabled)


if __name__ == "__main__":
    unittest.main()
