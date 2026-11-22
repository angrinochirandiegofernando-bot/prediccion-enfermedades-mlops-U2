"""Configuración común de pytest.

Redirige el archivo de predicciones a una carpeta temporal en cada prueba,
para no modificar los datos reales y que cada prueba empiece sin registros.
"""

import pytest

from app import estadisticas


@pytest.fixture(autouse=True)
def archivo_predicciones_temporal(tmp_path, monkeypatch):
    monkeypatch.setattr(estadisticas, "ARCHIVO", str(tmp_path / "predicciones.txt"))
