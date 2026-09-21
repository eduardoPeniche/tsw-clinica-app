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
