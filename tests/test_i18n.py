# TEST010 — Internacionalización (SPEC010 AC-01..AC-05, decisión D6).
import os
import tempfile
import unittest

import paths  # noqa: F401

from src.repositories.settings_repository import FileSettingsRepository
from src.services.i18n_service import I18nService, _normalize, detect_system_language


def _settings(tmp_dir, language=None):
    path = os.path.join(tmp_dir, "cfg", "s.json")
    repo = FileSettingsRepository(path)
    if language is not None:
        repo.set_language(language)
    return repo


class Test010Shared(unittest.TestCase):
    def test_normalize_lc_variants(self):
        self.assertEqual(_normalize("es-ES"), "es")
        self.assertEqual(_normalize("en_US"), "en")
        self.assertEqual(_normalize("EN"), "en")
        self.assertIsNone(_normalize("fr"))
        self.assertIsNone(_normalize(""))
        self.assertIsNone(_normalize(None))


class Test010Preference(unittest.TestCase):
    def test_ac01_saved_preference_applies(self):
        # AC-01: preferencia guardada 'en' se aplica pese al sistema es.
        with tempfile.TemporaryDirectory() as td:
            repo = _settings(td)
            repo.set_language("en")
            svc = I18nService(repo, system_language="es-ES")
            self.assertEqual(svc.language, "en")


class Test010SystemLanguage(unittest.TestCase):
    def test_ac02_system_es_without_preference_uses_es(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _settings(td)
            svc = I18nService(repo, system_language="es_MX")
            self.assertEqual(svc.language, "es")

    def test_ac03_system_en_without_preference_uses_en(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _settings(td)
            svc = I18nService(repo, system_language="en-GB")
            self.assertEqual(svc.language, "en")

    def test_ac04_unsupported_system_uses_product_default_es(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _settings(td)
            svc = I18nService(repo, system_language="fr-FR")
            self.assertEqual(svc.language, "es")  # D6


class Test010ChangeAndPersist(unittest.TestCase):
    def test_ac05_change_persists_preference_and_updates_ui_language(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _settings(td)
            svc = I18nService(repo, system_language="fr-FR")
            self.assertEqual(svc.language, "es")
            # Cambiar a inglés: se aplica al instante y se persiste.
            res = svc.set_language("en")
            self.assertTrue(res.is_ok)
            self.assertEqual(svc.language, "en")
            self.assertEqual(svc.tr("ui.mix"), "Mix")
            # Persistencia: un servicio nuevo sin preferencia de sistema lee 'en'.
            svc2 = I18nService(repo, system_language="es-ES")
            self.assertEqual(svc2.language, "en")

    def test_ac05b_unsupported_change_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _settings(td)
            svc = I18nService(repo, system_language="es")
            res = svc.set_language("de")
            self.assertTrue(res.is_err)
            self.assertEqual(svc.language, "es")  # no cambia


class Test010Translation(unittest.TestCase):
    def test_spanish_and_english_texts(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _settings(td)
            svc = I18nService(repo, system_language="es")
            self.assertEqual(svc.tr("ui.preferences"), "Preferencias")
            self.assertEqual(svc.tr("ui.mix"), "Mezclar")
            svc.set_language("en")
            self.assertEqual(svc.tr("ui.preferences"), "Preferences")
            self.assertEqual(svc.tr("ui.mix"), "Mix")

    def test_missing_key_falls_back_to_default_catalog(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _settings(td)
            svc = I18nService(repo, system_language="es")
            # Clave inexistente -> clave tal cual (fallback).
            self.assertEqual(svc.tr("no.such.key"), "no.such.key")


class Test010DetectSystem(unittest.TestCase):
    def test_detect_system_language_from_env(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _settings(td)
            old = os.environ.get("LANG")
            os.environ["LANG"] = "en_US.UTF-8"
            try:
                svc = I18nService(repo, system_language=None)
                self.assertEqual(svc.language, "en")
            finally:
                if old is None:
                    os.environ.pop("LANG", None)
                else:
                    os.environ["LANG"] = old


if __name__ == "__main__":
    unittest.main()