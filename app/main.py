"""
Servicio web (Flask) que expone el modelo simulado de clasificación.

Rutas:
    GET  /          Formulario web para el médico.
    POST /          Procesa el formulario y muestra el resultado.
    POST /predecir  API REST: recibe JSON y retorna JSON con el estado.
    GET  /health    Verificación de estado del servicio.
    GET  /estadisticas  Estadísticas de las predicciones registradas.

Ejecución local (desde la carpeta 02_DOCKER_SERVICIO):
    python -m app.main
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

from app import estadisticas
from app.modelo import ESTADOS, ErrorValidacion, predecir

VERSION_MODELO = "simulado-1.0.0"


def create_app() -> Flask:
    """Fábrica de la aplicación (facilita las pruebas automáticas)."""
    app = Flask(__name__)
    app.json.ensure_ascii = False  # Respuestas JSON con tildes legibles
    # Declarar UTF-8 explícitamente para que todos los clientes (p. ej. PowerShell 5.1)
    # interpreten bien las tildes, como en "ENFERMEDAD CRÓNICA".
    app.json.mimetype = "application/json; charset=utf-8"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    def registrar_prediccion(origen: str, resultado: dict) -> None:
        """
        Registro de predicciones (etapa de monitoreo del pipeline MLOps).
        Solo se registran variables clínicas anónimas, nunca datos personales.
        """
        app.logger.info(
            "prediccion origen=%s estado=%s puntaje=%s entrada=%s",
            origen,
            resultado["estado"],
            resultado["puntaje_severidad"],
            resultado["entrada"],
        )
        # Registro persistente para las estadísticas (solo fecha y categoría).
        estadisticas.registrar_prediccion(resultado["estado"])

    # ------------------------------------------------------------------
    # Interfaz web
    # ------------------------------------------------------------------
    @app.route("/", methods=["GET", "POST"])
    def index():
        resultado = None
        errores = {}
        valores = {}
        if request.method == "POST":
            valores = request.form.to_dict()
            try:
                resultado = predecir(valores)
                registrar_prediccion("web", resultado)
            except ErrorValidacion as exc:
                errores = exc.errores
        return render_template(
            "index.html",
            resultado=resultado,
            errores=errores,
            valores=valores,
            version=VERSION_MODELO,
        ), (400 if errores else 200)

    # ------------------------------------------------------------------
    # API REST
    # ------------------------------------------------------------------
    @app.post("/predecir")
    def api_predecir():
        datos = request.get_json(silent=True)
        if datos is None:
            return jsonify(
                error="El cuerpo de la solicitud debe ser JSON válido "
                "(Content-Type: application/json)"
            ), 400
        try:
            resultado = predecir(datos)
        except ErrorValidacion as exc:
            return jsonify(error="Datos de entrada inválidos", detalles=exc.errores), 422

        registrar_prediccion("api", resultado)
        resultado["version_modelo"] = VERSION_MODELO
        resultado["fecha"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        return jsonify(resultado), 200

    @app.get("/estadisticas")
    def consultar_estadisticas():
        """Total por categoría, últimas cinco predicciones y fecha de la más reciente."""
        return jsonify(estadisticas.obtener_estadisticas()), 200

    @app.get("/health")
    def health():
        return jsonify(
            estado="ok",
            servicio="sistema-enfermedades",
            version_modelo=VERSION_MODELO,
            estados_posibles=list(ESTADOS),
        ), 200

    # Errores genéricos en formato JSON para clientes de la API
    @app.errorhandler(404)
    def no_encontrado(_):
        return jsonify(error="Ruta no encontrada"), 404

    @app.errorhandler(405)
    def metodo_no_permitido(_):
        return jsonify(error="Método HTTP no permitido para esta ruta"), 405

    return app


app = create_app()


if __name__ == "__main__":
    # 0.0.0.0 permite que el servicio sea accesible desde fuera del contenedor.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
