"""
Registro y consulta de estadísticas de las predicciones.

Cada predicción exitosa se agrega como una línea a un archivo de texto:
    2026-11-16 10:30:00 | ENFERMEDAD AGUDA

Ruta del archivo: variable de entorno PREDICCIONES_FILE (por defecto,
"predicciones.txt" en el directorio de trabajo). En Docker se monta un volumen
en /servicio/data para que los datos sobrevivan al contenedor.

Nota: un archivo de texto es suficiente para este ejercicio académico con una
sola instancia del servicio. En producción se usaría una base de datos.
"""

from __future__ import annotations

import os
import threading
from collections import Counter
from datetime import datetime

from app.modelo import ESTADOS

ARCHIVO = os.getenv("PREDICCIONES_FILE", "predicciones.txt")
CATEGORIAS = list(ESTADOS)
_candado = threading.Lock()  # evita escrituras simultáneas desde varios hilos


def registrar_prediccion(resultado: str) -> None:
    """Agrega la predicción al archivo. Solo acepta una de las cinco categorías."""
    if resultado not in CATEGORIAS:
        raise ValueError(f"Categoría desconocida: {resultado!r}")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    carpeta = os.path.dirname(ARCHIVO)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with _candado, open(ARCHIVO, "a", encoding="utf-8") as f:
        f.write(f"{fecha} | {resultado}\n")


def leer_registros() -> list[dict]:
    """Lee el archivo y retorna [{"fecha": ..., "categoria": ...}, ...] en orden."""
    registros: list[dict] = []
    if not os.path.exists(ARCHIVO):
        return registros
    with open(ARCHIVO, "r", encoding="utf-8") as f:
        for linea in f:
            if "|" not in linea:
                continue
            fecha, categoria = (parte.strip() for parte in linea.split("|", 1))
            if categoria in CATEGORIAS:
                registros.append({"fecha": fecha, "categoria": categoria})
    return registros


def obtener_estadisticas() -> dict:
    """Total por categoría, últimas cinco predicciones y fecha de la más reciente."""
    registros = leer_registros()
    conteo = Counter(r["categoria"] for r in registros)
    return {
        "total_predicciones": len(registros),
        "total_por_categoria": {c: conteo.get(c, 0) for c in CATEGORIAS},
        "ultimas_5_predicciones": registros[-5:][::-1],
        "fecha_ultima_prediccion": registros[-1]["fecha"] if registros else None,
    }
