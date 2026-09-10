# TEST001 + TEST008 — gestión de proyecto local y persistencia `.automixer`.
import json
import os
import tempfile
import unittest

import paths  # noqa: F401

from src.models.project import Genre, SCHEMA_VERSION, Stem, StemType
from src.repositories.json_project_repository import JsonProjectRepository
from src.repositories.settings_repository import FileSettingsRepository
from src.services.project_service import ProjectService


class ProjectTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = JsonProjectRepository()
        self.settings = FileSettingsRepository(
            os.path.join(self.tmp.name, "cfg", "settings.json")
        )
        self.service = ProjectService(self.repo, self.settings)

    def tearDown(self):
        self.tmp.cleanup()

    def touch(self, rel, data=b"audio"):
        path = os.path.join(self.tmp.name, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
        return path


class TestCreate(ProjectTestCase):
    def test_creates_project_with_pop_genre(self):
        res = self.service.create("Mi cancion", self.tmp.name)
        self.assertTrue(res.is_ok)
        self.assertEqual(res.value.genre, Genre.POP)
        self.assertEqual(self.service.active_project, res.value)

    def test_rejects_empty_name(self):
        res = self.service.create("   ", self.tmp.name)
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "project.name_empty")

    def test_rejects_not_writable_folder(self):
        ro = os.path.join(self.tmp.name, "ro")
        os.makedirs(ro)
        os.chmod(ro, 0o500)
        if os.access(ro, os.W_OK):
            self.skipTest("el usuario actual puede escribir en un dir 0500")
        res = self.service.create("ok", ro)
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "project.folder_notwritable")


class TestPersistence(ProjectTestCase):
    def test_save_writes_versioned_file(self):
        self.service.create("Cancion", self.tmp.name)
        path = self.service.active_path
        res = self.service.save()
        self.assertTrue(res.is_ok)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertEqual(data["schema_version"], SCHEMA_VERSION)
        self.assertIn("stems", data)

    def test_load_reconstructs_project(self):
        self.service.create("Cancion", self.tmp.name)
        self.service.add_stem(self.touch("voz.wav"))
        self.service.save()
        path = self.service.active_path
        res = self.service.open(path)
        self.assertTrue(res.is_ok)
        self.assertEqual(res.value.name, "Cancion")
        self.assertEqual(len(res.value.stems), 1)

    def test_failed_save_preserves_previous_file(self):
        self.service.create("Cancion", self.tmp.name)
        self.service.save()
        path = self.service.active_path
        with open(path, encoding="utf-8") as _fb:
            before = _fb.read()

        ro = os.path.join(self.tmp.name, "ro2")
        os.makedirs(ro)
        os.chmod(ro, 0o500)
        new_path = os.path.join(ro, "Cancion.automixer")
        res = self.service.save_to(self.service.active_project, new_path)
        if os.access(ro, os.W_OK):
            self.skipTest("el usuario actual puede escribir en un dir 0500")
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "project.save_failed")
        # El archivo previo sigue intacto y legible.
        with open(path, encoding="utf-8") as _fa:
            after = _fa.read()
        self.assertEqual(before, after)

    def test_load_rejects_unsupported_schema(self):
        path = os.path.join(self.tmp.name, "bad.automixer")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"schema_version": 99}, fh)
        res = self.service.open(path)
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "project.schema_unsupported")

    def test_missing_stem_marked_not_available(self):
        self.service.create("Cancion", self.tmp.name)
        self.service.add_stem(self.touch("sta.wav"))
        self.service.save()
        path = self.service.active_path
        # Simular que el stem desapareció.
        os.remove(os.path.join(self.tmp.name, "sta.wav"))
        res = self.service.open(path)
        self.assertTrue(res.is_ok)
        self.assertFalse(res.value.stems[0].available)

    def test_relocate_stem_updates_path(self):
        self.service.create("Cancion", self.tmp.name)
        stem = self.service.add_stem(self.touch("a/sta.wav"))
        self.assertTrue(stem.is_ok)
        new_path = self.touch("b/sta.wav")
        res = self.service.relocate_stem(stem.value.id, new_path)
        self.assertTrue(res.is_ok)
        self.assertEqual(res.value.path, new_path)
        self.assertTrue(res.value.available)

    def test_add_stem_rejects_unsupported_extension(self):
        self.service.create("Cancion", self.tmp.name)
        res = self.service.add_stem(self.touch("x.ogg"))
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "stem.format_unsupported")


class TestPreferences(unittest.TestCase):
    def test_language_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = FileSettingsRepository(os.path.join(tmp, "s.json"))
            settings.set_language("es")
            self.assertEqual(settings.get_language(), "es")


if __name__ == "__main__":
    unittest.main()
