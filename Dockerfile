# ------------------------------------------------------------------
# Imagen del Sistema de Clasificación de Síntomas (prototipo académico)
#
# Construcción:  docker build -t sistema-enfermedades .
# Ejecución:     docker run -d -p 5000:5000 --name sistema-medico sistema-enfermedades
# Acceso:        http://localhost:5000
# ------------------------------------------------------------------

# Imagen base ligera con Python 3.12
FROM python:3.12-slim

# Variables de entorno: sin archivos .pyc, salida de logs sin búfer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=5000

# Directorio de trabajo dentro del contenedor
WORKDIR /servicio

# 1) Instalar dependencias primero (aprovecha la caché de capas de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copiar el código fuente y las pruebas
COPY app/ ./app/
COPY tests/ ./tests/

# 3) Ejecutar como usuario sin privilegios (buena práctica de seguridad)
RUN useradd --create-home --uid 1000 medico \
    && chown -R medico:medico /servicio
USER medico

# Puerto en el que escucha el servicio
EXPOSE 5000

# Verificación periódica del estado del servicio usando el endpoint /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/health').status == 200 else 1)"

# Gunicorn escucha en 0.0.0.0 para ser accesible desde fuera del contenedor
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app.main:app"]
