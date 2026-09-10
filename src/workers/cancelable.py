from __future__ import annotations
import threading
from typing import Callable, Optional

from ..utils.result import DomainError, Result


class Cancelled(Exception):
    """Se lanza dentro del trabajo cuando la cancelación fue solicitada."""


class CancelToken:
    """Señal thread-safe de cancelación compartida con un trabajo."""

    def __init__(self) -> None:
        self._cancel = threading.Event()

    def cancel(self) -> None:
        self._cancel.set()

    @property
    def cancelled(self) -> bool:
        return self._cancel.is_set()

    def raise_if_cancelled(self) -> None:
        if self.cancelled:
            raise Cancelled()


# Callback de progreso (porcentaje entero 0-100).
ProgressCallback = Callable[[int], None]
# Trabajo: recibe el token de cancelación y un callback de progreso.
WorkFn = Callable[[CancelToken, ProgressCallback], object]


class AudioWorkerManager:
    """Gestiona un único trabajo de audio a la vez (SPEC009).

    - `run_sync`: ejecuta el trabajo en el hilo actual (determinista, tests).
    - `start`: ejecuta en un hilo en segundo plano y enruta callbacks.
    - `cancel`: solicita la cancelación del trabajo activo.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active = False
        self._token: Optional[CancelToken] = None

    @property
    def active(self) -> bool:
        with self._lock:
            return self._active

    def run_sync(self, work: WorkFn, progress_cb: Optional[ProgressCallback] = None) -> Result:
        with self._lock:
            if self._active:
                return Result.err(DomainError("busy.job_active"))
            self._active = True
            self._token = CancelToken()
            token = self._token
        try:
            value = work(token, progress_cb or (lambda p: None))
            return Result.ok(value)
        except Cancelled:
            return Result.err(DomainError("job.cancelled"))
        except DomainError as exc:
            return Result.err(exc)
        except Exception as exc:  # noqa: BLE001 - fallo externo -> error de dominio
            return Result.err(DomainError("job.failed", {"detail": str(exc)}))
        finally:
            with self._lock:
                self._active = False
                self._token = None

    def start(
        self,
        work: WorkFn,
        on_progress: Optional[ProgressCallback] = None,
        on_done: Optional[Callable[[Result], None]] = None,
    ) -> bool:
        """Inicia el trabajo en un hilo. Devuelve False si ya hay uno activo."""
        with self._lock:
            if self._active:
                return False
            self._active = True
            self._token = CancelToken()
            token = self._token
        progress = on_progress or (lambda p: None)

        def _runner() -> None:
            try:
                value = work(token, progress)
                result: Result = Result.ok(value)
            except Cancelled:
                result = Result.err(DomainError("job.cancelled"))
            except DomainError as exc:
                result = Result.err(exc)
            except Exception as exc:  # noqa: BLE001
                result = Result.err(DomainError("job.failed", {"detail": str(exc)}))
            finally:
                with self._lock:
                    self._active = False
                    self._token = None
            if on_done is not None:
                on_done(result)

        threading.Thread(target=_runner, daemon=True).start()
        return True

    def cancel(self) -> None:
        with self._lock:
            token = self._token
        if token is not None:
            token.cancel()
