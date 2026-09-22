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

## MCP por stdio

El adaptador MCP es opcional: no inicia con `docker compose up` ni publica un
puerto. Un host MCP local debe iniciarlo como proceso hijo mediante:

```bash
docker compose --profile mcp run --rm -T mcp
```

Mientras la sesión del agente esté abierta, ese proceso reutiliza los casos de
uso existentes para administrar pacientes, médicos y citas. Comparte el volumen
SQLite con el backend, pero no expone SQL ni rutas HTTP como herramientas.

### Configuración compartida para agentes

El repositorio incluye un lanzador portable en `scripts/run-mcp`, que encuentra
la raíz del proyecto y crea un contenedor MCP temporal. No depende de la ruta
donde cada integrante haya clonado el repositorio.

- Codex carga `.codex/config.toml` al abrir un proyecto confiable. Las
  herramientas de consulta son de solo lectura; las que modifican datos
  requieren aprobación.
- Claude Code carga `.mcp.json` y solicita aprobar el servidor de proyecto la
  primera vez.
- Grok Build carga `.grok/config.toml`. También reconoce `.mcp.json` por
  compatibilidad, pero la configuración nativa tiene prioridad.

En ambos casos, abre el agente desde la raíz del repositorio con Docker u
OrbStack en ejecución. El agente inicia una sola instancia MCP durante la
sesión; no se crea un contenedor por cada herramienta utilizada.

Para un host que no reconozca esos archivos, ejecuta manualmente:

```bash
sh ./scripts/run-mcp
```
