"""
Pruebas unitarias de la Unidad 2 (se ejecutan automáticamente en GitHub Actions).

Ejecución local, desde la raíz del repositorio:
    python -m pytest -v
"""

from app import estadisticas
from app.modelo import clasificar_paciente


def test_se_pueden_obtener_las_cinco_categorias():
    # (temperatura, dolor, duracion_dias, dificultad_respiratoria, fiebre)
    casos = [
        (36.5, 1, 1, False, False),   # puntaje 0                         -> NO ENFERMO
        (37.8, 4, 3, False, True),    # puntaje 3                         -> ENFERMEDAD LEVE
        (39.5, 8, 2, True, True),     # puntaje 7, síntomas recientes     -> ENFERMEDAD AGUDA
        (37.2, 5, 60, False, False),  # 60 días, puntaje 1                -> ENFERMEDAD CRÓNICA
        (39.5, 8, 60, True, True),    # 60 días, resp., puntaje 7         -> ENFERMEDAD TERMINAL
    ]
    resultados = [clasificar_paciente(*caso) for caso in casos]

    assert resultados == [
        "NO ENFERMO",
        "ENFERMEDAD LEVE",
        "ENFERMEDAD AGUDA",
        "ENFERMEDAD CRÓNICA",
        "ENFERMEDAD TERMINAL",
    ]
    assert len(set(resultados)) == 5


def test_registro_y_consulta_de_estadisticas(tmp_path, monkeypatch):
    archivo = tmp_path / "predicciones.txt"
    monkeypatch.setattr(estadisticas, "ARCHIVO", str(archivo))

    inicial = estadisticas.obtener_estadisticas()
    assert inicial["fecha_ultima_prediccion"] is None
    assert inicial["ultimas_5_predicciones"] == []
    assert sum(inicial["total_por_categoria"].values()) == 0

    estadisticas.registrar_prediccion("ENFERMEDAD TERMINAL")
    datos = estadisticas.obtener_estadisticas()

    assert archivo.exists()
    assert datos["total_por_categoria"]["ENFERMEDAD TERMINAL"] == 1
    assert datos["ultimas_5_predicciones"][0]["categoria"] == "ENFERMEDAD TERMINAL"
    assert datos["fecha_ultima_prediccion"] is not None
