
from __future__ import annotations
from typing import Any, Optional


class DomainError(Exception):
    """Error de dominio identificado por una clave de mensaje `msg.*`."""

    def __init__(self, code: str, params: Optional[dict[str, Any]] = None):
        self.code = code
        self.params = params or {}
        super().__init__(code)


class Result:
    """Contenedor de resultado: Ok (valor) o Error (DomainError)."""

    __slots__ = ("_ok", "_value", "_error")

    def __init__(self, ok: bool, value: Any = None, error: Optional[DomainError] = None):
        self._ok = ok
        self._value = value
        self._error = error

    @staticmethod
    def ok(value: Any = None) -> "Result":
        return Result(True, value=value)

    @staticmethod
    def err(error: DomainError) -> "Result":
        return Result(False, error=error)

    @property
    def is_ok(self) -> bool:
        return self._ok

    @property
    def is_err(self) -> bool:
        return not self._ok

    @property
    def value(self) -> Any:
        if not self._ok:
            raise ValueError("no hay valor en un Result de error")
        return self._value

    @property
    def error(self) -> DomainError:
        if self._ok:
            raise ValueError("no hay error en un Result ok")
        return self._error

    def unwrap_or(self, default: Any) -> Any:
        return self._value if self._ok else default
