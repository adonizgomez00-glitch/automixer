# TEST004 — Sincronización de tempo y alineación temporal (SPEC004, decisión D2).
import os
import tempfile
import unittest

import paths  # noqa: F401

from src.adapters.fake_audio_engine import FakeAudioEngine
from src.models.project import StemType
from src.ports.audio import AlignmentAnalysis, TempoAnalysis
from src.repositories.json_project_repository import JsonProjectRepository
from src.repositories.settings_repository import FileSettingsRepository
from src.services.alignment_service import AlignmentService
from src.services.profile_service import ProfileService
from src.services.project_service import ProjectService


def _touch(tmp, rel):
    p = os.path.join(tmp, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(b"audio")
    return p


class AlignmentBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.engine = FakeAudioEngine()
        self.svc = ProjectService(
            JsonProjectRepository(),
            FileSettingsRepository(os.path.join(self.tmp.name, "cfg", "s.json")),
            profile=ProfileService(),
            engine=self.engine,
        )
        self.svc.create("cancion", self.tmp.name)
        self.asvc = AlignmentService(self.engine)

    def tearDown(self):
        self.tmp.cleanup()

    def _add(self, rel, stype):
        return self.svc.add_stem(_touch(self.tmp.name, rel), stype).value


class Test004ReferenceSelection(AlignmentBase):
    def test_test004_ac01_reference_is_bateria(self):
        self._add("bateria.wav", StemType.BATERIA)
        self._add("voz.wav", StemType.VOZ)
        ref = self.asvc.primary_reference(self.svc.active_project)
        self.assertIsNotNone(ref)
        self.assertEqual(ref.type, StemType.BATERIA)

    def test_test004_ac02_reference_is_first_valid_without_bateria(self):
        self._add("voz.wav", StemType.VOZ)
        self._add("bajo.wav", StemType.BAJO)
        ref = self.asvc.primary_reference(self.svc.active_project)
        self.assertEqual(ref.type, StemType.VOZ)

    def test_test004_ac03_tempo_correction_saved_when_reliable(self):
        bateria = self._add("bateria.wav", StemType.BATERIA)
        voz = self._add("voz.wav", StemType.VOZ)
        self.engine.set(voz.path, tempo=TempoAnalysis(ratio=1.04, confidence=0.9))
        res = self.asvc.sync_tempo(self.svc.active_project, voz)
        self.assertTrue(res.is_ok)
        self.assertEqual(voz.corrections.tempo_ratio, 1.04)
        self.assertEqual(voz.corrections.confidence, 0.9)


class Test004AlignmentStart(AlignmentBase):
    def test_test004_ac04_start_offset_saved_when_reliable(self):
        bateria = self._add("bateria.wav", StemType.BATERIA)
        voz = self._add("voz.wav", StemType.VOZ)
        self.engine.set(voz.path, alignment=AlignmentAnalysis(offset_ms=350, confidence=0.9))
        res = self.asvc.align_start(self.svc.active_project, voz)
        self.assertTrue(res.is_ok)
        self.assertEqual(voz.corrections.start_offset_ms, 350)
        self.assertEqual(voz.corrections.confidence, 0.9)


class Test004LowConfidence(AlignmentBase):
    def test_test004_ac05a_tempo_warned_and_intact_on_low_confidence(self):
        bateria = self._add("bateria.wav", StemType.BATERIA)
        voz = self._add("voz.wav", StemType.VOZ)
        self.engine.set(voz.path, tempo=TempoAnalysis(ratio=1.1, confidence=0.5))
        res = self.asvc.sync_tempo(self.svc.active_project, voz)
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "sync.low_confidence_tempo")
        self.assertIsNone(voz.corrections.tempo_ratio)
        self.assertIsNone(voz.corrections.confidence)

    def test_test004_ac05b_tempo_warned_when_ratio_out_of_range(self):
        bateria = self._add("bateria.wav", StemType.BATERIA)
        voz = self._add("voz.wav", StemType.VOZ)
        # ratio 2.0 está fuera de [0.75, 1.33] aunque confidence sea alta.
        self.engine.set(voz.path, tempo=TempoAnalysis(ratio=2.0, confidence=0.95))
        res = self.asvc.sync_tempo(self.svc.active_project, voz)
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "sync.low_confidence_tempo")

    def test_test004_ac05c_align_warned_when_offset_out_of_range(self):
        bateria = self._add("bateria.wav", StemType.BATERIA)
        voz = self._add("voz.wav", StemType.VOZ)
        self.engine.set(voz.path, alignment=AlignmentAnalysis(offset_ms=5000, confidence=0.95))
        res = self.asvc.align_start(self.svc.active_project, voz)
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "sync.low_confidence_alignment")


class Test004ReferenceChange(AlignmentBase):
    def test_test004_ac06_change_reference_preserves_manual_offset(self):
        bateria = self._add("bateria.wav", StemType.BATERIA)
        voz = self._add("voz.wav", StemType.VOZ)
        bajo = self._add("bajo.wav", StemType.BAJO)
        # voz tiene desfase manual; bajo sin él.
        voz.corrections.manual_offset_ms = 20
        res = self.asvc.set_reference(self.svc.active_project, bateria)
        self.assertTrue(res.is_ok)
        self.assertEqual(self.svc.active_project.reference_stem_id, bateria.id)
        # voz conserva su manual offset; bajo se recalcula (se limpian sus correcciones automáticas).
        self.assertEqual(voz.corrections.manual_offset_ms, 20)

    def test_test004_ac07_bateria_added_adapts_to_existing_reference(self):
        voz = self._add("voz.wav", StemType.VOZ)
        bajo = self._add("bajo.wav", StemType.BAJO)
        # Referencia fijada al primer stem (voz) antes de agregar batería.
        self.asvc.set_reference(self.svc.active_project, voz)
        self.assertEqual(self.svc.active_project.reference_stem_id, voz.id)
        bateria = self._add("bateria.wav", StemType.BATERIA)
        # La batería se adapta a la referencia existente (voz), no la reemplaza.
        self.assertEqual(self.svc.active_project.reference_stem_id, voz.id)
        ref = self.asvc.reference_for(self.svc.active_project)
        self.assertEqual(ref.id, voz.id)


class Test004Reset(AlignmentBase):
    def test_test004_ac08_reset_removes_corrections_and_manual_offset(self):
        bateria = self._add("bateria.wav", StemType.BATERIA)
        voz = self._add("voz.wav", StemType.VOZ)
        self.engine.set(voz.path, tempo=TempoAnalysis(ratio=1.1, confidence=0.9))
        self.asvc.sync_tempo(self.svc.active_project, voz)
        voz.corrections.start_offset_ms = 12
        voz.corrections.manual_offset_ms = 30
        # "Restablecer" orquestra el reset completo (ganancia + correcciones).
        res = self.svc.reset_stem(voz.id)
        self.assertTrue(res.is_ok)
        self.assertIsNone(voz.corrections.tempo_ratio)
        self.assertIsNone(voz.corrections.start_offset_ms)
        self.assertIsNone(voz.corrections.confidence)
        self.assertIsNone(voz.corrections.manual_offset_ms)


if __name__ == "__main__":
    unittest.main()


