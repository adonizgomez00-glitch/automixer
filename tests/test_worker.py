# TEST009 — trabajos cancelables, progreso y un trabajo a la vez.
import threading
import time
import unittest

import paths  # noqa: F401

from src.utils.result import DomainError
from src.workers.cancelable import AudioWorkerManager, Cancelled, CancelToken


def _long_work(token: CancelToken, progress):
    for i in range(100):
        progress(i)
        time.sleep(0.01)
        token.raise_if_cancelled()
    return "done"


class TestWorker(unittest.TestCase):
    def test_reports_progress(self):
        m = AudioWorkerManager()
        seen = []
        res = m.run_sync(_long_work, on_progress := (lambda p: seen.append(p)))
        self.assertTrue(res.is_ok)
        self.assertEqual(res.value, "done")
        self.assertTrue(len(seen) > 0)
        self.assertEqual(seen[-1], 99)

    def test_internal_cancel_yields_cancelled(self):
        m = AudioWorkerManager()

        def work(token, progress):
            raise Cancelled()

        res = m.run_sync(work)
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "job.cancelled")

    def test_maps_domain_error(self):
        m = AudioWorkerManager()

        def work(token, progress):
            raise DomainError("export.failed")

        res = m.run_sync(work)
        self.assertTrue(res.is_err)
        self.assertEqual(res.error.code, "export.failed")

    def test_one_job_at_a_time_and_external_cancel(self):
        m = AudioWorkerManager()
        done = threading.Event()
        results = []

        def on_done(result):
            results.append(result)
            done.set()

        ok = m.start(_long_work, on_done=on_done)
        self.assertTrue(ok)
        self.assertTrue(m.active)
        # Un segundo trabajo se rechaza.
        self.assertFalse(m.start(_long_work))
        # Cancelamos desde fuera.
        m.cancel()
        self.assertTrue(done.wait(timeout=5))
        self.assertEqual(results[0].error.code, "job.cancelled")
        self.assertFalse(m.active)

    def test_not_active_accepts_job(self):
        m = AudioWorkerManager()
        self.assertFalse(m.active)
        self.assertTrue(m.start(_long_work, on_done=lambda r: None))
        time.sleep(0.1)
        m.cancel()


if __name__ == "__main__":
    unittest.main()
