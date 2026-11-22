"""
Modelo SIMULADO de clasificación de estados de salud a partir de síntomas.

ADVERTENCIA: este módulo NO contiene un modelo de Machine Learning entrenado.
Implementa un conjunto de reglas determinísticas con fines exclusivamente
académicos, para ilustrar cómo se expone un "modelo" como servicio en Docker.
No debe utilizarse para diagnóstico ni para la toma de decisiones clínicas.

Variables de entrada (5):
    temperatura              float  Temperatura corporal en °C (34.0 – 43.0)
    dolor                    int    Intensidad del dolor, escala 0 – 10
    duracion_dias            int    Días desde el inicio de los síntomas (0 – 365)
    dificultad_respiratoria  bool   ¿Presenta dificultad respiratoria?
    fiebre                   bool   ¿Reporta fiebre?

Lógica de clasificación (en este orden):
    1. Se calcula un puntaje de severidad (0 – 9):
         - Temperatura >= 39.0 °C o < 35.0 °C ........ +2
         - Temperatura entre 37.5 y 38.9 °C .......... +1
         - Dolor >= 7 ................................ +2
         - Dolor entre 4 y 6 ......................... +1
         - Dificultad respiratoria ................... +2
         - Fiebre reportada .......................... +1
         - Síntomas de 8 a 29 días ................... +1
    2. Si los síntomas persisten 30 días o más, hay dificultad respiratoria
       y el puntaje es >= 6 -> ENFERMEDAD TERMINAL (cuadro grave y persistente).
    3. Si los síntomas persisten 30 días o más y el puntaje es >= 1
       -> ENFERMEDAD CRÓNICA (la persistencia domina sobre la intensidad).
    4. Si el puntaje es 0                -> NO ENFERMO
    5. Si el puntaje está entre 1 y 3    -> ENFERMEDAD LEVE
    6. Si el puntaje es 4 o más          -> ENFERMEDAD AGUDA
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Constantes del dominio
# --------------------------------------------------------------------------
NO_ENFERMO = "NO ENFERMO"
ENFERMEDAD_LEVE = "ENFERMEDAD LEVE"
ENFERMEDAD_AGUDA = "ENFERMEDAD AGUDA"
ENFERMEDAD_CRONICA = "ENFERMEDAD CRÓNICA"
ENFERMEDAD_TERMINAL = "ENFERMEDAD TERMINAL"

ESTADOS = (
    NO_ENFERMO,
    ENFERMEDAD_LEVE,
    ENFERMEDAD_AGUDA,
    ENFERMEDAD_CRONICA,
    ENFERMEDAD_TERMINAL,
)

# Descripción breve que se muestra al médico junto con el resultado.
DESCRIPCIONES = {
    NO_ENFERMO: (
        "Los valores ingresados no muestran signos relevantes de enfermedad "
        "según las reglas simuladas."
    ),
    ENFERMEDAD_LEVE: (
        "Se observan síntomas de baja intensidad. En un escenario real se "
        "sugeriría observación y control."
    ),
    ENFERMEDAD_AGUDA: (
        "Se observan síntomas intensos de aparición reciente. En un escenario "
        "real se sugeriría valoración prioritaria."
    ),
    ENFERMEDAD_CRONICA: (
        "Los síntomas persisten durante 30 días o más. En un escenario real se "
        "sugeriría seguimiento y estudio especializado."
    ),
    ENFERMEDAD_TERMINAL: (
        "Cuadro grave y persistente: síntomas de 30 días o más con dificultad "
        "respiratoria y severidad alta. En un escenario real se sugeriría "
        "atención especializada inmediata."
    ),
}

# Rangos válidos de las variables numéricas: (mínimo, máximo).
RANGOS = {
    "temperatura": (34.0, 43.0),
    "dolor": (0, 10),
    "duracion_dias": (0, 365),
}

CAMPOS_BOOLEANOS = ("dificultad_respiratoria", "fiebre")
CAMPOS_REQUERIDOS = tuple(RANGOS) + CAMPOS_BOOLEANOS

UMBRAL_CRONICO_DIAS = 30
UMBRAL_TERMINAL_PUNTAJE = 6  # Puntaje mínimo para ENFERMEDAD TERMINAL


class ErrorValidacion(ValueError):
    """Error de validación con un diccionario {campo: mensaje}."""

    def __init__(self, errores: dict[str, str]):
        super().__init__("Datos de entrada inválidos")
        self.errores = errores


# --------------------------------------------------------------------------
# Validación y conversión de datos
# --------------------------------------------------------------------------
def _a_booleano(valor) -> bool:
    """Convierte valores típicos de formularios/JSON a bool o lanza ValueError."""
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float)) and valor in (0, 1):
        return bool(valor)
    if isinstance(valor, str):
        texto = valor.strip().lower()
        if texto in ("si", "sí", "true", "1", "yes", "s"):
            return True
        if texto in ("no", "false", "0", "n"):
            return False
    raise ValueError("debe ser sí/no (true/false)")


def validar_datos(datos: dict) -> dict:
    """
    Valida y convierte los datos crudos (formulario o JSON) a tipos Python.

    Retorna un diccionario limpio o lanza ErrorValidacion con todos los
    errores encontrados (no solo el primero), para informar al usuario.
    """
    if not isinstance(datos, dict):
        raise ErrorValidacion({"general": "Se esperaba un objeto con los datos del paciente"})

    errores: dict[str, str] = {}
    limpio: dict = {}

    # Campos numéricos
    for campo, (minimo, maximo) in RANGOS.items():
        valor = datos.get(campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            errores[campo] = "Campo obligatorio"
            continue
        if isinstance(valor, bool):  # True/False no son números válidos aquí
            errores[campo] = "Debe ser un valor numérico"
            continue
        try:
            numero = float(str(valor).replace(",", "."))
        except ValueError:
            errores[campo] = "Debe ser un valor numérico"
            continue
        if numero != numero:  # NaN
            errores[campo] = "Debe ser un valor numérico"
            continue
        # Dolor y duración deben ser enteros
        if campo != "temperatura":
            if not numero.is_integer():
                errores[campo] = "Debe ser un número entero"
                continue
            numero = int(numero)
        if not (minimo <= numero <= maximo):
            errores[campo] = f"Debe estar entre {minimo} y {maximo}"
            continue
        limpio[campo] = numero

    # Campos booleanos
    for campo in CAMPOS_BOOLEANOS:
        valor = datos.get(campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            errores[campo] = "Campo obligatorio"
            continue
        try:
            limpio[campo] = _a_booleano(valor)
        except ValueError as exc:
            errores[campo] = f"Valor inválido: {exc}"

    if errores:
        raise ErrorValidacion(errores)
    return limpio


# --------------------------------------------------------------------------
# Función de clasificación (el "modelo" simulado)
# --------------------------------------------------------------------------
def calcular_puntaje(
    temperatura: float,
    dolor: int,
    duracion_dias: int,
    dificultad_respiratoria: bool,
    fiebre: bool,
) -> tuple[int, list[str]]:
    """Calcula el puntaje de severidad y la lista de factores que lo explican."""
    puntaje = 0
    factores: list[str] = []

    if temperatura >= 39.0:
        puntaje += 2
        factores.append("Temperatura muy elevada (>= 39 °C)")
    elif temperatura < 35.0:
        puntaje += 2
        factores.append("Temperatura muy baja (< 35 °C)")
    elif temperatura >= 37.5:
        puntaje += 1
        factores.append("Temperatura elevada (37.5 – 38.9 °C)")

    if dolor >= 7:
        puntaje += 2
        factores.append("Dolor intenso (>= 7)")
    elif dolor >= 4:
        puntaje += 1
        factores.append("Dolor moderado (4 – 6)")

    if dificultad_respiratoria:
        puntaje += 2
        factores.append("Dificultad respiratoria")

    if fiebre:
        puntaje += 1
        factores.append("Fiebre reportada")

    if 8 <= duracion_dias < UMBRAL_CRONICO_DIAS:
        puntaje += 1
        factores.append("Síntomas de 8 a 29 días")
    elif duracion_dias >= UMBRAL_CRONICO_DIAS:
        factores.append("Síntomas persistentes (>= 30 días)")

    return puntaje, factores


def clasificar_paciente(
    temperatura: float,
    dolor: int,
    duracion_dias: int,
    dificultad_respiratoria: bool,
    fiebre: bool,
) -> str:
    """
    Retorna uno de los cinco estados simulados:
    NO ENFERMO, ENFERMEDAD LEVE, ENFERMEDAD AGUDA, ENFERMEDAD CRÓNICA
    o ENFERMEDAD TERMINAL.
    """
    puntaje, _ = calcular_puntaje(
        temperatura, dolor, duracion_dias, dificultad_respiratoria, fiebre
    )

    # Caso más grave primero: síntomas persistentes, dificultad respiratoria y
    # severidad alta. Va antes de CRÓNICA para que esa regla, más general,
    # no capture estos casos.
    if (
        duracion_dias >= UMBRAL_CRONICO_DIAS
        and dificultad_respiratoria
        and puntaje >= UMBRAL_TERMINAL_PUNTAJE
    ):
        return ENFERMEDAD_TERMINAL
    # Luego, la persistencia de síntomas.
    if duracion_dias >= UMBRAL_CRONICO_DIAS and puntaje >= 1:
        return ENFERMEDAD_CRONICA
    if puntaje == 0:
        return NO_ENFERMO
    if puntaje <= 3:
        return ENFERMEDAD_LEVE
    return ENFERMEDAD_AGUDA


def predecir(datos: dict) -> dict:
    """
    Punto de entrada de alto nivel: valida los datos crudos, clasifica y
    retorna una respuesta completa y explicable.
    """
    v = validar_datos(datos)
    puntaje, factores = calcular_puntaje(**v)
    estado = clasificar_paciente(**v)
    return {
        "estado": estado,
        "descripcion": DESCRIPCIONES[estado],
        "puntaje_severidad": puntaje,
        "factores": factores,
        "entrada": v,
        "advertencia": (
            "Resultado simulado con fines académicos. "
            "No constituye un diagnóstico médico."
        ),
    }
