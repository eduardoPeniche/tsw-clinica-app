# Sistema de gestión de citas médicas

## Estructura

```text
backend/   API FastAPI, SQLite, pruebas y dependencias Python
frontend/  Interfaz web Astro
```

## Ejecutar con Docker

La aplicación se ejecuta desde un contenedor; no es necesario instalar las
dependencias de Python en el equipo local.

```bash
docker compose up --build
```

La API queda disponible en `http://localhost:8000`; la documentación
interactiva está en `http://localhost:8000/docs`.

## Endpoints principales

| Recurso | Operaciones |
| --- | --- |
| Pacientes | `POST /pacientes`, `GET /pacientes`, `GET/PUT/DELETE /pacientes/{id}` |
| Médicos | `POST /medicos`, `GET /medicos`, `GET/PUT/DELETE /medicos/{id}` |
| Citas | `POST /citas`, `PATCH /citas/{id}/cancelacion`, `GET /medicos/{id}/citas`, `GET /pacientes/{id}/citas` |

Una segunda cita activa para el mismo médico y fecha/hora devuelve `409 Conflict`.

## Ejecutar pruebas

```bash
docker compose run --rm api python -m unittest discover -s tests
```
