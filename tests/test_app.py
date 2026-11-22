"""
Pruebas automáticas del servicio de clasificación simulada.

Ejecución (desde la carpeta 02_DOCKER_SERVICIO):
    python -m pytest -v
"""

import os
import sys

import pytest

# Permite importar el paquete "app" sin importar desde dónde se ejecute pytest.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import create_app  # noqa: E402
from app.modelo import (  # noqa: E402
    ENFERMEDAD_AGUDA,
    ENFERMEDAD_CRONICA,
    ENFERMEDAD_LEVE,
    ESTADOS,
    NO_ENFERMO,
    ErrorValidacion,
    clasificar_paciente,
    validar_datos,
)

# Casos representativos que producen cada uno de los cuatro estados.
CASOS = {
    NO_ENFERMO: dict(temperatura=36.5, dolor=1, duracion_dias=1,
                     dificultad_respiratoria=False, fiebre=False),
    ENFERMEDAD_LEVE: dict(temperatura=37.8, dolor=4, duracion_dias=3,
                          dificultad_respiratoria=False, fiebre=True),
    ENFERMEDAD_AGUDA: dict(temperatura=39.5, dolor=8, duracion_dias=2,
                           dificultad_respiratoria=True, fiebre=True),
    ENFERMEDAD_CRONICA: dict(temperatura=37.2, dolor=5, duracion_dias=60,
                             dificultad_respiratoria=False, fiebre=False),
}


@pytest.fixture
def cliente():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


# ----------------------------------------------------------------------
# Función de clasificación
# ----------------------------------------------------------------------
@pytest.mark.parametrize("esperado,datos", CASOS.items())
def test_funcion_retorna_cada_estado(esperado, datos):
    assert clasificar_paciente(**datos) == esperado


def test_los_cuatro_estados_son_alcanzables():
    obtenidos = {clasificar_paciente(**d) for d in CASOS.values()}
    assert obtenidos == set(ESTADOS)


def test_la_funcion_usa_las_variables():
    """Cambiar una sola variable modifica el resultado."""
    base = dict(CASOS[NO_ENFERMO])
    assert clasificar_paciente(**base) == NO_ENFERMO
    assert clasificar_paciente(**{**base, "dificultad_respiratoria": True}) == ENFERMEDAD_LEVE
    assert clasificar_paciente(**{**base, "temperatura": 39.6, "dolor": 9}) == ENFERMEDAD_AGUDA
    assert clasificar_paciente(**{**base, "duracion_dias": 45, "fiebre": True}) == ENFERMEDAD_CRONICA


def test_validacion_convierte_tipos_de_formulario():
    limpio = validar_datos({"temperatura": "38,2", "dolor": "6", "duracion_dias": "4",
                            "dificultad_respiratoria": "si", "fiebre": "no"})
    assert limpio == {"temperatura": 38.2, "dolor": 6, "duracion_dias": 4,
                      "dificultad_respiratoria": True, "fiebre": False}


def test_validacion_reporta_todos_los_errores():
    with pytest.raises(ErrorValidacion) as exc:
        validar_datos({"temperatura": "50", "dolor": "abc", "duracion_dias": "2.5",
                       "dificultad_respiratoria": "tal vez"})
    assert set(exc.value.errores) == {"temperatura", "dolor", "duracion_dias",
                                      "dificultad_respiratoria", "fiebre"}


# ----------------------------------------------------------------------
# Aplicación y endpoints
# ----------------------------------------------------------------------
def test_aplicacion_inicia_y_muestra_formulario(cliente):
    r = cliente.get("/")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "Sistema de Clasificación de Síntomas" in html
    assert "no reemplaza la valoración de un profesional de salud" in html


def test_health(cliente):
    r = cliente.get("/health")
    assert r.status_code == 200
    assert r.get_json()["estado"] == "ok"


@pytest.mark.parametrize("esperado,datos", CASOS.items())
def test_api_predecir_cuatro_estados(cliente, esperado, datos):
    r = cliente.post("/predecir", json=datos)
    assert r.status_code == 200
    cuerpo = r.get_json()
    assert cuerpo["estado"] == esperado
    assert "descripcion" in cuerpo and "advertencia" in cuerpo


def test_api_acepta_valores_como_texto(cliente):
    r = cliente.post("/predecir", json={"temperatura": "39.5", "dolor": "8", "duracion_dias": "2",
                                        "dificultad_respiratoria": "si", "fiebre": "si"})
    assert r.status_code == 200
    assert r.get_json()["estado"] == ENFERMEDAD_AGUDA


def test_api_campos_faltantes(cliente):
    r = cliente.post("/predecir", json={"temperatura": 37})
    assert r.status_code == 422
    detalles = r.get_json()["detalles"]
    assert detalles["dolor"] == "Campo obligatorio"
    assert "fiebre" in detalles


@pytest.mark.parametrize("campo,valor", [
    ("temperatura", 20), ("temperatura", "abc"), ("dolor", 11), ("dolor", -1),
    ("dolor", 3.5), ("duracion_dias", -2), ("fiebre", "quizas"), ("temperatura", True),
])
def test_api_valores_invalidos(cliente, campo, valor):
    datos = {**CASOS[NO_ENFERMO], campo: valor}
    r = cliente.post("/predecir", json=datos)
    assert r.status_code == 422
    assert campo in r.get_json()["detalles"]


def test_api_json_malformado(cliente):
    r = cliente.post("/predecir", data="{no es json", content_type="application/json")
    assert r.status_code == 400


def test_api_sin_json(cliente):
    r = cliente.post("/predecir", data="temperatura=37")
    assert r.status_code == 400


def test_api_metodo_no_permitido(cliente):
    assert cliente.get("/predecir").status_code == 405


def test_formulario_web_clasifica(cliente):
    r = cliente.post("/", data={"temperatura": "37.2", "dolor": "5", "duracion_dias": "60",
                                "dificultad_respiratoria": "no", "fiebre": "no"})
    assert r.status_code == 200
    assert ENFERMEDAD_CRONICA in r.get_data(as_text=True)


def test_formulario_web_campos_vacios(cliente):
    r = cliente.post("/", data={"temperatura": "", "dolor": "3"})
    assert r.status_code == 400
    assert "Campo obligatorio" in r.get_data(as_text=True)
