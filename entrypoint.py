from __future__ import annotations

"""Punto de entrada del ejecutable empaquetado (PyInstaller).

Importa `src.app` como módulo (con su paquete padre) para que funcionen los
imports relativos; así el entrypoint puede ser compilado de forma aislada.
"""

from src.app import main

if __name__ == "__main__":
    raise SystemExit(main())