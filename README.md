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
