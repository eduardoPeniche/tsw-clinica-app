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

El frontend Astro queda disponible en `http://localhost:4321` por defecto. Si
alguno de los puertos del equipo está ocupado, copia `.env.example` como `.env`
y cambia `BACKEND_PORT` o `FRONTEND_PORT`. Los servicios conservan sus puertos
internos (`8000` y `4321`), por lo que su comunicación dentro de Docker no
cambia. También se pueden definir solo para una ejecución:

```bash
BACKEND_PORT=8001 FRONTEND_PORT=4322 docker compose up --build
```

Con ese ejemplo, Swagger quedará en `http://localhost:8001/docs` y el frontend
en `http://localhost:4322`.

## Ejecutar pruebas

```bash
docker compose run --rm backend python -m unittest discover -s tests
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

Si se configuró un `BACKEND_PORT` distinto para Docker, usa ese mismo puerto en
`frontend/.env` o en `OPENAPI_URL`.

Dentro de Docker, ambas variables apuntan automáticamente al servicio `backend`.
El archivo generado se versiona y se regenera cuando cambian los esquemas de
FastAPI.
