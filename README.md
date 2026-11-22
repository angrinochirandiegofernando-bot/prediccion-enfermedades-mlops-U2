# Sistema de Predicción de Enfermedades – MLOps U2

Maestría en Ingeniería de la Investigación – Universidad Icesi.

> ⚠ Prototipo académico. La predicción es **simulada** y no constituye diagnóstico ni recomendación médica.

## Problema
Se desarrolla una aplicación académica que simula la clasificación del estado de salud de un paciente a partir de
cinco variables clínicas: temperatura, intensidad del dolor, duración de los síntomas, dificultad respiratoria y fiebre.

## Propósito
Practicar control de versiones, colaboración, pruebas automatizadas, contenedorización e integración y despliegue
continuo (CI/CD) sobre el servicio construido en la Unidad 1.

## Objetivo
Recibir los datos de un paciente, generar una de cinco categorías simuladas (NO ENFERMO, ENFERMEDAD LEVE,
ENFERMEDAD AGUDA, ENFERMEDAD CRÓNICA y ENFERMEDAD TERMINAL) y consultar estadísticas de las predicciones registradas.

## Tecnologías
Python, Flask, Gunicorn, pytest, Docker, Git, GitHub, GitHub Actions y GitHub Container Registry (GHCR).

## Estructura
- `app/main.py`: aplicación web Flask (formulario y API REST).
- `app/modelo.py`: función de predicción simulada.
- `app/estadisticas.py`: registro y consulta de predicciones.
- `app/templates/` y `app/static/`: interfaz web.
- `tests/`: pruebas automatizadas.
- `Dockerfile`: construcción de la imagen.
- `requirements.txt`: dependencias.
- `.github/workflows/workflow.yaml`: automatización CI/CD.

## Ramas de trabajo
| Rama | Responsabilidad |
|---|---|
| `main` | Versión integrada y final del proyecto (protegida: solo recibe cambios por Pull Request). |
| `solucion-inicial` | Archivos de la Unidad 1 (sin el pipeline general). |
| `nueva-categoria-terminal` | Quinta categoría: ENFERMEDAD TERMINAL. |
| `estadisticas-predicciones` | Registro y consulta de estadísticas. |
| `anadir-github-actions` | Pruebas unitarias y workflow CI/CD. |

## Alcance
La predicción es simulada y tiene fines académicos. No constituye diagnóstico ni recomendación médica.

---

# Documentación técnica del servicio (Unidad 1)

## 1. Finalidad del proyecto

Este proyecto implementa el componente de **despliegue y predicción** del pipeline MLOps propuesto en la Unidad 1 (documento del pipeline general, no incluido en este repositorio). Ofrece a un médico un servicio, empaquetado como imagen Docker, en el que introduce los síntomas de un paciente y obtiene uno de cinco estados:

| Estado | Significado (simulado) |
|---|---|
| `NO ENFERMO` | Sin signos relevantes |
| `ENFERMEDAD LEVE` | Síntomas de baja intensidad |
| `ENFERMEDAD AGUDA` | Síntomas intensos y recientes |
| `ENFERMEDAD CRÓNICA` | Síntomas que persisten 30 días o más |
| `ENFERMEDAD TERMINAL` | Cuadro grave y persistente: 30 días o más, dificultad respiratoria y puntaje ≥ 6 |

## 2. Descripción general

- **Modelo simulado** (`app/modelo.py`): función `clasificar_paciente()` basada en reglas explicables. Usa 5 variables de entrada.
- **Interfaz web** (`/`): formulario responsive hecho con Flask, HTML y CSS.
- **API REST**: `POST /predecir` (JSON de entrada y de salida), `GET /estadisticas` y `GET /health`.
- **Registro de predicciones**: cada predicción se escribe en el log del contenedor, solo con variables clínicas y sin datos personales. Esto apoya la etapa de monitoreo del pipeline.

### Variables de entrada

| Campo | Tipo | Rango / valores |
|---|---|---|
| `temperatura` | decimal | 34.0 – 43.0 °C |
| `dolor` | entero | 0 – 10 |
| `duracion_dias` | entero | 0 – 365 |
| `dificultad_respiratoria` | sí/no | `true`/`false` o `"si"`/`"no"` |
| `fiebre` | sí/no | `true`/`false` o `"si"`/`"no"` |

### Lógica de clasificación

1. Se calcula un **puntaje de severidad** (0 – 9):

   | Condición | Puntos |
   |---|---|
   | Temperatura ≥ 39.0 °C o < 35.0 °C | +2 |
   | Temperatura 37.5 – 38.9 °C | +1 |
   | Dolor ≥ 7 | +2 |
   | Dolor 4 – 6 | +1 |
   | Dificultad respiratoria | +2 |
   | Fiebre reportada | +1 |
   | Síntomas de 8 a 29 días | +1 |

2. Si `duracion_dias ≥ 30`, hay dificultad respiratoria y el puntaje es ≥ 6, el estado es **ENFERMEDAD TERMINAL**.
3. Si no, cuando `duracion_dias ≥ 30` y el puntaje es ≥ 1, el estado es **ENFERMEDAD CRÓNICA**.
4. En otro caso: puntaje 0 → **NO ENFERMO**; 1 – 3 → **ENFERMEDAD LEVE**; ≥ 4 → **ENFERMEDAD AGUDA**.

## 3. Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) o Docker Engine (Linux), ya iniciado.
- Opcional, para ejecutar sin Docker o correr las pruebas localmente: Python 3.10 o superior.

## 4. Estructura de carpetas

```
prediccion-enfermedades-mlops-U2/
├── app/
│   ├── __init__.py          # Paquete de la aplicación
│   ├── main.py              # Servicio Flask: rutas web y API REST
│   ├── modelo.py            # Función de clasificación simulada y validaciones
│   ├── estadisticas.py      # Registro y consulta de estadísticas de predicciones
│   ├── templates/
│   │   └── index.html       # Interfaz web (formulario y resultado)
│   └── static/
│       └── style.css        # Estilos responsive
├── tests/
│   ├── __init__.py
│   ├── test_app.py          # Pruebas del servicio (pytest)
│   └── test_modelo.py       # Pruebas unitarias U2: cinco categorías y estadísticas
├── .github/workflows/workflow.yaml  # CI/CD con GitHub Actions
├── conftest.py              # Aísla el archivo de predicciones en las pruebas
├── .dockerignore            # Archivos excluidos de la imagen
├── Dockerfile               # Definición de la imagen Docker
├── requirements.txt         # Dependencias de Python
└── README.md                # Este documento
```

## 5. Instalar las dependencias (solo para ejecución local, sin Docker)

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

Con Docker no hace falta instalar nada: la imagen ya trae todas las dependencias.

## 6. Construir la imagen Docker

Desde la raíz del repositorio (donde está el `Dockerfile`):

```bash
docker build -t sistema-enfermedades .
```

Para verificar que la imagen existe:

```bash
docker images sistema-enfermedades
```

## 7. Ejecutar el contenedor

```bash
docker run -d -p 5000:5000 --name sistema-medico sistema-enfermedades
```

Para comprobar que está en ejecución y ver sus registros (incluye el log de predicciones):

```bash
docker ps
docker logs -f sistema-medico
```

> Si el puerto 5000 está ocupado, cambie el puerto del equipo, por ejemplo `-p 8080:5000`, y acceda por `http://localhost:8080`.

## 8. Acceder a la aplicación

Abra en el navegador: **http://localhost:5000**

## 9. Usar el formulario web

1. Ingrese la **temperatura corporal** en °C (por ejemplo, `38.5`).
2. Ajuste la **intensidad del dolor** con el deslizador (0 – 10).
3. Indique la **duración de los síntomas** en días.
4. Seleccione **Sí/No** en *Dificultad respiratoria* y *Presencia de fiebre*.
5. Pulse **Clasificar**.

A la derecha (o debajo, en el celular) aparecen el estado, una descripción breve, el puntaje de severidad simulado y los factores que influyeron. Si hay campos vacíos o fuera de rango, el formulario los marca en rojo.

## 10. Consumir la API REST

### Verificar el servicio — `GET /health`

```bash
curl http://localhost:5000/health
```

```json
{
  "estado": "ok",
  "servicio": "sistema-enfermedades",
  "version_modelo": "simulado-1.0.0",
  "estados_posibles": ["NO ENFERMO", "ENFERMEDAD LEVE", "ENFERMEDAD AGUDA", "ENFERMEDAD CRÓNICA", "ENFERMEDAD TERMINAL"]
}
```

### Clasificar — `POST /predecir`

**Linux / macOS / Git Bash:**

```bash
curl -X POST http://localhost:5000/predecir \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 39.5, "dolor": 8, "duracion_dias": 2, "dificultad_respiratoria": true, "fiebre": true}'
```

**Windows PowerShell:**

```powershell
$cuerpo = @{ temperatura = 39.5; dolor = 8; duracion_dias = 2; dificultad_respiratoria = $true; fiebre = $true } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:5000/predecir -Method Post -ContentType "application/json" -Body $cuerpo
```

**Python:**

```python
import requests
r = requests.post("http://localhost:5000/predecir", json={
    "temperatura": 39.5, "dolor": 8, "duracion_dias": 2,
    "dificultad_respiratoria": True, "fiebre": True})
print(r.json()["estado"])
```

## 11. Ejemplos de solicitudes JSON (uno por estado)

| Estado esperado | Cuerpo JSON |
|---|---|
| NO ENFERMO | `{"temperatura": 36.5, "dolor": 1, "duracion_dias": 1, "dificultad_respiratoria": false, "fiebre": false}` |
| ENFERMEDAD LEVE | `{"temperatura": 37.8, "dolor": 4, "duracion_dias": 3, "dificultad_respiratoria": false, "fiebre": true}` |
| ENFERMEDAD AGUDA | `{"temperatura": 39.5, "dolor": 8, "duracion_dias": 2, "dificultad_respiratoria": true, "fiebre": true}` |
| ENFERMEDAD CRÓNICA | `{"temperatura": 37.2, "dolor": 5, "duracion_dias": 60, "dificultad_respiratoria": false, "fiebre": false}` |
| ENFERMEDAD TERMINAL | `{"temperatura": 39.5, "dolor": 8, "duracion_dias": 60, "dificultad_respiratoria": true, "fiebre": true}` |

## 12. Ejemplos de respuestas

**Respuesta exitosa (HTTP 200):**

```json
{
  "estado": "ENFERMEDAD AGUDA",
  "descripcion": "Se observan síntomas intensos de aparición reciente. En un escenario real se sugeriría valoración prioritaria.",
  "puntaje_severidad": 7,
  "factores": ["Temperatura muy elevada (>= 39 °C)", "Dolor intenso (>= 7)", "Dificultad respiratoria", "Fiebre reportada"],
  "entrada": {"temperatura": 39.5, "dolor": 8, "duracion_dias": 2, "dificultad_respiratoria": true, "fiebre": true},
  "advertencia": "Resultado simulado con fines académicos. No constituye un diagnóstico médico.",
  "version_modelo": "simulado-1.0.0",
  "fecha": "2026-11-08T18:00:00+00:00"
}
```

**Datos inválidos (HTTP 422):**

```json
{
  "error": "Datos de entrada inválidos",
  "detalles": {"dolor": "Debe estar entre 0 y 10", "fiebre": "Campo obligatorio"}
}
```

**Cuerpo que no es JSON (HTTP 400):**

```json
{"error": "El cuerpo de la solicitud debe ser JSON válido (Content-Type: application/json)"}
```

## 13. Ejecutar las pruebas

**Dentro del contenedor** (no requiere Python en el equipo):

```bash
docker run --rm sistema-enfermedades python -m pytest -v
```

**Localmente** (con las dependencias instaladas, desde la raíz del repositorio):

```bash
python -m pytest -v
```

Las pruebas verifican que:

- la aplicación inicia y muestra el formulario;
- `/health` responde;
- `/predecir` recibe JSON y responde correctamente;
- se obtienen los cinco estados;
- los campos se validan (faltantes, fuera de rango, tipos incorrectos);
- los errores de entrada se manejan con los códigos HTTP adecuados (400, 405 y 422).

## 14. Detener y eliminar el contenedor

```bash
docker stop sistema-medico
docker rm sistema-medico
# Opcional: eliminar también la imagen
docker rmi sistema-enfermedades
```

## 15. Estadísticas de predicciones — `GET /estadisticas`

Cada predicción exitosa (formulario web o API) se guarda en un archivo de texto con la fecha y la categoría,
por ejemplo `2026-11-16 10:30:00 | ENFERMEDAD AGUDA`. Las solicitudes inválidas no se registran.
La ruta del archivo se define con la variable de entorno `PREDICCIONES_FILE`
(por defecto `predicciones.txt`; dentro del contenedor `/servicio/data/predicciones.txt`).

```bash
curl http://localhost:5000/estadisticas
```

```json
{
  "total_predicciones": 3,
  "total_por_categoria": {"NO ENFERMO": 1, "ENFERMEDAD LEVE": 0, "ENFERMEDAD AGUDA": 1,
                          "ENFERMEDAD CRÓNICA": 0, "ENFERMEDAD TERMINAL": 1},
  "ultimas_5_predicciones": [
    {"fecha": "2026-11-16 10:32:00", "categoria": "ENFERMEDAD TERMINAL"},
    {"fecha": "2026-11-16 10:31:00", "categoria": "NO ENFERMO"},
    {"fecha": "2026-11-16 10:30:00", "categoria": "ENFERMEDAD AGUDA"}
  ],
  "fecha_ultima_prediccion": "2026-11-16 10:32:00"
}
```

### Persistencia en Docker
Monte un volumen en `/servicio/data` para que el registro no se pierda al eliminar el contenedor:

```bash
docker run -d -p 5000:5000 \
  -v predicciones_data:/servicio/data \
  -e PREDICCIONES_FILE=/servicio/data/predicciones.txt \
  --name sistema-medico prediccion-enfermedades-mlops-u2
```

> Un archivo de texto es suficiente para este ejercicio (una sola instancia). En producción, con varias
> instancias o escrituras concurrentes, se usaría una base de datos.

## 16. Integración y despliegue continuo (GitHub Actions)

El workflow `.github/workflows/workflow.yaml` atiende dos eventos:

| Evento | Job | Qué hace |
|---|---|---|
| Pull Request hacia `main` | `pruebas-pull-request` | Comenta el inicio, instala dependencias, ejecuta `pytest` y comenta el éxito si todas las pruebas pasan. |
| Push a `main` (merge de un PR) | `publicar-imagen` | Ejecuta las pruebas y, si pasan, construye y publica la imagen Docker en GitHub Container Registry. |

La rama `main` está protegida: solo recibe cambios mediante Pull Request.

Pruebas unitarias principales (`tests/test_modelo.py`): obtención de las cinco categorías y registro/consulta de estadísticas.

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

Imagen publicada:

```bash
docker pull ghcr.io/angrinochirandiegofernando-bot/prediccion-enfermedades-mlops-u2:latest
docker run -d -p 5000:5000 -v predicciones_data:/servicio/data ghcr.io/angrinochirandiegofernando-bot/prediccion-enfermedades-mlops-u2:latest
```
