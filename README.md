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

Compose es el entorno de desarrollo: ambos servicios observan los cambios en
sus carpetas de código y se recargan automáticamente. Para imágenes de
producción se usarán los Dockerfiles directamente, sin los montajes de código.

La API queda disponible en `http://localhost:8000`; la documentación
interactiva está en `http://localhost:8000/docs`.

El frontend Astro queda disponible en `http://localhost:4321`.

## Endpoints principales

| Recurso | Operaciones |
| --- | --- |
| Pacientes | `POST /pacientes`, `GET /pacientes`, `GET/PUT/DELETE /pacientes/{id}` |
| Médicos | `POST /medicos`, `GET /medicos`, `GET/PUT/DELETE /medicos/{id}` |
| Citas | `POST /citas`, `PATCH /citas/{id}/cancelacion`, `GET /medicos/{id}/citas`, `GET /pacientes/{id}/citas` |

Una segunda cita activa para el mismo médico y fecha/hora devuelve `409 Conflict`.

## Horario de atención

La clínica atiende de lunes a viernes, de 09:00 a 17:00 en la zona
`America/Merida`. Cada cita ocupa un slot de 30 minutos; por eso el último
inicio disponible es a las 16:30. Estas reglas se configuran en las variables
del servicio `api` dentro de `docker-compose.yml` y se validan en el dominio.

## Ejecutar pruebas

```bash
docker compose run --rm api python -m unittest discover -s tests
```

## Generar tipos del frontend

Para ejecutar el frontend fuera de Docker, copia `frontend/.env.example` como
`frontend/.env`. Ahí se configura tanto el proxy de desarrollo hacia el backend
como la URL para generar los tipos. Con la API levantada, genera los tipos
TypeScript desde OpenAPI:

```bash
cd frontend
OPENAPI_URL=http://localhost:8000/openapi.json npm run generate:api
```

Dentro de Docker, ambas variables apuntan automáticamente al servicio `api`.
El archivo generado se versiona y se regenera cuando cambian los esquemas de
FastAPI.
